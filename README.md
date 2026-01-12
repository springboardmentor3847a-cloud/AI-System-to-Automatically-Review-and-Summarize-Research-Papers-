# Automated Research Paper Analysis & Draft Generation System

## Project Overview

This project implements an end-to-end automated research assistant that supports academic research by automating paper discovery, content extraction, synthesis, draft generation, and refinement.  
It follows a milestone-based development approach completed over 8 weeks as part of the Infosys Springboard program.

---

## Milestone 1: Topic Input & Paper Search (Week 1–2)

### Description
Allows users to input a research topic and automatically retrieve relevant academic papers using the Semantic Scholar API.

### Key Features
- Topic-based paper search
- Metadata extraction (title, authors, year, venue)
- PDF download support
- JSON-based storage of results

### Output
- Research paper PDFs  
- Metadata JSON files

---

## Milestone 2: PDF Text Extraction & Analysis (Week 3–4)

### Description
Processes downloaded PDFs and extracts structured academic content for analysis.

### Key Features
- PDF text extraction
- Section-wise parsing (Abstract, Methods, Results, etc.)
- Keyword and key-finding extraction
- Cross-paper comparison
- Structured dataset creation

### Technologies
- Python
- pdfplumber
- pandas
- scikit-learn

### Output
- Structured JSON files
- Analysis-ready datasets

---

## Milestone 3: Automated Draft Generation (Week 5–6)

### Description
Synthesizes extracted content from multiple papers to automatically generate academic draft sections.

### Generated Sections
- Abstract
- Methods
- Results
- References (APA format)

### Key Features
- Academic-style text generation
- Cross-paper synthesis
- Rate-limit handling
- Robust and reproducible execution

### Output
Generated drafts stored in:

milestone-3/output/

---

## Milestone 4: Review, Refinement & UI Integration (Week 7–8)

### Description
Introduces a human-in-the-loop review and refinement process through an interactive web interface.

### Key Features
- Academic quality evaluation
- Section-wise refinement
- User-controlled revision
- Gradio-based UI with separate tabs for sections

### How to Run
```bash
pip install gradio
python app.py

##Pipeline Flow
Paper Search → PDF Extraction → Draft Generation → Review & Refinement

##Final Outcome
Automated academic research workflow
Reduced manual effort in literature review and drafting
Structured and professional research drafts
Interactive refinement interface

##Technologies Used
Python
Semantic Scholar API
pdfplumber
pandas
scikit-learn
Large Language Models (LLMs)
Gradio
