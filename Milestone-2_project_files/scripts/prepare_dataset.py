"""
Dataset Preparation Script - Milestone 1
=========================================
Creates selected_papers.json with complete metadata for analysis.
This script combines search and download results into a unified dataset.
"""

import os
import json
import sys
from typing import List, Dict, Any

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Change to parent directory for relative file paths
os.chdir(parent_dir)

from modules.search_papers import search_papers, save_metadata, display_papers
from modules.download_pdf import download_papers, save_download_metadata


def create_dataset(
    topic: str,
    limit: int = 10,
    year_min: int = None,
    min_citations: int = None,
    download_pdfs: bool = True
) -> Dict[str, Any]:
    """
    Complete workflow: Search papers, download PDFs, create dataset.
    
    Args:
        topic: Research topic to search
        limit: Maximum number of papers
        year_min: Minimum publication year filter
        min_citations: Minimum citation count filter
        download_pdfs: Whether to download PDFs (default: True)
    
    Returns:
        Dictionary with dataset statistics
    """
    print("="*80)
    print("MILESTONE 1: DATASET PREPARATION")
    print("="*80)
    
    # Step 1: Search for papers
    print(f"\nStep 1: Searching for papers on '{topic}'...")
    search_results = search_papers(
        topic=topic,
        limit=limit,
        year_min=year_min,
        min_citations=min_citations
    )
    
    # Display search results
    display_papers(search_results['papers'])
    
    # Save search metadata
    save_metadata(search_results, "data/metadata/paper_metadata.json")
    
    # Step 2: Filter papers with available PDFs
    papers_with_pdf = [p for p in search_results['papers'] if p.get('pdf_available')]
    
    print(f"\nStep 2: Found {len(papers_with_pdf)}/{len(search_results['papers'])} papers with available PDFs")
    
    # Step 3: Download PDFs
    downloaded_papers = []
    if download_pdfs and papers_with_pdf:
        print(f"\nStep 3: Downloading PDFs...")
        downloaded_papers = download_papers(papers_with_pdf)
        
        # Step 4: Extract text from PDFs
        if downloaded_papers:
            print(f"\nStep 4: Extracting text from PDFs...")
            from modules.extract_text import extract_text_for_papers

            downloaded_papers = extract_text_for_papers(
                downloaded_papers,
                output_dir="data/extracted"
            )

            # Save downloaded papers metadata with extraction details
            save_download_metadata(downloaded_papers, "selected_papers.json")

            # Step 5: Analyze extracted text
            print(f"\nStep 5: Analyzing extracted text...")
            from modules.analyze_text import process_analysis

            analysis_summary = process_analysis(
                metadata_path="data/metadata/selected_papers.json",
                output_path="data/metadata/analyzed_papers.json",
            )
            print(f"Analysis complete. Success: {analysis_summary.get('success', 0)} / {analysis_summary.get('total', 0)}")

            # Step 6: Generate drafts
            print(f"\nStep 6: Generating drafts...")
            from modules.generate_draft import generate_drafts

            drafts_summary = generate_drafts(
                metadata_path="data/metadata/selected_papers.json",
                analysis_path="data/metadata/analyzed_papers.json",
                output_path="data/metadata/drafts.json",
            )
            print(f"Drafts generated: {drafts_summary.get('total', 0)}")

            # Step 7: Critique drafts
            print(f"\nStep 7: Critiquing drafts...")
            from modules.critique_draft import critique_drafts

            critiques_summary = critique_drafts(
                drafts_path="data/metadata/drafts.json",
                output_path="data/metadata/critiques.json",
            )
            print(f"Critiques generated: {critiques_summary.get('total', 0)}")
    else:
        print("\nStep 3: Skipping PDF download")
        downloaded_papers = papers_with_pdf
    
    # Step 4: Generate final dataset statistics
    print("\n" + "="*80)
    print("DATASET PREPARATION COMPLETE")
    print("="*80)
    
    stats = {
        "topic": topic,
        "total_papers_found": len(search_results['papers']),
        "papers_with_pdf": len(papers_with_pdf),
        "successfully_downloaded": len(downloaded_papers),
        "extraction_success": len([p for p in downloaded_papers if p.get('extraction_status') == 'success']),
        "analysis_success": None,
        "drafts_total": None,
        "critiques_total": None,
        "dataset_file": "data/metadata/selected_papers.json"
    }

    # Populate analysis stats if analysis was run
    if os.path.exists("data/metadata/analyzed_papers.json"):
        try:
            with open("data/metadata/analyzed_papers.json", "r", encoding="utf-8") as f:
                analysis_data = json.load(f)
            stats["analysis_success"] = analysis_data.get("success")
            stats["analysis_total"] = analysis_data.get("total")
            stats["analysis_output"] = "data/metadata/analyzed_papers.json"
        except Exception:
            stats["analysis_success"] = "error"
            stats["analysis_total"] = None
            stats["analysis_output"] = None

    # Populate draft stats if drafts were generated
    if os.path.exists("data/metadata/drafts.json"):
        try:
            with open("data/metadata/drafts.json", "r", encoding="utf-8") as f:
                drafts_data = json.load(f)
            stats["drafts_total"] = drafts_data.get("total")
            stats["drafts_output"] = "data/metadata/drafts.json"
        except Exception:
            stats["drafts_total"] = "error"
            stats["drafts_output"] = None

    # Populate critique stats if critiques were generated
    if os.path.exists("data/metadata/critiques.json"):
        try:
            with open("data/metadata/critiques.json", "r", encoding="utf-8") as f:
                crit_data = json.load(f)
            stats["critiques_total"] = crit_data.get("total")
            stats["critiques_output"] = "data/metadata/critiques.json"
        except Exception:
            stats["critiques_total"] = "error"
            stats["critiques_output"] = None
    
    print(f"\nDataset Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\nDataset ready for analysis!")
    print(f"Next steps: Run text extraction (extract_text.py) on downloaded PDFs")
    
    return stats


