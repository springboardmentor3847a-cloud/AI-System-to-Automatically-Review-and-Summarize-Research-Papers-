"""
Research Paper Search Module 
===========================================
Implements automated paper search using Semantic Scholar API with:
- Query by topic
- Optional filters: year range, minimum citations, author name
- Comprehensive metadata extraction
- Error handling and retry logic
- Logging for debugging and monitoring
- Progress tracking
"""

import json
import os
import logging
import time
from typing import List, Dict, Optional, Any
from semanticscholar import SemanticScholar
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/search_papers.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

# Initialize Semantic Scholar client
sch = SemanticScholar(api_key=API_KEY, timeout=30)


def search_papers(
    topic: str,
    limit: int = 10,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    min_citations: Optional[int] = None,
    author: Optional[str] = None,
    fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Search for research papers using Semantic Scholar API.
    
    Args:
        topic: Search query/topic
        limit: Maximum number of papers to retrieve (default: 10)
        year_min: Minimum publication year filter (optional)
        year_max: Maximum publication year filter (optional)
        min_citations: Minimum citation count filter (optional)
        author: Filter by author name (optional)
        fields: Additional fields to retrieve (optional)
    
    Returns:
        Dictionary containing topic and list of paper metadata
    
    Raises:
        Exception: If API request fails after retries
    """
    logger.info(f"Starting paper search for topic: '{topic}' (limit={limit})")
    
    # Default fields to retrieve
    if fields is None:
        fields = [
            'title', 'abstract', 'year', 'authors', 'citationCount',
            'paperId', 'url', 'openAccessPdf', 'publicationDate',
            'venue', 'publicationTypes', 'externalIds', 'influentialCitationCount'
        ]
    
    # Build search query with filters
    query = topic
    if author:
        query += f" author:{author}"
    
    papers = []
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            logger.info(f"Attempting API request (attempt {retry_count + 1}/{max_retries})")
            
            # Execute search
            results = sch.search_paper(
                query,
                limit=limit * 2,  # Get more results for filtering
                fields=fields
            )
            
            # Process and filter results
            for paper in results:
                # Apply filters
                if year_min and (not paper.year or paper.year < year_min):
                    continue
                if year_max and (not paper.year or paper.year > year_max):
                    continue
                if min_citations and (not paper.citationCount or paper.citationCount < min_citations):
                    continue
                
                # Extract comprehensive metadata
                # Convert publication_date to string if it's a datetime object
                pub_date = getattr(paper, 'publicationDate', None)
                if pub_date and hasattr(pub_date, 'isoformat'):
                    pub_date = pub_date.isoformat()
                elif pub_date:
                    pub_date = str(pub_date)
                
                paper_data = {
                    "title": paper.title or "N/A",
                    "abstract": paper.abstract or "N/A",
                    "authors": [author.name if hasattr(author, 'name') else str(author) for author in (paper.authors or [])],
                    "year": paper.year,
                    "citation_count": paper.citationCount or 0,
                    "influential_citation_count": getattr(paper, 'influentialCitationCount', 0),
                    "paper_id": paper.paperId,
                    "url": paper.url,
                    "pdf_url": paper.openAccessPdf.get('url') if paper.openAccessPdf else None,
                    "publication_date": pub_date,
                    "venue": getattr(paper, 'venue', None),
                    "publication_types": getattr(paper, 'publicationTypes', []),
                    "external_ids": getattr(paper, 'externalIds', {}),
                    "pdf_available": bool(paper.openAccessPdf)
                }
                
                papers.append(paper_data)
                
                # Stop if we have enough papers
                if len(papers) >= limit:
                    break
            
            logger.info(f"Successfully retrieved {len(papers)} papers")
            break
            
        except Exception as e:
            retry_count += 1
            logger.warning(f"API request failed (attempt {retry_count}/{max_retries}): {str(e)}")
            
            if retry_count >= max_retries:
                logger.error(f"All retry attempts failed. Error: {str(e)}")
                raise Exception(f"Failed to search papers after {max_retries} attempts: {str(e)}")
            
            # Exponential backoff
            wait_time = 2 ** retry_count
            logger.info(f"Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
    
    result = {
        "topic": topic,
        "search_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "filters": {
            "year_min": year_min,
            "year_max": year_max,
            "min_citations": min_citations,
            "author": author
        },
        "total_papers": len(papers),
        "papers": papers
    }
    
    return result


def save_metadata(data: Dict[str, Any], path: str = "data/metadata/paper_metadata.json") -> None:
    """
    Save paper metadata to JSON file.
    
    Args:
        data: Dictionary containing paper metadata
        path: Output file path (default: data/metadata/paper_metadata.json)
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Metadata saved successfully to {path}")
    except Exception as e:
        logger.error(f"Failed to save metadata: {str(e)}")
        raise


def display_papers(papers: List[Dict[str, Any]]) -> None:
    """
    Display paper information in a readable format.
    
    Args:
        papers: List of paper metadata dictionaries
    """
    print("\n" + "="*80)
    print(f"Found {len(papers)} papers")
    print("="*80 + "\n")
    
    for idx, paper in enumerate(papers, 1):
        print(f"{idx}. {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'][:3])}" + (" et al." if len(paper['authors']) > 3 else ""))
        print(f"   Year: {paper['year']} | Citations: {paper['citation_count']}")
        print(f"   PDF Available: {'✓' if paper['pdf_available'] else '✗'}")
        if paper['abstract'] != "N/A":
            abstract_preview = paper['abstract'][:150] + "..." if len(paper['abstract']) > 150 else paper['abstract']
            print(f"   Abstract: {abstract_preview}")
        print()


# Demo and testing
if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("data/logs", exist_ok=True)
    
    # Example 1: Basic search
    print("Example 1: Basic Search")
    topic = "machine learning interpretability"
    data = search_papers(topic, limit=5)
    save_metadata(data)
    display_papers(data['papers'])
    
    # Example 2: Advanced search with filters
    print("\n" + "="*80)
    print("Example 2: Advanced Search with Filters")
    print("="*80)
    data_filtered = search_papers(
        topic="deep learning computer vision",
        limit=5,
        year_min=2020,
        min_citations=50
    )
    save_metadata(data_filtered, "data/metadata/filtered_papers.json")
    display_papers(data_filtered['papers'])
    
    print("\nSearch completed successfully!")
    print(f"Metadata saved to: data/metadata/paper_metadata.json")
