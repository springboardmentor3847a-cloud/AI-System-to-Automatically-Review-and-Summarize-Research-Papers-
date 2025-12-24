# 🧠 Automated Research Paper Collection System  
### Infosys Springboard – Internship Project  

**Milestone:** 1 – Automated Paper Retrieval  
**Duration:** Week 1–2  

---

## 📌 Milestone Description
This milestone focuses on designing and implementing an automated system to search, retrieve, and organize research papers based on a user-defined topic.  
It forms the data foundation required for subsequent milestones involving text extraction, comparison, and summarization.

---

## 🎯 Milestone Objectives
- Automate research paper discovery using an academic API  
- Enable topic-based paper search  
- Download available open-access PDFs  
- Store paper metadata in a structured dataset  
- Prepare clean inputs for further processing stages  

---

## 🏗️ Implementation Highlights
- Topic-driven research paper search  
- User-controlled number of papers to fetch  
- Manual or automatic paper selection options  
- Robust PDF download handling with validation  
- Structured dataset generation in CSV format  

---

## ⚙️ Technologies Used
- Python 3.x  
- Semantic Scholar API  
- Requests  
- CSV / JSON handling  
- Logging for error tracking  

---

## 📁 Folder Structure
milestone-1/
│
├── data/
│ ├── pdfs/ # Downloaded research PDFs
│ └── dataset/
│ └── papers_dataset.csv # Metadata dataset
│
├── logs/
│ └── download.log # Error and download logs
│
├── milestone1.py # Main implementation script
└── README.md


---

## 📊 Dataset Details
Each record in the dataset includes:
- Paper title  
- Authors  
- Publication year  
- Venue  
- Citation count  
- Open-access availability  
- PDF download status  

---

## ✅ Output of Milestone 1
- A curated dataset of research paper metadata  
- Validated and downloadable PDF files stored locally  
- Logged errors for failed or unavailable downloads  

---

## 🔍 Key Design Decisions
- Only metadata-level processing (no PDF text parsing in this milestone)  
- Clear separation between search, selection, and download logic  
- Explicit tracking of download success to ensure transparency  
- Simple, readable, and mentor-friendly code structure  

---

## 🚀 Outcome
Milestone 1 successfully establishes a reliable and automated pipeline for collecting research papers, enabling smooth progression into Milestone 2 where text extraction and analysis are performed.

---


## 📁 Folder Structure
