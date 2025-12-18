# ============================================================
# MODULE 3: PDF TEXT EXTRACTION + ANALYSIS (FINAL FIXED)
# ============================================================

import json
import re
import logging
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

import fitz  
import pymupdf4llm
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# LOGGING
# ============================================================
Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    filename="logs/module3.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ============================================================
# CONFIG
# ============================================================
PDF_DIR = Path("downloads/pdfs")
OUTPUT_DIR = Path("data/extracted")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. TEXT CLEANING
# ============================================================
def clean_text_basic(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'page\s+\d+', '', text, flags=re.I)
    text = re.sub(r'(figure|table)\s+\d+', '', text, flags=re.I)
    text = re.sub(r'-\s+', '', text)
    text = ''.join(c for c in text if ord(c) >= 32)
    return text.strip()


# ============================================================
# 2. TEXT EXTRACTION
# ============================================================
def extract_text_improved(pdf_path: Path):
    try:
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            return None

        first_page = doc[0].get_text().lower()
        if any(k in first_page for k in ["copyright", "permission", "takedown"]):
            return None

        texts = []

        # Layout-aware extraction
        try:
            md_text = pymupdf4llm.to_markdown(str(pdf_path))
            if md_text and len(md_text) > 1000:
                texts.append(md_text)
        except Exception:
            pass

        # Standard extraction
        full_text = ""
        for page in doc[:50]:
            full_text += page.get_text() + "\n"

        if len(full_text) > 1000:
            texts.append(full_text)

        doc.close()
        return max(texts, key=len) if texts else None

    except Exception as e:
        logging.error(f"Extraction failed: {pdf_path.name} | {e}")
        return None


# ============================================================
# 3. SECTION EXTRACTION
# ============================================================
def extract_sections_improved(text: str):
    sections = {
        "title": "",
        "abstract": "",
        "introduction": "",
        "methods": "",
        "results": "",
        "conclusion": "",
        "references": "",
        "full_text": text[:20000]
    }

    if not text or len(text) < 500:
        return sections

    text = clean_text_basic(text)
    lines = text.split("\n")

    patterns = {
        "abstract": ["abstract", "summary"],
        "introduction": ["introduction", "background"],
        "methods": ["method", "methodology", "experiment"],
        "results": ["results", "findings"],
        "conclusion": ["conclusion", "discussion"],
        "references": ["references", "bibliography"]
    }

    boundaries = {}

    for i, line in enumerate(lines):
        l = line.lower().strip()

        if len(l) > 200:
            continue

        for sec, keys in patterns.items():
            for k in keys:
                
                if re.match(rf"^(\d+\.?|[ivx]+\.)?\s*{k}", l):
                    boundaries.setdefault(sec, i)

    ordered = sorted(boundaries.items(), key=lambda x: x[1])

    for idx, (sec, start) in enumerate(ordered):
        end = ordered[idx + 1][1] if idx + 1 < len(ordered) else len(lines)
        content = "\n".join(lines[start + 1:end]).strip()
        if len(content) > 200:
            sections[sec] = content[:5000]

   
    if not sections["abstract"]:
        lower = text.lower()
        if "abstract" in lower:
            s = lower.find("abstract")
            e = lower.find("introduction", s + 8)
            sections["abstract"] = text[s:e if e != -1 else s + 2500].strip()

    # Title extraction
    for line in lines[:10]:
        if 20 < len(line.strip()) < 200:
            sections["title"] = line.strip()
            break

    return sections


# ============================================================
# 4. KEY-FINDING EXTRACTION
# ============================================================
def extract_key_findings(text, top_k=10):
    if not text or len(text) < 300:
        return []

    try:
        vec = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=top_k
        )
        tfidf = vec.fit_transform([text])
        return vec.get_feature_names_out().tolist()
    except Exception:
        return []


# ============================================================
# 5. VALIDATION
# ============================================================
def validate_extraction(paper):
    checks = {
        "has_abstract": bool(paper["sections"].get("abstract")),
        "has_methods": bool(paper["sections"].get("methods")),
        "has_results": bool(paper["sections"].get("results")),
        "sufficient_length": paper["total_characters"] > 3000
    }

    paper["validation"] = {
        "passed": all(checks.values()),
        "checks": checks
    }
    return paper


