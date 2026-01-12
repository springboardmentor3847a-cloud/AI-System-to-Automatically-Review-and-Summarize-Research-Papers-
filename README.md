# AI System to Automatically Review and Summarize Research Papers

A production-ready system that automatically searches, downloads, analyzes, and writes a concise literature review from open-access research papers. It features a modern academic UI, robust PDF handling, and natural, low-AI-detection writing with APA 7th edition references.

## ✅ Final Project Highlights
- **Modern UI**: Clean, academic Gradio v6 interface in `ui/app_modern.py`
- **Open-Access First**: Multi-strategy search prefers arXiv and other open hosts
- **Reliable Downloads**: Smart host filtering, HTML sniffing, and retries
- **3-Paper Guarantee**: Ensures at least 3 PDFs are downloaded and analyzed
- **Structured Analysis**: Text extraction, statistics, and cross-paper comparisons
- **Natural Writing**: Varied sentence structures for less AI-detection
- **APA 7 References**: Proper authors, year, venue, and DOI links
- **Server PDF Export**: Presentation-ready PDF output

---

## 📁 Folder Structure
```
ai_paper_review/
├── modules/
│   ├── search_papers.py       # Paper search + ranking (Semantic Scholar)
│   ├── download_pdf.py        # Robust PDF downloads with validation
│   ├── extract_text.py        # PDF → text via PyMuPDF
│   ├── analyze_text.py        # Text stats + synthesis
│   ├── generate_draft.py      # Abstract/Intro/Methods/Results/Conclusion/References
│   ├── critique_draft.py      # Heuristic critique of drafts
│   ├── security.py            # Validation + basic safety checks
│   └── workflow.py            # Workflow orchestration
│
├── scripts/
│   ├── check_imports.py       # Dependency checker
│   └── quick_check.py         # Lightweight pipeline check
│
├── data/
│   ├── pdfs/                  # Downloaded PDFs
│   ├── extracted/             # Extracted text files
│   ├── metadata/              # JSON metadata (selected, analyzed, drafts, critiques)
│   └── logs/                  # Application logs
│
├── ui/
│   └── app_modern.py          # Modern academic UI (primary entry)
│
├── tests/
│   └── test_all.py            # Comprehensive tests
│
├── .env.example               # Environment variables template
├── .env                       # Your environment (optional)
├── requirements.txt           # Dependencies
├── MILESTONE3_SUMMARY.md      # Final milestone summary
└── README.md                  # This file (updated)
```

---

## 🚀 Quick Start (Windows)

### Step 1: Create Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Configure `.env` (optional)
```powershell
Copy-Item .env.example .env
# Edit .env and add keys if available
# SEMANTIC_SCHOLAR_API_KEY=your_key
```

### Step 3: Launch the Modern UI
```powershell
cd ai_paper_review
python ui/app_modern.py
```

Open the URL shown (e.g., http://127.0.0.1:7860), enter your topic and keywords, and generate the literature review. The system will:
- Search 10–50 papers (open-access prioritized)
- Download and analyze 3 best PDFs
- Write a review (Abstract, Introduction, Methodology, Results, Conclusion)
- Format APA 7 references with DOI links
- Allow PDF export of the review

---

## 🔍 How It Works (Final Pipeline)
1. **Search**: Multi-strategy query (topic + “open access”, “arxiv”) via Semantic Scholar
2. **Filter**: Prioritize open-access hosts; block known paywalled domains
3. **Download**: Try direct PDF; if HTML, sniff for `.pdf` links; exponential backoff
4. **Extract**: Use PyMuPDF to extract text; store in `data/extracted/`
5. **Analyze**: Compute stats, aggregate cross-paper findings
6. **Write**: Generate Abstract, Introduction, Methodology, Results, Conclusion, References
7. **Format**: APA 7 references, sorted, with DOI links
8. **Export**: Server-side PDF export from the UI

---

## 📊 JSON Structures

### `data/metadata/selected_papers.json`
- Papers selected and successfully downloaded with paths and metadata.

### `data/metadata/analyzed_papers.json`
- Text statistics (length, readability, n-grams, key terms).

### `data/metadata/drafts.json`
- Generated sections and references.

### `data/metadata/critiques.json`
- Heuristic critique notes (readability, structure).

---

## 📝 Logging
Logs are saved to `data/logs/`:
- `search_papers.log` – Search API calls and errors
- `download_pdf.log` – Download progress and validation
- `ui.log` – UI-level events (if enabled)

---

## 🧪 Testing
```powershell
cd ai_paper_review
pytest -q tests/test_all.py
```

---

## ⚙️ Configuration Cheatsheet
```powershell
# Semantic Scholar API
$env:SEMANTIC_SCHOLAR_API_KEY = "your_key"          # optional
$env:SEMANTIC_SCHOLAR_TIMEOUT = 12                   # default 12s
$env:SEMANTIC_SCHOLAR_MAX_RETRIES = 2                # default 2
$env:USE_CACHED_METADATA_ON_FAILURE = 1              # fallback to cache
$env:SEMANTIC_SCHOLAR_FALLBACK_PATH = "data/metadata/paper_metadata.json"

# PDF download behavior
$env:PDF_DOWNLOAD_TIMEOUT = 20                       # seconds
$env:PDF_DOWNLOAD_MAX_RETRIES = 3
$env:PDF_RETRY_ONLY_ON_RETRYABLE = 1                 # skip restricted hosts
```

---

## 📌 Notes
- Legacy UI files (`ui/app.py`, `ui/app_flask.py`) and demo scripts were removed to streamline the project.
- Use `ui/app_modern.py` as the primary entry point for the final experience.
- See `MILESTONE3_SUMMARY.md` for a narrative of the journey and final checks.
