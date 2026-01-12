# AI System to Automatically Review and Summarize Research Papers

An intelligent system that automates the process of reviewing and summarizing academic research papers using AI.

## 🎯 Milestone 1 → 2: Retrieval → Text Prep

### Overview
Automated paper search, PDF download, text extraction, and basic text analysis using the Semantic Scholar API + PyMuPDF.

### ✨ Features Implemented

- ✅ **Automated Paper Search** via Semantic Scholar API
- ✅ **Advanced Filtering**: by year, citation count, and author
- ✅ **PDF Download** with progress tracking
- ✅ **Metadata Extraction**: title, abstract, authors, citations, year
- ✅ **Dataset Preparation**: structured JSON output
- ✅ **Error Handling & Retry Logic**
- ✅ **Logging** for debugging and monitoring
- ✅ **Progress Bars** with tqdm
- ✅ **PDF Validation** with file integrity checks
- ✅ **Text Extraction** to `data/extracted/*.txt`
- ✅ **Basic Text Analysis** (counts, top terms) to `data/metadata/analyzed_papers.json`

---

## 📁 Folder Structure

```
ai_paper_review/
├── modules/
│   ├── search_papers.py       # Paper search with Semantic Scholar API
│   ├── download_pdf.py        # PDF download with validation
│   ├── extract_text.py        # Extract PDF text to data/extracted
│   ├── analyze_text.py        # Basic stats over extracted text
│   ├── generate_draft.py      # Generate lightweight drafts (includes narrative text)
│   ├── critique_draft.py      # Heuristic critique of drafts → data/metadata/critiques.json
│
├── scripts/
│   ├── prepare_dataset.py     # Complete workflow script
│   └── check_imports.py       # Dependency checker
│
├── data/
│   ├── pdfs/                  # Downloaded PDF files
│   ├── extracted/             # Extracted text
│   ├── metadata/              # JSON metadata files
│   └── logs/                  # Application logs
│
├── ui/
│   └── app.py                 # [Milestone 6] Gradio UI
│
├── .env.example               # Environment variables template
├── .env                       # Your API keys (create from .env.example)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🚀 Quick Start

### Step 1: Environment Setup

**Create and activate a virtual environment:**

```powershell
# Create virtual environment
python -m venv .venv

# Activate (PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (Command Prompt)
.venv\Scripts\activate.bat

# Activate (Git Bash / Linux / macOS)
source .venv/bin/activate
```

**Install dependencies:**

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Configure API Keys

1. Copy the example environment file:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```bash
   SEMANTIC_SCHOLAR_API_KEY=your_key_here  # Optional but recommended
   OPENAI_API_KEY=your_key_here            # For future milestones
   ```

   **Get API Keys:**
   - Semantic Scholar: https://www.semanticscholar.org/product/api#api-key
   - OpenAI: https://platform.openai.com/api-keys

### Step 3: Quick Start with run.py

**The easiest way to run the project:**

```powershell
# Check dependencies
python run.py --check

# Run workflow test
python run.py --test

# Launch web UI (recommended)
python run.py --ui

