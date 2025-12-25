# Milestone 2 — Progress Summary (to date)

This document summarizes what is built and working so far in the AI Paper Reviewer project, focusing on end‑to‑end integration and the user interface.

## What’s Implemented

- Search and filtering: Semantic Scholar search with optional filters (`year_min`, `min_citations`) and retry logic.
- Robust PDF download: Fallback URL detection (e.g., arXiv abs→pdf), streaming downloads with progress bars, validation of `%PDF` header, and structured metadata saving.
- Text extraction: Converts PDFs to plain text files for downstream analysis.
- Lightweight text analysis: Readability metrics (Flesch, FK grade), type‑token ratio, top n‑grams, and heuristic noun phrases.
- Draft generation: Heuristic summaries built from metadata and analysis results (no external LLM required).
- Draft critique: Rule‑based flags and suggestions to improve the drafts.
- End‑to‑end orchestration: A single function `create_dataset()` executes search → download → extract → analyze → draft → critique.
- Gradio UI: A simple app to run the full pipeline interactively.

## End‑to‑End Flow

1. Search papers (`modules/search_papers.py`):
   - Uses Semantic Scholar API (optional `SEMANTIC_SCHOLAR_API_KEY` via `.env`).
   - Applies filters and retries; writes `data/metadata/paper_metadata.json`.
2. Download PDFs (`modules/download_pdf.py`):
   - Validates PDFs, handles redirects/HTML pages, saves to `data/pdfs/`.
   - Writes consolidated selection to `data/metadata/selected_papers.json`.
3. Extract text (`modules/extract_text.py`):
   - Produces `.txt` per paper under `data/extracted/`.
4. Analyze text (`modules/analyze_text.py`):
   - Computes readability and lexical stats; writes `data/metadata/analyzed_papers.json`.
5. Generate drafts (`modules/generate_draft.py`):
   - Produces concise, structured drafts; writes `data/metadata/drafts.json`.
6. Critique drafts (`modules/critique_draft.py`):
   - Adds flags/suggestions; writes `data/metadata/critiques.json`.

All steps are orchestrated from `scripts/prepare_dataset.py` (`create_dataset()`), and exposed via the Gradio UI in `ui/app.py`.

## Current Artifacts (as of this milestone)

- Metadata:
  - `data/metadata/paper_metadata.json`
  - `data/metadata/selected_papers.json`
  - `data/metadata/analyzed_papers.json`
  - `data/metadata/drafts.json`
  - `data/metadata/critiques.json`
- Extracted text samples:
  - `data/extracted/*.txt` (3 sample papers included)
- Logs:
  - `data/logs/` contains per‑module logs (search, download, analysis, drafts, critiques).

## User Interface

- Gradio app at `ui/app.py`:
  - Inputs: topic, max papers, min year, min citations.
  - Action: “Run full pipeline” triggers `create_dataset()`.
  - Output: JSON stats for the run.

## Reliability & Design Choices

- Defensive HTTP and file handling (timeouts, retries, validation of headers).
- Heuristic fallbacks for PDF links (e.g., HTML pages pointing to PDFs).
- Clear logging to `data/logs/*` for traceability.
- No vendor LLM dependency for summarization/critique; everything runs locally.

## How to Run

```powershell
# Using the project virtual environment
& C:\Users\vinod\Desktop\MinorProject\.venv\Scripts\python.exe C:\Users\vinod\Desktop\MinorProject\ai_paper_review\ui\app.py

# Or run the full workflow headlessly
& C:\Users\vinod\Desktop\MinorProject\.venv\Scripts\python.exe C:\Users\vinod\Desktop\MinorProject\ai_paper_review\scripts\prepare_dataset.py
```

## Next Steps (toward Milestone 2 completion)

- UI enhancements (auto‑open browser, progress status per step, error surfacing).
- Richer extraction quality checks and PDF normalization.
- Improved analysis (entity/keyphrase extraction, section detection, citation parsing).
- Draft improvements (section templates per venue/type; richer narrative).
- Visualization/reporting (HTML/PDF export of summaries and critiques).
- Caching and reproducibility (dedupe, re‑run avoidance, config profiles).
- Expanded tests (module‑level + end‑to‑end scenarios).