# ============================================================
# 6. PROCESS SINGLE PAPER 
# ============================================================
def process_paper(pdf_path: Path):
    print(f"\nProcessing: {pdf_path.name}")

    if pdf_path.stat().st_size < 10_000:
        print(" File too small, skipping")
        return None

    raw = extract_text_improved(pdf_path)
    if not raw:
        print(" Extraction failed or restricted")
        return None

    sections = extract_sections_improved(raw)

    analysis_text = (
        sections.get("abstract", "") +
        sections.get("introduction", "") +
        sections.get("results", "")
    )

    paper = {
        "paper_id": pdf_path.stem,
        "filename": pdf_path.name,
        "total_characters": len(raw),
        "sections": sections,
        "key_findings": extract_key_findings(analysis_text)
    }

    paper = validate_extraction(paper)

    meaningful = [
        k for k, v in sections.items()
        if k not in ["full_text"] and v and len(v) > 200
    ]

    # ---- VISIBLE ENHANCEMENTS ----
    print(f" Extracted {paper['total_characters']:,} characters")
    print(f" Sections found: {meaningful}")
    print(f" Key findings: {paper['key_findings'][:6]}")
    print(f" Validation: {paper['validation']['checks']}")

    return paper


# ============================================================
# 7. CROSS-PAPER COMPARISON
# ============================================================
def keyword_overlap(k1, k2):
    s1, s2 = set(k1), set(k2)
    return round(len(s1 & s2) / len(s1 | s2), 3) if s1 and s2 else 0.0


def cross_paper_comparison(papers):
    abstracts = [
        p["sections"]["abstract"]
        for p in papers
        if p["sections"].get("abstract") and len(p["sections"]["abstract"]) > 200
    ]

    if len(abstracts) < 2:
        print(" Not enough valid abstracts for similarity analysis.")
        return pd.DataFrame()

    vec = TfidfVectorizer(stop_words="english")
    tfidf = vec.fit_transform(abstracts)
    sim = cosine_similarity(tfidf)

    rows = []
    for i in range(len(papers)):
        for j in range(i + 1, len(papers)):
            rows.append({
                "paper_1": papers[i]["paper_id"],
                "paper_2": papers[j]["paper_id"],
                "cosine_similarity": round(sim[i][j], 3),
                "keyword_overlap": keyword_overlap(
                    papers[i]["key_findings"],
                    papers[j]["key_findings"]
                )
            })

    return pd.DataFrame(rows)


# ============================================================
# 8. SAVE OUTPUTS
# ============================================================
def save_outputs(papers, comparison_df):
    for p in papers:
        with open(OUTPUT_DIR / f"{p['paper_id']}_extracted.json", "w", encoding="utf-8") as f:
            json.dump(p, f, indent=2, ensure_ascii=False)

    pd.DataFrame([
        {
            "paper_id": p["paper_id"],
            "title": p["sections"].get("title", ""),
            "key_findings": ", ".join(p["key_findings"]),
            "validation_passed": p["validation"]["passed"]
        }
        for p in papers
    ]).to_csv(OUTPUT_DIR / "extracted_papers.csv", index=False)

    if not comparison_df.empty:
        comparison_df.to_csv(OUTPUT_DIR / "cross_paper_similarity.csv", index=False)

    with open(OUTPUT_DIR / "extraction_summary.json", "w") as f:
        json.dump({
            "date": datetime.now().isoformat(),
            "total_papers": len(papers)
        }, f, indent=2)


# ============================================================
# 9. MAIN RUNNER
# ============================================================
def extract_all_papers(max_papers=5):
    print("\n" + "=" * 80)
    print("MODULE 3: PDF TEXT EXTRACTION + ANALYSIS")
    print("=" * 80)

    pdfs = list(PDF_DIR.glob("*.pdf"))[:max_papers]
    results = []

    for pdf in tqdm(pdfs, desc="Extracting PDFs"):
        paper = process_paper(pdf)
        if paper:
            results.append(paper)

    comparison_df = cross_paper_comparison(results)
    save_outputs(results, comparison_df)

    print(f"\n Completed: {len(results)} papers processed")


if __name__ == "__main__":
    extract_all_papers()