# Run full pipeline from command line
python run.py --run --topic "machine learning" --limit 5
```

### Step 4: Run Paper Search (Alternative)

**Basic search:**

```powershell
python modules/search_papers.py
```

**Custom search (edit the main block in search_papers.py):**

```python
# Example with filters
data = search_papers(
    topic="deep learning computer vision",
    limit=10,
    year_min=2020,
    min_citations=50
)
```

---

## 📸 Submission Snippets

See `OUTPUT_SNIPPETS.md` for ready-to-use commands to capture:
- PDFs list (filenames)
- Metadata JSON excerpt
- Search and download logs tails
- Quick environment check

Example (PowerShell):
```powershell
Get-ChildItem data\pdfs | Select-Object Name | Out-File snippets_pdfs.txt
Get-Content data\metadata\selected_papers.json -Head 100 | Out-File snippets_metadata_head.txt
Get-Content data\logs\search_papers.log -Tail 50 | Out-File snippets_search_log_tail.txt
Get-Content data\logs\download_pdf.log -Tail 50 | Out-File snippets_download_log_tail.txt
```

**Output:** `data/metadata/paper_metadata.json`

### Step 4: Download PDFs

**Run the download module:**

```powershell
python modules/download_pdf.py
```

This will:
- Load papers from `data/metadata/paper_metadata.json`
- Download PDFs with available links
- Validate downloaded files
- Save metadata to `data/metadata/selected_papers.json`

**Output:**
- PDFs: `data/pdfs/`
- Metadata: `data/metadata/selected_papers.json`

### Step 5: Prepare Complete Dataset (search → download → extract → analyze → draft → critique)

**Run the all-in-one dataset preparation script:**

```powershell
python scripts/prepare_dataset.py
```

This script:
1. Searches for papers on a configured topic
2. Filters by year and citations
3. Downloads available PDFs (with retries + validation)
4. Extracts text to `data/extracted/*.txt`
5. Analyzes text (counts, readability, n-grams, top terms) to `data/metadata/analyzed_papers.json`
6. Generates drafts with narrative to `data/metadata/drafts.json`
7. Critiques drafts heuristically to `data/metadata/critiques.json`
8. Saves dataset to `data/metadata/selected_papers.json` and validates

**Edit configuration in `prepare_dataset.py`:**

```python
RESEARCH_TOPIC = "deep learning natural language processing"
MAX_PAPERS = 10
MIN_YEAR = 2020
MIN_CITATIONS = 50
```

---

## 📊 Output Format

### `selected_papers.json` Structure

```json
{
  "download_date": "2025-12-10 10:30:00",
  "total_papers": 5,
  "papers": [
    {
      "title": "Paper Title",
      "authors": ["Author 1", "Author 2"],
      "abstract": "Paper abstract text...",
      "year": 2023,
      "citation_count": 150,
      "influential_citation_count": 25,
      "paper_id": "abc123def456",
      "url": "https://semanticscholar.org/paper/...",
      "pdf_url": "https://arxiv.org/pdf/...",
      "pdf_path": "data/pdfs/abc123_Paper_Title.pdf",
      "pdf_available": true,
      "publication_date": "2023-06-15",
      "venue": "CVPR",
      "download_status": "success",
      "download_date": "2025-12-10 10:32:15",
      "text_path": "data/extracted/abc123_Paper_Title.txt",
      "extraction_status": "success",
      "extraction_method": "pymupdf",
      "text_characters": 12345
    }
  ]
}

### `analyzed_papers.json` Structure (enhanced stats)

```json
{
  "total": 3,
  "success": 3,
  "failed": 0,
  "missing_text": 0,
  "results": [
    {
      "paper_id": "abc123def456",
      "title": "Paper Title",
      "analysis_status": "success",
      "text_path": "data/extracted/abc123_Paper_Title.txt",
      "stats": {
        "characters": 12000,
        "words": 2200,
        "sentences": 130,
        "avg_word_length": 4.8,
        "avg_sentence_length": 17.1,
        "type_token_ratio": 0.42,
        "flesch_reading_ease": 48.5,
        "top_terms": [["learning", 42], ["model", 35], ["data", 30]],
        "top_bigrams": [["deep learning", 12]],
        "top_trigrams": [["natural language processing", 9]]
      }
    }
  ]
}
```

### `drafts.json` Structure (lightweight drafts with narrative)

```json
{
  "total": 3,
  "drafts": [
    {
      "title": "Paper Title",
      "paper_id": "abc123def456",
      "year": 2023,
      "citations": 150,
      "abstract": "...",
      "text_path": "data/extracted/abc123_Paper_Title.txt",
      "analysis_status": "success",
      "stats": {"...": "see analyzed_papers.json"},
      "strengths": ["Readable score: 48.5", "Top terms: learning, model"],
      "key_terms": ["learning", "model", "data"],
      "draft_text": "Paper Title (2023) (citations: 150). Content profile: ~2200 words; avg sentence 17.1 words; Flesch 48.5. Key terms: learning, model, data. Abstract: ..."
    }
  ]
}
```

### Additional one-off runs

```powershell
# Re-run analysis only (uses existing extracted text)
python modules/analyze_text.py

# Generate drafts from metadata + analysis
python modules/generate_draft.py

# Critique drafts heuristically (readability, length, keywords)
python modules/critique_draft.py
```

### `critiques.json` Structure (heuristic checks)

```json
{
  "total": 3,
  "critiques": [
    {
      "paper_id": "abc123def456",
      "title": "Paper Title",
      "flags": ["hard_to_read", "draft_too_short"],
      "suggestions": [
        "Improve readability (shorter sentences, simpler words).",
        "Expand draft_text with contribution, method, results."
      ],
      "draft_text": "..."
    }
  ]
}
```
```

---

## 🔧 Advanced Usage

### Search with Filters

```python
from modules.search_papers import search_papers, save_metadata

results = search_papers(
    topic="transformer models",
    limit=20,
    year_min=2022,
    year_max=2024,
    min_citations=100,
    author="Vaswani"
)

save_metadata(results, "data/metadata/transformers.json")
```

### Download Specific Papers

```python
from modules.download_pdf import download_papers, save_download_metadata

papers = [
    {
        "paper_id": "abc123",
        "title": "My Paper",
        "pdf_url": "https://example.com/paper.pdf"
    }
]

downloaded = download_papers(papers)
save_download_metadata(downloaded, "custom_dataset.json")
```

### Validate Dataset

```python
from scripts.prepare_dataset import validate_dataset

validate_dataset("data/metadata/selected_papers.json")
```

---

## 📝 Logging

Logs are saved to `data/logs/`:
- `search_papers.log` - Search API calls and errors
- `download_pdf.log` - Download progress and validation

**View logs:**

```powershell
Get-Content data\logs\search_papers.log -Tail 20
Get-Content data\logs\download_pdf.log -Tail 20
```

---

## 🐛 Troubleshooting

### Issue: `ConnectTimeout` or Network Errors

**Solution:**
1. Check your internet connection
2. Try increasing timeout in `search_papers.py`:
   ```python
   sch = SemanticScholar(api_key=API_KEY, timeout=60)
   ```
3. Check firewall/proxy settings

### Issue: No PDFs Downloaded

**Solution:**
- Many papers don't have open-access PDFs
- Filter by `pdf_available=True` in search results
- Try different search topics (e.g., "machine learning" has more open access papers)

### Issue: `.env` Parse Errors

**Solution:**
- Ensure `.env` has format: `KEY=value` (no spaces around `=`)
- No quotes needed around values
- One variable per line

### Issue: Module Import Errors

**Solution:**
```powershell
# Ensure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Next Steps (Future Milestones)

- **Milestone 2**: Text extraction from PDFs using PyMuPDF
- **Milestone 3**: Semantic analysis with LangChain
- **Milestone 4**: Automated review draft generation
- **Milestone 5**: Critical review with critique generation
- **Milestone 6**: Web UI with Gradio

---

## 🤝 Contributing

This project is part of an internship assignment. For questions or issues, please refer to the project documentation.

---

## 📄 License

Educational project for internship evaluation.

---

## 🎓 References

- Semantic Scholar API: https://api.semanticscholar.org/
- Research papers sourced via Semantic Scholar
- Built with Python, LangChain, and OpenAI GPT

---

## 🎬 Milestone 1 Demo (2–3 min)

For a quick, live demo guide, see `MILESTONE1_DEMO.md`.

Quick commands (PowerShell):

```powershell
# Verify setup
python scripts\quick_check.py

# End-to-end run (search → download → dataset)
python scripts\prepare_dataset.py

# Ensure outputs (fallback/verification)
python scripts\ensure_pdfs_and_metadata.py
```




## To run all the things done till now
python scripts\prepare_dataset.py; explorer data\pdfs; code data\metadata\selected_papers.json