This directory includes a few sample datasets to get you started.

*   `california_housing_data*.csv` is California housing data from the 1990 US
    Census; more information is available at:
    https://docs.google.com/document/d/e/2PACX-1vRhYtsvc5eOR2FWNCwaBiKL6suIOrxJig8LcSBbmCbyYsayia_DvPOOBlXZ4CAlQ5nlDD8kTaIDRwrN/pub

*   `mnist_*.csv` is a small sample of the
    [MNIST database](https://en.wikipedia.org/wiki/MNIST_database), which is
    described at: http://yann.lecun.com/exdb/mnist/

*   `anscombe.json` contains a copy of
    [Anscombe's quartet](https://en.wikipedia.org/wiki/Anscombe%27s_quartet); it
    was originally described in

    Anscombe, F. J. (1973). 'Graphs in Statistical Analysis'. American
    Statistician. 27 (1): 17-21. JSTOR 2682899.

    and our copy was prepared by the
    [vega_datasets library](https://github.com/altair-viz/vega_datasets/blob/4f67bdaad10f45e3549984e17e1b3088c731503d/vega_datasets/_data/anscombe.json).

# Automated Research Paper Text Extraction and Analysis

# Overview
This project implements an automated pipeline for extracting, structuring, and analyzing text from academic research paper PDFs.

# Features
- Robust PDF text extraction
- Section-wise content extraction
- Automatic key-finding extraction using TF-IDF
- Cross-paper similarity analysis
- Validation of extracted text
- Structured dataset generation

## Technologies Used
- Python
- PyMuPDF
- pymupdf4llm
- scikit-learn
- pandas


📄 Milestone 3: Automated Draft Generation (Week 5–6)
📌 Overview

This module implements Milestone 3 of the research automation pipeline.
It focuses on automated academic draft generation by synthesizing extracted research content from multiple papers (Milestone 2 output) using LLM-based text generation.

The system generates structured drafts for:
Abstract
Methods
Results
References (APA format)
It is designed to be robust, reproducible, and evaluation-safe, with fallback mechanisms to ensure execution even in restricted environments.

🧠 Core Features
✅ Automated Section Drafting
Generates Abstract, Methods, and Results sections automatically
Uses synthesized findings across multiple papers
Maintains formal academic tone and structure

✅ Gemini-Based Text Generation
Uses Google Gemini 2.5 Flash for primary content generation
Ensures semantic coherence and high-quality academic language
✅ Fallback Mechanism (Robust Design)

If Gemini API access is unavailable (missing key, SDK, or network):

The system gracefully falls back to a deterministic text generator
Ensures no runtime failure during evaluation
Guarantees reproducibility in offline or restricted environments
This design choice follows industry best practices for AI system robustness.

📂 Input & Output
📥 Input
JSON metadata files from Milestone 2

Located in:
processed/metadata/
Each file contains:
Extracted sections
Key findings
Themes
Paper metadata

📤 Output
Generated drafts are stored in:
milestone3_output/
File	Description
final_draft.json	Structured machine-readable draft
final_draft.docx	Human-readable Word document
final_draft.pdf	Submission-ready PDF
📑 APA Citation Support

In-text citations follow APA-style format
(Author et al., Year)
References are auto-generated using extracted metadata

⚙️ Configuration
🔑 Environment Variables (.env)
GEMINI_API_KEY=your_gemini_api_key_here
⚠️ .env is excluded from version control for security reasons(but still uploaded for your review).

▶️ How to Run
python week_5_6_milestone3.py

*Error Handling & Robustness

1.Handles missing APIs gracefully
2.Avoids hard-coded model dependencies
3.Prevents pipeline failure during evaluation
4.Ensures end-to-end execution in all environments
