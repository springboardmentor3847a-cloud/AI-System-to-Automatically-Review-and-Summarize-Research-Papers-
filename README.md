Milestone 1: Automated Research & Data Collection
Overview This milestone focuses on setting up the environment and automating the retrieval of academic papers. The system connects to the Semantic Scholar API to search, rank, and download relevant research papers based on user-defined topics.


Key Features

Automated Search: Queries the Semantic Scholar database for papers matching a specific topic.

Smart Ranking: Ranks papers based on recency, citation count, and PDF availability.

PDF Retrieval: Automatically downloads open-access PDFs to a local directory (data/pdfs).

Metadata Logging: Saves dataset metadata (titles, authors, years) for downstream processing.


Tech Stack

Language: Python 3.x 

Libraries: semanticscholar, requests, pandas.


Data Source: Semantic Scholar API.

Usage Instructions

Install Dependencies: Run the setup cells to install semanticscholar and other base libraries.

Configure Search:

Run the "Research Assistant" cell.

Input a Research Topic (e.g., "Machine Learning").

(Optional) Set filters for Minimum Year and Minimum Citations.

Output:

The system screens papers and selects the top candidates (default: 3).

PDFs are saved to data/pdfs/.

Milestone 2: Text Extraction & Analysis
Overview This milestone implements the analysis pipeline. It extracts raw text from the downloaded PDFs and uses Large Language Models (LLMs) to analyze findings and compare papers against one another.

Key Features

PDF Parsing: Utilizes pymupdf4llm to convert PDF content into Markdown-formatted text, optimized for LLM processing.

Individual Analysis: Extracts the main objective, methodology, key findings, and limitations from each paper.

Cross-Paper Comparison: Synthesizes data to identify common themes, methodological differences, and contradictions across the selected papers.

Tech Stack

Libraries: pymupdf4llm, langchain-groq, langchain-core.

Models: Llama-3.3-70b-versatile (via Groq API).

Input: PDFs located in data/pdfs/.

Usage Instructions

Extract Text: Run the TextExtractionModule to parse PDFs into text files stored in data/processed/.

Run Analysis: Execute the AnalysisModule.

Ensure the GROQ_API_KEY is set in the environment.

Output:

JSON file generated at data/analysis_results.json containing structured insights and the cross-paper synthesis.

Milestone 3: Draft Generation
Overview The objective of this milestone is to automatically generate a structured academic draft. The system uses the analysis data from Milestone 2 to write specific sections of a systematic review, including the Abstract, Methodology, and Results.
+1

Key Features

Automated Drafting: Generates cohesive text for the Abstract, Methodology Comparison, and Results & Discussion sections.

APA Formatting: Automatically formats references into APA style using the metadata collected in Milestone 1.

Report Compilation: Aggregates all sections into a single Markdown file (Final_Review_Draft.md).

Tech Stack

Libraries: langchain, json, os.

Logic: Uses prompt templates to guide the LLM in academic writing styles.

Usage Instructions

Prerequisites: Ensure data/analysis_results.json exists (from Milestone 2).

Generate Draft: Run the DraftGenerationModule cell.

Output:

A Markdown file is saved to data/drafts/Final_Review_Draft.md.

A preview of the draft is displayed directly in the notebook output.

Milestone 4: Review, Refinement & UI
Overview The final milestone implements a "human-in-the-loop" review cycle and a graphical user interface (GUI). It allows users to assess the quality of the generated draft, request AI-driven revisions, and export a final polished report.
+2

Key Features

Quality Assessment: An AI agent evaluates the draft for coherence, accuracy, clarity, and rigor, providing a score out of 10.

Interactive UI: A Streamlit-based web interface allows users to view the draft, run assessments, and modify suggestions.

Revision Cycle: Users can trigger an AI revision process based on specific critiques.


Final Export: Generates a comprehensive final report including quality metrics and the revised content.

Tech Stack


Framework: Streamlit.

Tunneling: localtunnel (to expose the UI from Colab).

Files: Generates app.py dynamically.

Usage Instructions

Write App: Run the cell containing %%writefile app.py to create the Streamlit application file.

Launch Server: Run the final cell to install Streamlit and start the server.

Access UI:

Copy the IP address printed in the output (e.g., from ipv4.icanhazip.com).

Click the loca.lt link provided in the output.

Paste the IP address to bypass the tunnel security page.

Workflow:

Tab 1: Load the draft generated in Milestone 3.

Tab 2: Click "Run Quality Assessment" to see scores and issues.

Tab 3: Review suggestions and click "Apply AI Revisions".

Tab 4: Download the final report.

The Final Output

<img width="1919" height="1022" alt="Screenshot 2026-01-13 133124" src="https://github.com/user-attachments/assets/4b1580f2-74be-4dab-89c8-a83c0d326e34" />

<img width="1919" height="1022" alt="Screenshot 2026-01-13 133141" src="https://github.com/user-attachments/assets/3053b29e-0727-4473-8234-0a459916489e" />

<img width="1919" height="1019" alt="Screenshot 2026-01-13 133153" src="https://github.com/user-attachments/assets/21faf4c4-9064-4fda-a8df-2abbadbf841b" />

<img width="1919" height="1019" alt="Screenshot 2026-01-13 133228" src="https://github.com/user-attachments/assets/9b25e6c2-1241-444e-a0ef-deb258fbcc1f" />

