# 📍 Milestone 3 — Draft Generation & Synthesis (Week 5–6)

## 🧠 Project Title
**AI System to Automatically Review and Summarize Research Papers**  
Infosys Springboard Internship

---

## 📌 Milestone Objective
The objective of **Milestone 3** is to transform the structured and cleaned textual data extracted in **Milestone 2** into a coherent academic review draft.

This milestone focuses on:
- Content aggregation across multiple research papers  
- Transformer-based text generation  
- Structured draft creation suitable for academic and research review purposes  

---

## ✅ Features Implemented

### 🔹 Draft Generation Pipeline
- Aggregation of extracted sections across multiple research papers  
- Structured generation of:
  - **Abstract** (≈100 words)
  - **Methodology Comparison**
  - **Results Synthesis**

---

### 🔹 Transformer-based NLP
- Utilized Hugging Face Transformer models (e.g., `t5-small`)  
- Prompt-driven summarization for academic-style outputs  
- Controlled generation using token limits and deterministic decoding  

---

### 🔹 Section-wise Processing
- Abstract synthesis from combined abstracts  
- Methodology comparison across papers  
- Results synthesis highlighting trends and key findings  

---

### 🔹 Structured Output Storage
Human-readable and machine-readable outputs saved as:
- `draft_report.json`
- `summary_metrics.json`

---

### 🔹 Metrics & Validation
- Number of papers used in generation  
- Sections generated  
- Model used  
- Timestamped generation metadata  

---

### 🔹 Enhanced Presentation (Colab UI)
- Section-wise preview using Markdown rendering  
- Clear and readable academic layout inside Google Colab  
- Progress indicators during generation  

---

## 📂 Folder Structure
```
Milestone3/
│
├── Milestone 3 – Draft Generation & Synthesis.ipynb
│
├── data/
│ └── drafts/
│ ├── draft_report.json
│ └── summary_metrics.json
│
└── README.md

```
---

## 📄 Outputs Generated

### 1️⃣ Draft Report (`draft_report.json`)
Structured academic draft containing:
- Generated abstract  
- Methods comparison  
- Results synthesis  
- Number of papers used  

---

### 2️⃣ Summary Metrics (`summary_metrics.json`)
Includes:
- Number of papers processed  
- Sections generated  
- Average word statistics  
- Model details  
- Generation timestamp  

---

## 🧪 Technologies Used
- Python 3.x  
- Hugging Face Transformers  
- PyTorch  
- Google Colab  
- JSON-based data storage  
- IPython Markdown display  

---

## 🎯 Milestone Outcome
By the end of **Milestone 3**:
- A structured academic review draft is automatically generated  
- Outputs are stored for downstream integration  
- The system is prepared for UI integration and end-to-end automation  

This milestone establishes the foundation for **Milestone 4**, where the complete pipeline will be integrated into an interactive user interface.
