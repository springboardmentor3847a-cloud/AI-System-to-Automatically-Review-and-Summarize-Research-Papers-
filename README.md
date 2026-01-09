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


⚙️ Configuration
🔑 Environment Variables (.env)
GEMINI_API_KEY=your_gemini_api_key_here

 How to Run
python week_5_6_milestone3.py

*Error Handling & Robustness

1.Handles missing APIs gracefully
2.Avoids hard-coded model dependencies
3.Prevents pipeline failure during evaluation
4.Ensures end-to-end execution in all environments

 Milestone 4: Review, Refinement & UI Integration (Week 7–8)
 Overview:
 
This module implements Milestone 4 (Week 7–8) of the automated research pipeline.
It extends Milestone 3 (Automated Draft Generation) by introducing a human-in-the-loop review and refinement cycle, along with a polished interactive UI for final evaluation and revision.
The goal of this milestone is to ensure that the automatically generated academic draft is:

Critically reviewed
Refined for academic quality
User-controllable
Presentation-ready

Objectives Achieved:

Review and refinement cycle for generated content
Revision suggestions and quality evaluation module
Final UI integration using Gradio
User-triggered re-run of revision cycle
Final report preparation
Final testing, documentation, and demo readiness

Core Features:
Review & Quality Evaluation
Performs rule-based quality checks on generated sections
Evaluates:
Length adequacy
Sentence structure
Readability

Revision Suggestions (LLM-Assisted):

Uses Google Gemini (2.5 Flash preferred) to:
Critique generated sections
Suggest targeted academic improvements
Suggestions focus on:

Clarity
Coherence
Academic tone

Does not overwrite content automatically

User-Triggered Revision Cycle:

A dedicated “Critique / Revise” button allows users to:
Trigger evaluation
View suggestions
Generate a refined version of the section
Enables human-in-the-loop control, essential for academic writing

Final UI Integration using Gradio:

The module provides a polished Gradio interface that:

Displays generated sections in separate tabs:

Abstract
Methods
Results

Shows:
Original section
Quality evaluation
Revision suggestions
Revised version
This UI enables interactive review, refinement, and demonstration.

How to run:
pip install gradio python-dotenv
python week_7_8_milestone4.py

Error Handling & Robustness:
Gracefully handles:

Revoked API keys
Gemini overload (503 errors)
Network/API failures

Prevents crashes during UI interaction
Allows safe demo even in restricted environments
Clear warning messages displayed instead of runtime failures

Pipeline Position
Milestone 1 → Auotmactic paper selection 
Milestone 2 → PDF Extraction & Analysis
Milestone 3 → Automated Draft Generation
Milestone 4 → Review, Refinement & UI Integration
