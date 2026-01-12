An AI-powered research assistant that automatically searches, analyzes, summarizes, reviews, and formats academic research papers into structured systematic literature reviews with APA citations and PDF output.

This system is designed for students, researchers, and academicians who want to save time while producing high-quality research reviews.

Features

✔ Automated research paper search
✔ PDF extraction and preprocessing
✔ AI-based summarization and review
✔ APA-style citation formatting
✔ Plagiarism-safe paraphrasing
✔ Structured systematic review generation
✔ PDF report creation
✔ Secure login system
✔ Research history storage

How the System Works
User enters a research topic
System searches online academic sources
Relevant papers are downloaded
PDFs are processed and cleaned
AI analyzes and summarizes content

Results are structured into sections:

Abstract
Introduction
Methodology
Findings
Conclusion
APA references are generated
A final PDF review paper is created

 Project Folder Structure
research_ai/
│
├── app.py                # Gradio UI
├── backend.py            # Core system logic
├── auth.py               # User authentication
├── database.py           # SQLite database handling
├── research_ai.db        # User & research data
│
├── paper_search.py       # Finds research papers
├── pdf_handler.py        # Extracts text from PDFs
├── analysis.py           # AI analysis & summarization
├── reviewer.py           # Systematic review generator
├── writer.py             # Final report writer
├── apa_formatter.py      # APA citation generator
├── pdf_generator.py     # Converts results to PDF
│
├── workflow.py           # Connects all components
├── check_models.py       # AI model validation
│
├── .env                  # API keys
├── requirements.txt      # Python dependencies
└── README.md

Installation & Setup
1.Clone the Repository
git clone https://github.com/yourusername/research_ai.git
cd research_ai

2️.Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows

3.Install Dependencies
pip install -r requirements.txt

Add API Key
Create .env file:

GEMINI_API_KEY=your_api_key_here
SEMANTIC_SCHOLAR_API_KEY=your_api_key_here

▶️ Run the Application
python app.py

Open in browser: http://localhost:8501

Technologies Used

Python
Gradio
OpenAI / LLM
SQLite
PyPDF
NLP
Research APIs

Use Cases
College project reports
Thesis and dissertations
Literature review papers
Research surveys
Journal preparation

🔐 Security
User authentication system
Encrypted password storage
Secure API key handling

Output
The system generates:
  Structured review text
  APA formatted references
  Downloadable PDF research paper