def validate_dataset(filepath: str = "data/metadata/selected_papers.json") -> None:
    """
    Validate the generated dataset.
    
    Args:
        filepath: Path to selected_papers.json
    """
    print("\n" + "="*80)
    print("DATASET VALIDATION")
    print("="*80)
    
    if not os.path.exists(filepath):
        print(f"❌ Dataset file not found: {filepath}")
        return
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        papers = data.get('papers', [])
        
        print(f"\n✅ Dataset file found: {filepath}")
        print(f"✅ Total papers: {len(papers)}")
        
        # Check required fields
        required_fields = [
            'title', 'authors', 'abstract', 'year', 'citation_count',
            'pdf_path', 'paper_id'
        ]
        
        missing_fields = []
        for paper in papers:
            for field in required_fields:
                if field not in paper:
                    missing_fields.append(field)
        
        if missing_fields:
            print(f"⚠️  Some papers missing fields: {set(missing_fields)}")
        else:
            print(f"✅ All required fields present in all papers")
        
        # Check PDF files exist
        pdfs_exist = 0
        for paper in papers:
            if 'pdf_path' in paper and os.path.exists(paper['pdf_path']):
                pdfs_exist += 1
        
        print(f"✅ PDF files found: {pdfs_exist}/{len(papers)}")
        
        # Display sample paper
        if papers:
            print(f"\nSample paper entry:")
            sample = papers[0]
            print(f"  Title: {sample.get('title', 'N/A')}")
            print(f"  Authors: {', '.join(sample.get('authors', [])[:3])}")
            print(f"  Year: {sample.get('year', 'N/A')}")
            print(f"  Citations: {sample.get('citation_count', 'N/A')}")
            print(f"  PDF Path: {sample.get('pdf_path', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error validating dataset: {str(e)}")


# Main execution
if __name__ == "__main__":
    # Ensure required directories exist
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/pdfs", exist_ok=True)
    os.makedirs("data/metadata", exist_ok=True)
    
    # Configuration - to modify this section as needed
    RESEARCH_TOPIC = "deep learning natural language processing"#To change search topic can change here
    MAX_PAPERS = 10
    MIN_YEAR = 2020
    MIN_CITATIONS = 50
    
    print("\nConfiguration:")
    print(f"  Research Topic: {RESEARCH_TOPIC}")
    print(f"  Maximum Papers: {MAX_PAPERS}")
    print(f"  Minimum Year: {MIN_YEAR}")
    print(f"  Minimum Citations: {MIN_CITATIONS}")
    
    # Create dataset
    try:
        stats = create_dataset(
            topic=RESEARCH_TOPIC,
            limit=MAX_PAPERS,
            year_min=MIN_YEAR,
            min_citations=MIN_CITATIONS,
            download_pdfs=True
        )
        
        # Validate dataset
        validate_dataset()
        
    except Exception as e:
        print(f"\n❌ Error during dataset preparation: {str(e)}")
        import traceback
        traceback.print_exc()
