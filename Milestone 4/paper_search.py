import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()

class PaperSearcher:
    def __init__(self):
        self.api_key = os.getenv("SEMANTIC_SCHOLAR_KEY")
        self.pdf_dir = "pdfs"
        os.makedirs(self.pdf_dir, exist_ok=True)
        self.base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

    def search_and_download(self, topic, target_count=3):
        print(f"🔎 Searching for '{topic}' (Target: {target_count} PDFs)...")
        
        headers = {"User-Agent": "ResearchAI/1.0"}
        if self.api_key: headers["x-api-key"] = self.api_key

        # Fetch more candidates (20) to ensure we find 3 valid PDFs
        params = {
            "query": topic,
            "limit": 20, 
            "fields": "title,year,authors,openAccessPdf,citationCount,abstract"
        }

        results_data = []

        try:
            response = requests.get(self.base_url, params=params, headers=headers, timeout=30)
            if response.status_code != 200:
                print(f"❌ API Error: {response.status_code}")
                return []

            data = response.json()
            papers = data.get("data", [])

            for p in papers:
                # Stop if we hit the target
                if len(results_data) >= target_count: 
                    break
                
                # Check for PDF Link
                pdf_info = p.get("openAccessPdf")
                if not pdf_info or not pdf_info.get("url"): 
                    continue

                # Prepare Metadata
                meta = {
                    "title": p.get("title", "Unknown"),
                    "year": p.get("year", "N/A"),
                    "authors": ", ".join([a["name"] for a in p.get("authors", [])[:3]]), # Top 3 authors
                    "citations": p.get("citationCount", 0),
                    "url": pdf_info["url"]
                }

                # Download
                path = self._download_pdf(meta["url"], meta["title"])
                if path:
                    meta["path"] = path
                    results_data.append(meta)

        except Exception as e:
            print(f"❌ Search Error: {e}")

        print(f"✅ Successfully downloaded {len(results_data)} papers.")
        return results_data

    def _download_pdf(self, url, title):
        safe_title = re.sub(r"[^\w\-]", "_", title)[:50]
        path = os.path.join(self.pdf_dir, f"{safe_title}.pdf")
        
        if os.path.exists(path): return path

        print(f"   ⬇️ Downloading: {title[:30]}...")
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            r = requests.get(url, headers=headers, timeout=15, stream=True)
            
            # Validate PDF Content
            if "application/pdf" not in r.headers.get("Content-Type", "").lower():
                return None
            
            with open(path, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            return path
        except:
            return None