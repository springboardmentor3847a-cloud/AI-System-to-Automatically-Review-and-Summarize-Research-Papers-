# AI-System-to-Automatically-Review-and-Summarize-Research-Papers-
# 📚 Automated Research Paper Analysis Using AI  

## 🔍 Overview
This project implements an **end-to-end automated research analysis pipeline** that collects academic papers, extracts and processes their content, applies **AI-based summarization and analysis**, and finally evaluates and refines the outputs into a **stable, high-quality final report**.

The system is developed using a **milestone-based approach**, where **Milestone 1 and Milestone 2 are combined into a single notebook** for implementation efficiency.

---

## 🎯 Project Objectives
- Automate research paper discovery from open-access sources  
- Extract and preprocess text from academic PDFs  
- Apply AI-based summarization and thematic analysis  
- Generate an automated literature review  
- Evaluate quality and finalize outputs  

---

## 🧩 Project Structure

├── Milestone_1 #Implemented automated research paper retrieval via the Semantic Scholar API
├── Milestone_2 # PDF TEXT EXTRACTION, ANALYSIS & CROSS-PAPER COMPARISON
├── Milestone_3 # AI-based summarization & analysis
├── Milestone_4 # Review, evaluation & final report
├── data/
│ ├── pdfs/ # Downloaded PDF files
│ ├── raw_text/ # Extracted plain text (.txt)
│ ├── structured_text/ # Section-wise structured content
│ └── logs/ # Failed PDFs and runtime logs
├── milestone_3_outputs/
│ ├── summaries.json
│ └── literature_review.txt
├── final_report/
│ ├── final_summaries.json
│ └── final_literature_review.txt


---

## 🚀 Milestone Breakdown

### ✅ Milestone 1 & Milestone 2 (Combined)  
**Problem Definition, Data Collection & Preprocessing**

**Notebook:** `Milestone_2.ipynb`

**Key Features:**
- Problem understanding and system design  
- Research paper metadata retrieval (Semantic Scholar / OpenAlex)  
- Open-access PDF downloading with runtime limits  
- Robust PDF text extraction using PyMuPDF  
- Handling corrupted or invalid PDFs gracefully  
- Structured storage of extracted text  

📌 *Milestone 1 (conceptual design) and Milestone 2 (implementation) are intentionally combined in a single notebook.*

---

### ✅ Milestone 3: AI-Based Summarization, Analysis & Literature Review  
**Notebook:** `Milestone_3.ipynb`

**Key Features:**
- Loads extracted text from Milestone 2  
- AI-based extractive summarization using NLP techniques  
- Keyword extraction and thematic analysis  
- Section-wise analysis using structured text  
- Automated literature review generation  

---

### ✅ Milestone 4: Final Review, Quality Evaluation & Reporting  
**Notebook:** `Milestone_4.ipynb`

**Key Features:**
- Review and refinement of AI-generated summaries  
- Lightweight quality evaluation metrics  
- Stability verification of the full pipeline  
- Final consolidated report generation  

---

## 🛠️ Technologies & Libraries Used
- Python 3  
- Semantic Scholar / OpenAlex APIs  
- PyMuPDF (fitz)  
- NLTK  
- tqdm  
- JSON, pathlib  

---

## ▶️ How to Run the Project

### Step 1: Run Milestone 1
```bash
Run all cells in Milestone_1

✔ Downloads PDFs
✔ Extracts and stores text

###Step 2: Run Milestone 3
Run all cells in Milestone_3.ipynb

✔ Generates summaries
✔ Produces literature review

####Step 3: Run Milestone 4
Run all cells in Milestone_4.ipynb


✔ Refines outputs
✔ Evaluates quality
✔ Generates final report




