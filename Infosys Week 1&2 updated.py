# ============================================================
# MODULE 1: PAPER SEARCH (NON-INTERACTIVE)
# ============================================================

import os
import json
import logging
import time
import hashlib
import requests
import fitz  # PyMuPDF
import pandas as pd

from tqdm import tqdm
from typing import List, Dict
from datetime import datetime
from dotenv import load_dotenv
from semanticscholar import SemanticScholar

# ------------------------------------------------------------
# FOLDER SETUP
# ------------------------------------------------------------
os.makedirs("logs", exist_ok=True)
os.makedirs("data/search_results", exist_ok=True)
os.makedirs("downloads/pdfs", exist_ok=True)
os.makedirs("downloads/metadata", exist_ok=True)
os.makedirs("data/dataset", exist_ok=True)

# ------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------
logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------------------------------------------------------------
# GLOBAL CONFIG (NO USER INPUT)
# ------------------------------------------------------------

SEARCH_CONFIG = {
    "topic": "machine learning in healthcare",
    "limit": 25,
    "year_min": 2019,
    "min_citations": 20
}

SELECTION_CONFIG = {
    "mode": "rule",       # only manual rule-based
    "top_n": 5,
    "min_year": 2020,
    "min_citations": 100
}

# ============================================================
# MODULE 1 FUNCTIONS
# ============================================================

def setup_api_key():
    load_dotenv()
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        print("Semantic Scholar initialized with API key")
        return SemanticScholar(api_key=api_key)
    else:
        print("Semantic Scholar initialized without API key (rate-limited)")
        return SemanticScholar()

def search_papers(config: Dict) -> Dict:
    sch = setup_api_key()
    print(f"\n🔍 Searching papers for topic: {config['topic']}")

    results = sch.search_paper(
        query=config["topic"],
        limit=config["limit"],
        fields=[
            "paperId", "title", "abstract", "year",
            "authors", "citationCount", "openAccessPdf",
            "url", "venue"
        ]
    )

    papers = []
    for paper in tqdm(results, desc="Processing papers"):
        if config["year_min"] and paper.year and paper.year < config["year_min"]:
            continue
        if config["min_citations"] and paper.citationCount < config["min_citations"]:
            continue

        papers.append({
            "title": paper.title,
            "authors": [a["name"] for a in paper.authors] if paper.authors else [],
            "year": paper.year,
            "paperId": paper.paperId,
            "abstract": paper.abstract,
            "citationCount": paper.citationCount,
            "venue": paper.venue,
            "url": paper.url,
            "pdf_url": paper.openAccessPdf["url"] if paper.openAccessPdf else None
        })

    data = {
        "topic": config["topic"],
        "timestamp": datetime.now().isoformat(),
        "total_results": len(papers),
        "papers": papers
    }

    path = f"data/search_results/{config['topic'].replace(' ', '_')}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Search results saved to {path}")
    return data, path

# ============================================================
# MODULE 2 FUNCTIONS
# ============================================================

def display_all_papers(papers: List[Dict], max_show: int = 50):
    print("\n" + "=" * 100)
    print("📄 ALL AVAILABLE PAPERS (FROM SEARCH RESULTS)")
    print("=" * 100)

    for i, p in enumerate(papers[:max_show], start=1):
        print(
            f"{i}. {p['title'][:60]} | "
            f"Year: {p.get('year')} | "
            f"Citations: {p.get('citationCount')} | "
            f"PDF: {'Yes' if p.get('pdf_url') else 'No'}"
        )

    print(f"\nTotal papers retrieved: {len(papers)}")

def compute_paper_score(paper: Dict) -> float:
    citations = paper.get("citationCount") or 0
    year = paper.get("year")
    current_year = datetime.now().year

    if isinstance(year, int):
        recency_penalty = max(0, current_year - year)
    else:
        recency_penalty = 10  # missing year treated as old

    score = (0.7 * citations) + (0.3 * max(0, 10 - recency_penalty))
    return round(score, 2)

def rank_papers(papers: List[Dict]) -> List[Dict]:
    for p in papers:
        p["ranking_score"] = compute_paper_score(p)

    ranked = sorted(papers, key=lambda x: x["ranking_score"], reverse=True)

    print("\n📊 RANKING JUSTIFICATION (Top 10)")
    print("-" * 100)
    for i, p in enumerate(ranked[:10], start=1):
        print(
            f"{i}. {p['title'][:55]} | "
            f"Year={p.get('year')} | "
            f"Citations={p.get('citationCount')} | "
            f"Score={p['ranking_score']}"
        )

    return ranked

def select_papers_manual(papers: List[Dict], config: Dict) -> List[Dict]:
    ranked = rank_papers(papers)

    selected = [
        p for p in ranked
        if (p.get("year") or 0) >= config["min_year"]
        and (p.get("citationCount") or 0) >= config["min_citations"]
    ][:config["top_n"]]

    print("\n📌 MANUALLY SELECTED PAPERS (RULE-BASED)")
    print("-" * 100)
    for i, p in enumerate(selected, start=1):
        print(
            f"{i}. {p['title'][:55]} | "
            f"Year={p.get('year')} | "
            f"Citations={p.get('citationCount')} | "
            f"Score={p['ranking_score']}"
        )

    return selected

def safe_filename(s: str, max_len=80) -> str:
    return "".join(c for c in s if c.isalnum() or c in " -_")[:max_len]

def sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def download_pdf(paper: Dict):
    if not paper.get("pdf_url"):
        return None

    filename = safe_filename(paper["title"]) + ".pdf"
    path = os.path.join("downloads/pdfs", filename)

    try:
        r = requests.get(paper["pdf_url"], stream=True, timeout=30)
        if r.status_code != 200:
            return None

        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

        with fitz.open(path) as doc:
            pages = len(doc)

        return {
            "local_path": path,
            "pages": pages,
            "size_mb": round(os.path.getsize(path) / (1024 * 1024), 2),
            "sha256": sha256_of_file(path)
        }

    except Exception:
        if os.path.exists(path):
            os.remove(path)
        return None

# ============================================================
# MAIN PIPELINE
# ============================================================

def main():
    # MODULE 1
    search_data, search_path = search_papers(SEARCH_CONFIG)

    # MODULE 2
    display_all_papers(search_data["papers"])
    selected = select_papers_manual(search_data["papers"], SELECTION_CONFIG)

    downloaded = []
    for p in selected:
        print(f"\n⬇ Downloading: {p['title'][:80]}")
        pdf_info = download_pdf(p)
        if pdf_info:
            p["pdf_info"] = pdf_info
            p["downloaded"] = True
        else:
            p["downloaded"] = False
        downloaded.append(p)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = f"data/dataset/papers_{timestamp}.csv"
    df = pd.DataFrame(downloaded)
    df.to_csv(csv_path, index=False)

    print(f"\n✅ Dataset created: {csv_path}")
    print("🎉 Pipeline completed successfully!")

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()

