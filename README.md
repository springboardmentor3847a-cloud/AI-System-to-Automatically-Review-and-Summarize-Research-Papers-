📄 Automated Research Paper Analysis & Draft Generation System
🔹 Short Project Description

This project implements an end-to-end automated research assistant that searches academic papers, extracts and analyzes their content, synthesizes findings across multiple papers, generates structured academic drafts using Large Language Models (LLMs), and enables human-in-the-loop review and refinement via an interactive web-based UI.

The system is designed to support research automation, academic writing assistance, and literature synthesis, following a milestone-based development approach over 8 weeks as part of the Infosys Springboard Internship.

🔹 Milestone 1: Topic Input & Paper Search (Week 1–2)
Overview

This module allows users to input a research topic and automatically retrieve relevant academic papers using the Semantic Scholar API.

Key Features

Topic-based academic paper search

Retrieval of paper metadata:

Title

Authors

Year of publication

Venue

PDF availability

Automated PDF download for selected papers

JSON-based storage of retrieved metadata

Logging for reproducibility and traceability

Output

Downloaded research paper PDFs

Metadata stored in structured JSON format

🔹 Milestone 2: PDF Text Extraction & Analysis (Week 3–4)
Overview

This module processes the downloaded PDFs and converts them into structured, analyzable text data.

Core Features

Robust PDF text extraction using pdfplumber

Section-wise parsing:

Abstract

Introduction

Methodology

Results

Conclusion

Flexible section header detection

Keyword extraction

Key findings extraction

Cross-paper comparison:

Keyword overlap

Summary statistics

Validation of extracted content

Structured JSON dataset generation

Technologies Used

Python

pdfplumber

pandas

scikit-learn

Output

Structured JSON files (one per paper)

Cross-paper comparison CSV files

Logs for verification and debugging

🔹 Milestone 3: Automated Draft Generation (Week 5–6)
Overview

This module focuses on automated academic draft generation by synthesizing extracted research content from multiple papers (Milestone 2 output) using LLM-based text generation.

The system generates structured academic sections while maintaining a formal, professional research tone.

Generated Sections

Abstract

Methods

Results

Results with in-text citations

References (APA format)

Core Features
✅ Automated Section Drafting

Synthesizes findings across multiple papers

Produces coherent, academic-style drafts

Ensures logical flow and clarity

✅ Token-Safe Aggregation

Aggregates Milestone 2 JSON outputs dynamically

Compresses input to avoid token overflow

Handles rate limits gracefully with retry logic

✅ Robust Execution Design

No hard-coded datasets

Dynamically reads Milestone 2 outputs

Designed to run safely during evaluation

Input & Output
Input

JSON files generated in Milestone 2

Located in:

milestone-2/extracted_text/

Output

Generated drafts stored in:

milestone-3/output/

File Name	Description
abstract.txt	Generated abstract
methods.txt	Generated methods section
results.txt	Generated results section
results_with_citations.txt	Results with citations
references.txt	APA-formatted references
🔹 Milestone 4: Review, Refinement & UI Integration (Week 7–8)
Overview

This module implements the final stage of the pipeline by introducing a human-in-the-loop review and refinement cycle along with a polished Gradio-based web interface.

The objective is to ensure the automatically generated academic content is:

Critically reviewed

Refined for academic quality

User-controllable

Presentation-ready

Objectives Achieved

Review and refinement cycle for generated content

Academic quality evaluation

User-triggered revision workflow

Final UI integration using Gradio

Final report presentation

Core Features
🔍 Review & Quality Evaluation

Evaluates generated sections for:

Clarity

Structure

Academic tone

Readability

Identifies areas needing improvement

✍️ Revision & Refinement

Refines content using LLM assistance

Improves:

Coherence

Formal tone

Logical flow

Preserves original meaning while enhancing quality

🧠 Human-in-the-Loop Control

User-triggered Critique / Revise workflow

Allows re-running refinement cycles on demand

Essential for academic writing assistance

🖥️ Final UI Integration (Gradio)

Single-file Gradio application (app.py)

Tab-based display for:

Abstract

Methods

Results

References

Clean, evaluator-friendly interface

How to Run
pip install gradio
python app.py

Robustness & Error Handling

Graceful handling of:

API rate limits

Network issues

Missing environment variables

Prevents crashes during UI interaction

Clear runtime messages for safe evaluation

🔁 Pipeline Summary
Milestone 1 → Automated paper search & selection  
Milestone 2 → PDF extraction & structured analysis  
Milestone 3 → Automated academic draft generation  
Milestone 4 → Review, refinement & UI integration  

✅ Final Outcome

Fully automated academic literature analysis pipeline

Reduced manual effort in literature review

Professionally structured academic drafts

Interactive review and refinement interface

Evaluation-safe, modular, and scalable design
