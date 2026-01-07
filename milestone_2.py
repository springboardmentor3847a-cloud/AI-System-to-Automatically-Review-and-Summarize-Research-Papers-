
# Milestone 2: TEXT EXTRACTION, SECTION PARSING & ANALYSIS

import os
import json
import pdfplumber
import nltk
import re
import logging
import pandas as pd
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime

# ----------------------------
# Logging setup
# ----------------------------
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename="logs/module2.log",
                    level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# ----------------------------
# NLTK setup
# ----------------------------
for pkg in ["punkt", "stopwords"]:
    try:
        nltk.data.find(pkg)
    except LookupError:
        nltk.download(pkg)

STOPWORDS = set(stopwords.words("english"))

# ----------------------------
# Folders
# ----------------------------
PDF_FOLDER = "search_results/pdfs"
EXTRACTED_FOLDER = "search_results/extracted_text"
KEYWORD_FOLDER = "search_results/keyword_analysis"
os.makedirs(EXTRACTED_FOLDER, exist_ok=True)
os.makedirs(KEYWORD_FOLDER, exist_ok=True)

# ----------------------------
# 1. Clean text
# ----------------------------
def clean_text(text):
    # Remove multiple spaces and newlines
    text = text.replace("\r", "\n")
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ----------------------------
# 2. Extract text from PDF
# ----------------------------
def extract_text_from_pdf(pdf_path):
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        full_text = clean_text(full_text)
    except Exception as e:
        logging.error(f"Failed to read {pdf_path}: {e}")
    return full_text

# ----------------------------
# 3. Section extraction (enhanced)
# ----------------------------
def extract_sections(text):
    sections = {
        "abstract": "",
        "introduction": "",
        "methods": "",
        "results": "",
        "conclusion": ""
    }

    section_patterns = {
        "abstract": r"(abstract)",
        "introduction": r"(introduction)",
        "methods": r"(method|methodology|approach)",
        "results": r"(result|discussion|findings)",
        "conclusion": r"(conclusion|future work)"
    }

    lower_text = text.lower()
    for section, pattern in section_patterns.items():
        match = re.search(pattern, lower_text)
        if match:
            start = match.start()
            sections[section] = text[start:start + 3000]  # 3000 chars approx
    return sections

# ----------------------------
# 4. Keyword extraction
# ----------------------------
def extract_keywords(text, top_n=15):
    tokens = word_tokenize(text.lower())
    words = [w for w in tokens if w.isalpha() and w not in STOPWORDS and len(w) > 3]
    freq = Counter(words)
    return [word for word, _ in freq.most_common(top_n)]

# ----------------------------
# 5. Validate text
# ----------------------------
def validate_text(text):
    return {
        "word_count": len(text.split()),
        "is_empty": len(text.strip()) == 0
    }

# ----------------------------
# 6. Process PDFs
# ----------------------------
def process_pdfs():
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
    if not pdf_files:
        logging.warning("No PDFs found.")
        print("No PDFs found. Run Module 1 first.")
        return

    all_keywords = []
    results = []

    for pdf in pdf_files:
        pdf_path = os.path.join(PDF_FOLDER, pdf)
        logging.info(f"Processing: {pdf}")
        print(f"\nProcessing: {pdf}")

        text = extract_text_from_pdf(pdf_path)
        if not text:
            logging.warning(f"No text extracted from {pdf}")
            print("No text extracted.")
            continue

        sections = extract_sections(text)
        keywords = extract_keywords(text)
        validation = validate_text(text)
        all_keywords.extend(keywords)

        paper_data = {
            "file_name": pdf,
            "validation": validation,
            "keywords": keywords,
            "sections": sections
        }
        results.append(paper_data)

        # Save per-paper JSON
        output_file = os.path.join(EXTRACTED_FOLDER, f"{pdf.replace('.pdf','')}_sections.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(paper_data, f, indent=4)
        logging.info(f"Saved extracted sections for {pdf}")

    # ----------------------------
    # Cross-paper keyword comparison
    # ----------------------------
    combined_counter = Counter(all_keywords)
    common_keywords = [k for k, v in combined_counter.items() if v > 1]

    # Save cross-paper keywords
    cross_file = os.path.join(KEYWORD_FOLDER, "common_keywords.json")
    with open(cross_file, "w", encoding="utf-8") as f:
        json.dump(common_keywords, f, indent=4)

    logging.info("Saved cross-paper keyword comparison")
    print("\nCross-paper keyword comparison saved.")
    print("Top keywords:", common_keywords[:10])

    # ----------------------------
    # Optional CSV dataset for analysis
    # ----------------------------
    csv_file = os.path.join(EXTRACTED_FOLDER, f"dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    df = pd.DataFrame([
        {
            "file_name": p["file_name"],
            "word_count": p["validation"]["word_count"],
            "keywords": ", ".join(p["keywords"]),
            "abstract": p["sections"]["abstract"][:200],  # first 200 chars
        } for p in results
    ])
    df.to_csv(csv_file, index=False)
    logging.info(f"CSV dataset saved at {csv_file}")
    print(f"CSV dataset saved at: {csv_file}")

    print("\nMilestone 2 completed successfully!")

# ----------------------------
# Run milestone
# ----------------------------
if __name__ == "__main__":
    process_pdfs()
