# 📍 Milestone 2 — PDF Text Extraction & Preprocessing  
### Infosys Springboard Internship | AI Research Paper Review System

---

## 📌 Milestone Overview
Milestone 2 focuses on extracting readable text from research paper PDFs downloaded in Milestone 1 and preparing the content for downstream Natural Language Processing (NLP) tasks such as summarization and analysis.

This milestone transforms raw PDF documents into clean, structured text datasets.

---

## 🎯 Objectives
- Load PDFs downloaded in Milestone 1  
- Extract textual content using reliable PDF parsers  
- Handle layout-aware and standard text extraction  
- Clean and preprocess extracted text  
- Remove noise such as references, headers, and footers  
- Store processed text in a structured format  

---

## 🧠 Key Functionalities
- Automatic detection of PDF files from the `downloads/` directory  
- Layout-aware text extraction (where supported)  
- Standard text extraction fallback mechanism  
- Text cleaning and normalization  
- Section-wise preprocessing  
- JSON-based output for easy reuse in later milestones  

---

## 🏗️ Tech Stack & Libraries
- Python 3.x  
- Google Colab  
- PyMuPDF (fitz)  
- pdfplumber  
- tqdm  
- regex (re)  
- json, os  

---

## 📂 Input & Output Structure

### 📥 Input
```
downloads/
├── paper1.pdf
├── paper2.pdf

```
### 📤 Output

```
data/extracted/
├── paper1_extracted.json
├── paper2_extracted.json

```
Each output file contains:
- Paper title  
- Extracted raw text  
- Cleaned and preprocessed text  

---

## ▶️ How to Run
1. Ensure **Milestone 1** has been executed successfully  
2. Confirm PDFs exist in the `downloads/` folder  
3. Open `Module2_PDF_Text_Extraction.ipynb` in Google Colab  
4. Run all cells sequentially  

---

## ✅ Status
**Completed**  
- PDFs successfully processed  
- Clean text dataset generated  
- Ready for summarization in Milestone 3  

---

## 🚀 Next Step
Proceed to **Milestone 3 — Summarization Engine**, where transformer-based NLP models will be applied to generate concise research summaries.

---
