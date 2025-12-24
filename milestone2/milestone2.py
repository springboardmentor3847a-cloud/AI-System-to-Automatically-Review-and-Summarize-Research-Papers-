import os
import re
import json
import csv
import logging
from collections import Counter
from itertools import combinations

import pdfplumber
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# ================== PATHS ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PDF_DIR = os.path.join(BASE_DIR, "..", "milestone-1", "data", "pdfs")
TEXT_DIR = os.path.join(BASE_DIR, "extracted_text")
COMPARE_DIR = os.path.join(BASE_DIR, "comparisons")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(TEXT_DIR, exist_ok=True)
os.makedirs(COMPARE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

print(f"[INFO] Looking for PDFs in: {os.path.abspath(PDF_DIR)}")

# ================== LOGGING ==================
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "extraction.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ================== TEXT CLEANING ==================
def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"-\n", "", text)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    return text.strip()

# ================== PDF TEXT EXTRACTION ==================
def extract_full_text(pdf_path):
    try:
        full_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[:40]:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
        return clean_text(full_text)
    except Exception as e:
        logging.error(f"Failed to extract text from {pdf_path}: {e}")
        return ""

# ================== SECTION DETECTION ==================
SECTION_PATTERNS = {
    "abstract": r"\babstract\b",
    "introduction": r"\bintroduction\b",
    "methodology": r"\b(methodology|methods)\b",
    "results": r"\b(results|experiments|evaluation)\b",
    "conclusion": r"\b(conclusion|discussion)\b"
}

def extract_sections(text):
    sections = {key: "" for key in SECTION_PATTERNS}
    lowered = text.lower()
    indices = {}

    for section, pattern in SECTION_PATTERNS.items():
        match = re.search(pattern, lowered)
        if match:
            indices[section] = match.start()

    sorted_sections = sorted(indices.items(), key=lambda x: x[1])

    for i, (section, start) in enumerate(sorted_sections):
        end = sorted_sections[i + 1][1] if i + 1 < len(sorted_sections) else len(text)
        sections[section] = text[start:end].strip()

    return sections

# ================== KEYWORD EXTRACTION ==================
def extract_keywords(text, top_n=15):
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    words = [w for w in words if w not in ENGLISH_STOP_WORDS]
    return [word for word, _ in Counter(words).most_common(top_n)]

# ================== KEY FINDINGS ==================
FINDING_PATTERNS = [
    r"we found .*?\.",
    r"results show .*?\.",
    r"our results .*?\.",
    r"significant .*?\."
]

def extract_key_findings(text, max_findings=3):
    findings = []
    for pattern in FINDING_PATTERNS:
        findings.extend(re.findall(pattern, text.lower()))
    return findings[:max_findings]

# ================== PROCESS SINGLE PAPER ==================
def process_pdf(pdf_file, index, total):
    pdf_path = os.path.join(PDF_DIR, pdf_file)

    print(f"\n[{index}/{total}] 📄 Processing: {pdf_file}")
    logging.info(f"Starting extraction for {pdf_file}")

    full_text = extract_full_text(pdf_path)

    if not full_text:
        print("   ❌ Text extraction failed")
        logging.warning(f"No text extracted from {pdf_file}")
        return None

    sections = extract_sections(full_text)
    keywords = extract_keywords(full_text)
    key_findings = extract_key_findings(full_text)

    print("   ✔ Text extracted successfully")
    print(f"   ✔ Sections identified: {', '.join([k.capitalize() for k,v in sections.items() if v])}")
    print(f"   ✔ Keywords extracted: {len(keywords)}")
    print(f"   ✔ Key findings extracted: {len(key_findings)}")

    words = re.findall(r"\b[a-zA-Z]{3,}\b", full_text.lower())

    return {
        "paper": pdf_file,
        "sections": sections,
        "keywords": keywords,
        "key_findings": key_findings,
        "stats": {
            "total_words": len(words),
            "unique_words": len(set(words))
        }
    }

# ================== SAVE STRUCTURED OUTPUT ==================
def save_extraction(data):
    output_path = os.path.join(TEXT_DIR, data["paper"].replace(".pdf", ".json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print("   ✔ Structured JSON saved")
    logging.info(f"Saved structured output for {data['paper']}")

# ================== CROSS-PAPER COMPARISON ==================
def compare_keywords(all_data):
    print("\n📊 Cross-Paper Analysis:")
    rows = []

    for a, b in combinations(all_data, 2):
        overlap = set(a["keywords"]) & set(b["keywords"])
        rows.append({
            "paper_1": a["paper"],
            "paper_2": b["paper"],
            "common_keywords": ", ".join(overlap),
            "overlap_count": len(overlap)
        })

    output_file = os.path.join(COMPARE_DIR, "keyword_overlap.csv")
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["paper_1", "paper_2", "common_keywords", "overlap_count"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print("   ✔ Keyword overlap comparison generated")
    logging.info("Keyword overlap comparison completed")

def save_paper_summary(all_data):
    output_file = os.path.join(COMPARE_DIR, "paper_summary.csv")

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["paper", "total_words", "unique_words"]
        )
        writer.writeheader()

        for data in all_data:
            writer.writerow({
                "paper": data["paper"],
                "total_words": data["stats"]["total_words"],
                "unique_words": data["stats"]["unique_words"]
            })

    print("   ✔ Paper summary CSV generated")
    logging.info("Paper summary CSV generated")

# ================== MAIN ==================
def main():
    print("\n==============================")
    print(" MILESTONE 2 PIPELINE STARTED ")
    print("==============================\n")

    logging.info("Milestone 2 execution started")

    if not os.path.exists(PDF_DIR):
        print("❌ PDF directory not found.")
        return

    pdf_files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")]
    print(f"📄 PDFs Found: {len(pdf_files)}")

    if not pdf_files:
        print("⚠️ No PDF files found.")
        return

    all_results = []

    for idx, pdf in enumerate(pdf_files, start=1):
        data = process_pdf(pdf, idx, len(pdf_files))
        if data:
            save_extraction(data)
            all_results.append(data)

    if len(all_results) >= 2:
        compare_keywords(all_results)

    save_paper_summary(all_results)

    print("\n==============================")
    print(" MILESTONE 2 COMPLETED ")
    print("==============================")
    print(f"✅ Papers Processed Successfully: {len(all_results)}")
    print(f"📁 Structured Output Directory: {TEXT_DIR}")
    print(f"📊 Comparison Files Directory: {COMPARE_DIR}")
    print(f"📝 Logs Saved To: {LOG_DIR}")

    logging.info("Milestone 2 execution completed successfully")

if __name__ == "__main__":
    main()
