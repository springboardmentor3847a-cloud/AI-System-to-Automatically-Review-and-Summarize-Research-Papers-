import os
import requests
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import re

# -------------------------
# NLTK Setup
# -------------------------
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

STOPWORDS = set(stopwords.words("english"))

# -------------------------
# Load API Key
# -------------------------
load_dotenv()
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
HEADERS = {"x-api-key": API_KEY} if API_KEY else {}
SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

os.makedirs("pdfs", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# ============================================================
# SEARCH PAPERS
# ============================================================
def search_papers(topic, limit):
    print(f"\nSearching {limit} papers for topic ➤ {topic}")
    params = {
        "query": topic,
        "limit": limit,
        "fields": "title,authors,year,abstract,openAccessPdf,url"
    }
    try:
        response = requests.get(SEARCH_URL, headers=HEADERS, params=params, timeout=20)
        if response.status_code == 429:
            print("⚠️ Rate limit exceeded. Try again later or use an API key.")
            return []
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"❌ Error fetching papers: {e}")
        return []

# ============================================================
# PDF DOWNLOAD
# ============================================================
def download_pdf(paper, output_dir="pdfs"):
    pdf_info = paper.get("openAccessPdf")
    if not pdf_info or not pdf_info.get("url"):
        return None
    pdf_url = pdf_info["url"]
    filename = re.sub(r"[^A-Za-z0-9]+", "_", paper["title"])[:50] + ".pdf"
    filepath = os.path.join(output_dir, filename)
    try:
        r = requests.get(pdf_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        if r.status_code != 200:
            return None
        if "application/pdf" not in r.headers.get("Content-Type", ""):
            return None
        with open(filepath, "wb") as f:
            f.write(r.content)
        return filepath
    except:
        return None

# ============================================================
# SUMMARY GENERATION
# ============================================================
def generate_summary(text, max_sents=3):
    if not text:
        return "No abstract available."
    sentences = sent_tokenize(text)
    return " ".join(sentences[:max_sents]) if len(sentences) > max_sents else text

# ============================================================
# KEYWORD EXTRACTION
# ============================================================
def extract_keywords(text, top_n=8):
    if not text:
        return []
    words = [
        w.lower() for w in word_tokenize(text)
        if w.isalpha() and w.lower() not in STOPWORDS
    ]
    freq = Counter(words)
    return [w for w, _ in freq.most_common(top_n)]

# ============================================================
# SAVE REPORT
# ============================================================
def save_report(paper, pdf_path, summary, keywords):
    fname = re.sub(r"[^A-Za-z0-9]+", "_", paper["title"])[:50] + ".txt"
    report_path = os.path.join("reports", fname)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"TITLE: {paper['title']}\n")
        f.write(f"YEAR: {paper['year']}\n")
        f.write("AUTHORS: " + ", ".join(a["name"] for a in paper["authors"]) + "\n\n")
        f.write("ABSTRACT:\n" + (paper.get("abstract") or "No abstract available") + "\n\n")
        f.write("SUMMARY:\n" + summary + "\n\n")
        f.write("KEYWORDS:\n" + ", ".join(keywords) + "\n\n")
        f.write("PDF PATH:\n" + (pdf_path or "PDF not available") + "\n")
    return report_path

# ============================================================
# SAVE DATASET
# ============================================================
def save_dataset(papers, filename="papers_dataset.csv"):
    rows = []
    for p in papers:
        rows.append({
            "Title": p["title"],
            "Year": p["year"],
            "Authors": ", ".join(a["name"] for a in p["authors"]),
            "Abstract": p.get("abstract"),
            "PDF Path": p.get("pdf_path"),
            "Summary": p.get("summary"),
            "Keywords": ", ".join(p.get("keywords", []))
        })
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    print(f"\n📁 Dataset saved → {filename}")

# ============================================================
# INITIAL TOPIC + LIMIT BEFORE MENU
# ============================================================
print("\n============================")
print("  MILESTONE 1 – RESEARCH TOOL")
print("============================\n")

topic = input("Enter research topic: ").strip()
if topic == "":
    topic = "Machine Learning"
print(f"🔎 Topic Selected: {topic}")

try:
    limit = int(input("How many papers to fetch? (Default = 10): ").strip() or 10)
except:
    limit = 10

if API_KEY:
    print("\n🔐 Using Semantic Scholar API key\n")
else:
    print("\n⚠️ No API key found — using public mode (limited requests)\n")

papers = []

# ============================================================
# MENU SYSTEM
# ============================================================
def menu():
    global papers, topic, limit
    while True:
        print("\n=== MENU ===")
        print("1. Search Papers")
        print("2. Download PDFs")
        print("3. Generate Summaries")
        print("4. Extract Keywords")
        print("5. Save Dataset (CSV)")
        print("6. Generate Reports")
        print("7. View Top Papers")
        print("8. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            new_topic = input(f"Enter topic to search (Press Enter to use '{topic}'): ").strip()
            if new_topic:
                topic = new_topic
            new_limit = input(f"Enter number of papers (Press Enter to use {limit}): ").strip()
            if new_limit.isdigit():
                limit = int(new_limit)
            papers = search_papers(topic, limit)
            print(f"\n📘 Found {len(papers)} papers.\n")
            for i, p in enumerate(papers, start=1):
                print(f"{i}. {p['title']}")
                print(f"   Year: {p['year']}")
                print(f"   Authors: {', '.join(a['name'] for a in p['authors'][:3])}")
                print(f"   PDF Available: {'Yes' if p.get('openAccessPdf') else 'No'}\n")

        elif choice == "2":
            if not papers:
                print("Please search papers first (Option 1).")
                continue
            print("\nDownloading PDFs...")
            for p in tqdm(papers):
                p["pdf_path"] = download_pdf(p)
            print("📥 PDF download complete.")

        elif choice == "3":
            if not papers:
                print("Search papers first (Option 1).")
                continue
            print("\n📝 Summaries:\n")
            for p in papers:
                p["summary"] = generate_summary(p.get("abstract", ""))
                print(f"Title: {p['title']}")
                print(f"Summary: {p['summary']}")
                print("-" * 60)

        elif choice == "4":
            if not papers:
                print("Search papers first (Option 1).")
                continue
            corpus = " ".join([(p.get("abstract") or "") for p in papers])
            keywords = extract_keywords(corpus)
            for p in papers:
                p["keywords"] = keywords
            print("\n🔑 Extracted Keywords:")
            print(", ".join(keywords))

        elif choice == "5":
            if not papers:
                print("Search papers first.")
                continue
            save_dataset(papers)

        elif choice == "6":
            if not papers:
                print("Search papers first.")
                continue
            for p in papers:
                save_report(p, p.get("pdf_path"), p.get("summary", ""), p.get("keywords", []))
            print("📁 Reports saved in /reports folder.")

        elif choice == "7":
            if not papers:
                print("No papers found.")
                continue
            print("\n📘 Top Papers:")
            for i, p in enumerate(papers[:5], start=1):
                print(f"{i}. {p['title']} ({p['year']})")

        elif choice == "8":
            print("\nExiting program...")
            break

        else:
            print("Invalid choice. Try again.")

# ============================================================
# RUN MENU
# ============================================================
if __name__ == "__main__":
    menu()
