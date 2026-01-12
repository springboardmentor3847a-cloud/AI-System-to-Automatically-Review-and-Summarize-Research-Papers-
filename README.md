# 🤖 Automated Research Assistant & Paper Analyzer

An end-to-end research automation pipeline that discovers, downloads, analyzes, and synthesizes academic papers. This tool automates the tedious parts of the research lifecycle, converting unstructured PDF data into structured insights and polished literature review drafts.

---

## 🚀 Key Features

The project is divided into 6 modular stages, functioning as a complete **ETL (Extract, Transform, Load)** and **NLP** pipeline:

### 1. Discovery (Data Ingestion)
- **API Integration:** Connects to the **Semantic Scholar API** to fetch metadata for papers based on user queries.
- **Filtering:** Automatically filters results based on Open Access PDF availability and citation counts.

### 2. Acquisition (Download Pipeline)
- **Robust Downloading:** Python `requests` with retry logic and User-Agent rotation.
- **Validation:** Verifies file integrity (checking magic bytes) to ensure downloaded files are valid PDFs, not corrupted HTML headers.

### 3. Extraction (Unstructured Data Processing)
- **Text Parsing:** Uses **PyMuPDF (Fitz)** to extract raw text from PDFs.
- **Intelligent Sectioning:** detailed Regex patterns to parse text into logical sections (Abstract, Introduction, Methods, Results, Conclusion).
- **Cleaning:** Removes artifacts, hyphenation issues, and non-printable characters.

### 4. Analysis (NLP & Insights)
- **Metadata Extraction:** Heuristic extraction of specific methods, datasets, and metrics used in the papers.
- **Cross-Paper Comparison:** Uses **TF-IDF** and **Cosine Similarity (Scikit-Learn)** to calculate semantic similarity scores between papers.
- **Pattern Recognition:** Identifies common research gaps and trending methodologies.

### 5. Synthesis (Draft Generation)
- **Generative Drafting:** Generates structured academic drafts (Abstract, Intro, Methods, etc.) based on the analyzed data.
- **Simulation Mode:** Includes a template-based generator to simulate LLM outputs without incurring API costs (extensible to OpenAI API).

### 6. Refinement (Critique Loop)
- **Automated Critique:** Analyzes the generated draft for structure, clarity, passive voice, and repetition.
- **Iterative Improvement:** Automatically revises the text based on the critique scorecard to produce a polished final output.

---

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **Data Acquisition:** `semanticscholar`, `requests`
- **PDF Processing:** `pymupdf` (fitz), `pymupdf4llm`
- **Machine Learning / NLP:** `scikit-learn`, `numpy`, `tiktoken`
- **File Management:** `pathlib`, `json`, `os`

---

## ⚙️ Installation & Usage

### Clone the repository

```

git clone https://github.com/springboardmentor3847a-cloud/AI-System-to-Automatically-Review-and-Summarize-Research-Papers
cd research-automation-tool

```

### Create a Virtual Environment

```

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```

### Install Dependencies

```

pip install -r requirements.txt
(Note: Ensure you have scikit-learn, semanticscholar, pymupdf, requests, and tiktoken installed)

```

### Run the Pipeline You can run the modules sequentially or via the main orchestrator:

```

python main.py
Follow the on-screen prompts to enter your research topic.

```
