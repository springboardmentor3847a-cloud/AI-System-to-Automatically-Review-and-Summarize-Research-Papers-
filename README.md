**AI-Powered Research Paper Search & Summarization System**

**Project Overview**

This project focuses on building an AI-assisted research workflow that can:
Search academic papers based on a given topic
Rank papers using citation count and relevance
Extract and process PDFs of selected research papers
Generate concise summaries using Large Language Models (LLMs)
The system is designed to help students and researchers quickly understand state-of-the-art research without manually reading multiple papers.

 **Key Features**

 Academic Paper Search using Semantic Scholar API
 Ranking & Filtering based on year, citations, and relevance score
 PDF Processing and text extraction
 LLM-based Summarization for quick insights
 Integration with LangChain and Google Generative AI
 Scalable architecture suitable for research automation


 **Technologies & Libraries Used**

Python
Semantic Scholar API
LangChain
LangGraph
Google Generative AI (Gemini)
pandas
PyMuPDF (pymupdf4llm)
tiktoken
requests

 **Project Structure**

Infosys_Intern_Final.ipynb   # Main Jupyter Notebook
README.md                   # Project documentation

 **Installation & Setup**

Run the following commands before executing the notebook:

pip install requests pandas
pip install semanticscholar
pip install langchain langchain-google-genai langgraph langsmith
pip install pymupdf4llm tiktoken


 Ensure you have a valid Google Generative AI API key configured in your environment variables.

** How It Works**

User provides a research topic
System fetches related papers from Semantic Scholar
Papers are ranked and filtered
Selected PDFs are parsed and cleaned
LLM generates structured summaries
Output is displayed directly in the notebook

 **Use Cases**

Literature review automation
Research topic exploration
Internship / academic project support
Time-efficient paper summarization

 **Outcome**

This project demonstrates the practical application of AI and LLMs in academic research, combining data retrieval, NLP, and intelligent summarization into a single workflow.

**The Final Output**

<img width="1919" height="1022" alt="Screenshot 2026-01-13 133124" src="https://github.com/user-attachments/assets/4b1580f2-74be-4dab-89c8-a83c0d326e34" />

<img width="1919" height="1022" alt="Screenshot 2026-01-13 133141" src="https://github.com/user-attachments/assets/3053b29e-0727-4473-8234-0a459916489e" />

<img width="1919" height="1019" alt="Screenshot 2026-01-13 133153" src="https://github.com/user-attachments/assets/21faf4c4-9064-4fda-a8df-2abbadbf841b" />

<img width="1919" height="1019" alt="Screenshot 2026-01-13 133228" src="https://github.com/user-attachments/assets/9b25e6c2-1241-444e-a0ef-deb258fbcc1f" />

