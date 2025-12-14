### Milestone 1: Automated Paper Search
- **Overview**

This milestone implements a simple pipeline to search research papers on a given topic using the Semantic Scholar API and collects metadata including title, authors, year, citations, venue, abstract, and PDF availability.

- **Features**

Input any research topic to search papers.

Collects and saves paper metadata in JSON format (data/search_results/).

Displays paper details (title, year, citations, PDF availability) in the notebook.

Limited number of papers fetched to ensure fast execution.

Uses public API access for reliability.

- **How to Run**

Ensure semanticscholar is installed:

pip install semanticscholar


Open the file and run all cells.

Enter a topic when prompted.

Results are displayed and saved automatically.

- **Output Screenshot**

![Example Output](Milestone1/ScreenshotMilestone1.png)
