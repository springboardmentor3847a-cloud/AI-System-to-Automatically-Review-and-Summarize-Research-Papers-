📍 Milestone 2 – PDF Text Extraction & Analysis

📌 Overview
Milestone 2 focuses on extracting text from research paper PDFs collected in Milestone 1 and converting them into structured and analyzable data for further processing.

🎯 Objectives

1. Extract complete text from research paper PDFs
2. Clean and normalize the extracted content
3. Identify standard research paper sections
4. Extract important keywords from each paper
5. Perform keyword comparison across multiple papers

🧠 Key Features

1. Automatic detection of PDF files
2. Page-wise PDF text extraction
3. Text cleaning using regular expressions
4. Section-wise extraction (Abstract, Introduction, Methodology, Results, Conclusion)
5. Keyword extraction using frequency analysis and stopword removal
6. Cross-paper keyword overlap analysis

🛠️ Tech Stack

1. Python
2. pdfplumber
3. Regular Expressions (re)
4. scikit-learn (English Stopwords)
5. JSON and CSV

📂 Input & Output

📥 Input:
Research paper PDFs generated in Milestone 1

📤 Output:

1. JSON files containing structured paper data
2. CSV file showing keyword overlap between papers
3. CSV file summarizing word statistics of each paper

▶️ Execution Flow

1. Load PDFs from the input directory
2. Extract and clean text from each PDF
3. Detect paper sections
4. Extract keywords and statistics
5. Save structured data as JSON
6. Compare keywords across papers

✅ Status
Completed successfully and ready for Milestone 3 (Summarization)

🔚 Closing Line
Milestone 2 converts unstructured research PDFs into structured data and performs keyword-based analysis to support automated research paper review and summarization.
