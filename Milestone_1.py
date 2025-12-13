import os
import json
import requests
import pandas as pd
from datetime import datetime
from semanticscholar import SemanticScholar
from dotenv import load_dotenv


# 1. Initialize Semantic Scholar
def initialize_scholar():
    load_dotenv()
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    
    if api_key:
        sch = SemanticScholar(api_key=api_key)
        print("Semantic Scholar initialized with API key")
    else:
        sch = SemanticScholar()
        print("No API key found. Using limited access mode.")
    return sch

# 2. Search papers

def search_papers(topic, max_results=10):
    print(f"\nSearching papers for topic: {topic}")
    sch = initialize_scholar()
    
    try:
        results = sch.search_paper(
            query=topic,
            limit=max_results,
            fields=["paperId", "title", "authors", "year", "abstract",
                    "citationCount", "openAccessPdf", "url", "venue"]
        )
        
        papers_list = []
        for paper in results:
            papers_list.append({
                "title": paper.title,
                "authors": [a['name'] for a in paper.authors] if paper.authors else [],
                "year": paper.year,
                "abstract": (paper.abstract[:250] + "...") if paper.abstract else "No abstract",
                "citations": paper.citationCount,
                "venue": getattr(paper, 'venue', 'Unknown'),
                "url": paper.url,
                "pdf_available": bool(paper.openAccessPdf),
                "pdf_url": paper.openAccessPdf['url'] if paper.openAccessPdf else None
            })
        return papers_list
    
    except Exception as e:
        print(f"Error: {e}")
        return []

# 3. Display papers for selection

def display_papers(papers):
    print("\nAvailable Papers (up to 10 shown):\n")
    for i, paper in enumerate(papers[:10], 1):
        print(f"{i}. {paper['title'][:80]}{'...' if len(paper['title'])>80 else ''}")
        print(f"   Authors: {', '.join(paper['authors'][:3])}" + ("..." if len(paper['authors'])>3 else ""))
        print(f"   Year: {paper['year']} | Citations: {paper['citations']} | PDF: {'Yes' if paper['pdf_url'] else 'No'}")
        print("-"*80)


# 4. Select papers to download (only valid PDFs)

def select_papers(papers, max_download=3):
    # Only papers with valid PDF URLs
    pdf_papers = [p for p in papers if p['pdf_available'] and p['pdf_url']]
    if not pdf_papers:
        print("No papers with valid PDFs available.")
        return []

    display_papers(pdf_papers)
    print(f"\nSelect up to {max_download} papers to download (enter numbers separated by commas):")
    choices = input("Your choice: ").split(",")

    selected = []
    for c in choices:
        try:
            idx = int(c.strip()) - 1
            if 0 <= idx < len(pdf_papers):
                selected.append(pdf_papers[idx])
            if len(selected) >= max_download:
                break
        except:
            continue

    if not selected:
        # Auto-select first available PDFs if user enters nothing
        selected = pdf_papers[:max_download]

    print(f"\nSelected {len(selected)} paper(s) for download.")
    return selected

# 5. Download PDFs

def download_pdfs(selected_papers):
    pdf_folder = "search_results/pdfs"
    os.makedirs(pdf_folder, exist_ok=True)
    
    for paper in selected_papers:
        try:
            response = requests.get(paper['pdf_url'], timeout=20)
            if response.status_code == 200:
                safe_title = "".join(c if c.isalnum() else "_" for c in paper['title'])[:50]
                pdf_path = os.path.join(pdf_folder, f"{safe_title}.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(response.content)
                paper['pdf_path'] = pdf_path
                print(f"PDF downloaded: {safe_title}.pdf")
            else:
                print(f"Failed to download PDF: {paper['title']}")
        except Exception as e:
            print(f"Error downloading {paper['title']}: {e}")

# 6. Save metadata & CSV dataset

def save_metadata_csv(papers, topic):
    os.makedirs("search_results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f"search_results/{topic.replace(' ', '_')}_{timestamp}.json"
    csv_file = f"search_results/{topic.replace(' ', '_')}_{timestamp}.csv"
    
    # Save JSON
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=4, ensure_ascii=False)
    
    # Save CSV
    dataset = []
    for p in papers:
        dataset.append({
            "title": p['title'],
            "authors": ", ".join(p['authors']),
            "year": p['year'],
            "citations": p['citations'],
            "venue": p['venue'],
            "abstract": p['abstract'],
            "pdf_path": p.get('pdf_path', "")
        })
    df = pd.DataFrame(dataset)
    df.to_csv(csv_file, index=False)
    
    print(f"Metadata saved to JSON: {json_file}")
    print(f"Dataset saved to CSV: {csv_file}")

# 7. Run the module

def run_module():
    topic = input("Enter research topic: ").strip()
    if not topic:
        topic = "Machine Learning"
    
    papers = search_papers(topic, max_results=10)
    if not papers:
        print("No papers found!")
        return
    
    selected_papers = select_papers(papers, max_download=3)
    download_pdfs(selected_papers)
    save_metadata_csv(papers, topic)
    print("\nModule completed successfully!")

# Run directly
if __name__ == "__main__":
    run_module()
