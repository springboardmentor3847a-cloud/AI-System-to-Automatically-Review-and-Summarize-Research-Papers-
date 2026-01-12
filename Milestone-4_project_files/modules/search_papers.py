"""
Research Paper Search Module 
===========================================
Implements automated paper search using Semantic Scholar API with:
- Query by topic
- Optional filters: year range, minimum citations, author name
- Comprehensive metadata extraction
- **WEIGHTED RANKING SYSTEM** for paper selection:
  - Topical relevance (w1)
  - Publication recency (w2)
  - Citation count (w3)
  - Author reputation (w4)
  - PDF availability (w5)
- Error handling and retry logic
- Logging for debugging and monitoring
- Progress tracking
"""

import json
import os
import logging
import time
import math
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from semanticscholar import SemanticScholar
from dotenv import load_dotenv

# Configure logging
os.makedirs("data/logs", exist_ok=True)
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
# Tunables via environment
SEM_SCH_TIMEOUT = int(os.getenv("SEMANTIC_SCHOLAR_TIMEOUT", "12"))
SEM_SCH_MAX_RETRIES = int(os.getenv("SEMANTIC_SCHOLAR_MAX_RETRIES", "2"))
USE_CACHED_ON_FAILURE = os.getenv("USE_CACHED_METADATA_ON_FAILURE", "1") == "1"

# Initialize Semantic Scholar client with configurable timeout
sch = SemanticScholar(api_key=API_KEY, timeout=SEM_SCH_TIMEOUT)

# =============================================================================
# RANKING WEIGHTS - Configurable scoring parameters
# =============================================================================
RANKING_WEIGHTS = {
    "relevance": 0.30,      # w1: Topical relevance (title + abstract matching)
    "recency": 0.20,        # w2: Publication recency (newer = better)
    "citations": 0.25,      # w3: Citation count (normalized)
    "author_score": 0.10,   # w4: Author reputation (h-index proxy)
    "pdf_available": 0.15   # w5: PDF availability bonus
}

# Normalization constants
CURRENT_YEAR = datetime.now().year
MAX_RECENCY_YEARS = 10  # Papers older than this get minimum recency score
MAX_CITATIONS_NORM = 1000  # Citation count normalization ceiling


def calculate_relevance_score(paper: Dict[str, Any], query_terms: List[str]) -> float:
    """
    Calculate topical relevance score based on query term matching in title and abstract.
    
    Args:
        paper: Paper metadata dictionary
        query_terms: List of search query terms (lowercased)
    
    Returns:
        Relevance score between 0.0 and 1.0
    """
    title = (paper.get("title") or "").lower()
    abstract = (paper.get("abstract") or "").lower()
    
    if not query_terms:
        return 0.5  # Neutral score if no query terms
    
    title_matches = sum(1 for term in query_terms if term in title)
    abstract_matches = sum(1 for term in query_terms if term in abstract)
    
    # Title matches weighted higher (2x)
    title_score = min(1.0, (title_matches * 2) / len(query_terms))
    abstract_score = min(1.0, abstract_matches / len(query_terms))
    
    # Combined relevance (60% title, 40% abstract)
    relevance = 0.6 * title_score + 0.4 * abstract_score
    return round(relevance, 4)


def calculate_recency_score(year: Optional[int]) -> float:
    """
    Calculate recency score - newer papers score higher.
    
    Args:
        year: Publication year
    
    Returns:
        Recency score between 0.0 and 1.0
    """
    if not year:
        return 0.3  # Low score for unknown year
    
    years_old = CURRENT_YEAR - year
    if years_old <= 0:
        return 1.0  # Current or future year (preprints)
    elif years_old >= MAX_RECENCY_YEARS:
        return 0.1  # Minimum score for old papers
    else:
        # Linear decay with floor
        score = 1.0 - (years_old / MAX_RECENCY_YEARS) * 0.9
        return round(max(0.1, score), 4)


def calculate_citation_score(citation_count: Optional[int]) -> float:
    """
    Calculate normalized citation score using logarithmic scaling.
    
    Args:
        citation_count: Number of citations
    
    Returns:
        Citation score between 0.0 and 1.0
    """
    if not citation_count or citation_count <= 0:
        return 0.0
    
    # Logarithmic normalization to handle wide citation ranges
    log_citations = math.log10(citation_count + 1)
    log_max = math.log10(MAX_CITATIONS_NORM + 1)
    
    score = min(1.0, log_citations / log_max)
    return round(score, 4)


def calculate_author_score(authors: List[Any], influential_citations: int = 0) -> float:
    """
    Calculate author reputation score based on:
    - Number of authors (collaborative research indicator)
    - Influential citation count (if available)
    
    Args:
        authors: List of author objects/names
        influential_citations: Number of influential citations
    
    Returns:
        Author score between 0.0 and 1.0
    """
    if not authors:
        return 0.2  # Low score for missing author info
    
    # Base score from author count (collaborative research is valued)
    author_count = len(authors)
    if author_count >= 3:
        collab_score = 0.6
    elif author_count >= 2:
        collab_score = 0.5
    else:
        collab_score = 0.4
    
    # Bonus for influential citations (proxy for author impact)
    if influential_citations:
        influence_bonus = min(0.4, influential_citations * 0.05)
    else:
        influence_bonus = 0.0
    
    return round(min(1.0, collab_score + influence_bonus), 4)


def calculate_paper_score(paper: Dict[str, Any], query_terms: List[str]) -> Tuple[float, Dict[str, float]]:
    """
    Calculate overall paper ranking score using weighted criteria.
    
    Formula: score = w1*relevance + w2*recency + w3*citations + w4*author_score + w5*pdf_available
    
    Args:
        paper: Paper metadata dictionary
        query_terms: List of search query terms
    
    Returns:
        Tuple of (total_score, component_scores_dict)
    """
    w = RANKING_WEIGHTS
    
    # Calculate individual component scores
    relevance = calculate_relevance_score(paper, query_terms)
    recency = calculate_recency_score(paper.get("year"))
    citations = calculate_citation_score(paper.get("citation_count"))
    author_score = calculate_author_score(
        paper.get("authors", []),
        paper.get("influential_citation_count", 0)
    )
    pdf_score = 1.0 if paper.get("pdf_available") else 0.0
    
    # Weighted sum
    total_score = (
        w["relevance"] * relevance +
        w["recency"] * recency +
        w["citations"] * citations +
        w["author_score"] * author_score +
        w["pdf_available"] * pdf_score
    )
    
    component_scores = {
        "relevance": relevance,
        "recency": recency,
        "citations": citations,
        "author_score": author_score,
        "pdf_available": pdf_score,
        "total": round(total_score, 4)
    }
    
    return round(total_score, 4), component_scores


def rank_papers(papers: List[Dict[str, Any]], query: str, top_n: int = 3) -> List[Dict[str, Any]]:
    """
    Rank papers using weighted scoring and return top N papers.
    
    Args:
        papers: List of paper metadata dictionaries
        query: Original search query
        top_n: Number of top papers to select
    
    Returns:
        List of ranked papers with scores, sorted by rank
    """
    if not papers:
        return []
    
    # Extract query terms for relevance scoring
    query_terms = [term.lower().strip() for term in query.split() if len(term) > 2]
    
    # Calculate scores for all papers
    scored_papers = []
    for paper in papers:
        total_score, components = calculate_paper_score(paper, query_terms)
        paper_with_score = paper.copy()
        paper_with_score["ranking_score"] = total_score
        paper_with_score["score_breakdown"] = components
        scored_papers.append(paper_with_score)
    
    # Sort by total score (descending)
    scored_papers.sort(key=lambda x: x["ranking_score"], reverse=True)
    
    # Assign ranks
    for idx, paper in enumerate(scored_papers, 1):
        paper["rank"] = idx
    
    # Log ranking results
    logger.info("=" * 60)
    logger.info("PAPER RANKING RESULTS")
    logger.info("=" * 60)
    logger.info(f"Query: {query}")
    logger.info(f"Total papers scored: {len(scored_papers)}")
    logger.info(f"Top {top_n} papers:")
    
    for paper in scored_papers[:top_n]:
        logger.info(f"\n  Rank #{paper['rank']}: {paper.get('title', 'Unknown')[:60]}...")
        logger.info(f"    Total Score: {paper['ranking_score']:.4f}")
        breakdown = paper['score_breakdown']
        logger.info(f"    Breakdown - Relevance: {breakdown['relevance']:.3f}, "
                   f"Recency: {breakdown['recency']:.3f}, "
                   f"Citations: {breakdown['citations']:.3f}, "
                   f"Author: {breakdown['author_score']:.3f}, "
                   f"PDF: {breakdown['pdf_available']:.1f}")
    
    logger.info("=" * 60)
    
    # Return top N papers
    return scored_papers[:top_n] if top_n else scored_papers


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
    max_retries = max(1, SEM_SCH_MAX_RETRIES)
    
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
                # Do not raise here; allow cached fallback below
                papers = []
                break
            
            # Exponential backoff
            wait_time = 2 ** retry_count
            logger.info(f"Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)

    # If request ultimately failed but cached metadata exists and fallback enabled, use it
    if not papers and USE_CACHED_ON_FAILURE:
        try:
            cache_path = os.getenv("SEMANTIC_SCHOLAR_FALLBACK_PATH", "data/metadata/paper_metadata.json")
            if os.path.exists(cache_path):
                with open(cache_path, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                cached_papers = cached.get("papers", [])
                if cached_papers:
                    logger.warning(
                        "Search failed; falling back to cached metadata (%s papers)",
                        len(cached_papers)
                    )
                    papers = cached_papers[:limit]
        except Exception as fe:
            logger.warning(f"Failed to load cached metadata fallback: {fe}")
    
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


def display_papers(papers: List[Dict[str, Any]], show_ranking: bool = True) -> None:
    """
    Display paper information in a readable format with ranking scores.
    
    Args:
        papers: List of paper metadata dictionaries
        show_ranking: Whether to display ranking scores
    """
    print("\n" + "="*80)
    print(f"Found {len(papers)} papers")
    print("="*80 + "\n")
    
    for idx, paper in enumerate(papers, 1):
        rank_info = ""
        if show_ranking and "rank" in paper:
            rank_info = f" [RANK #{paper['rank']} | Score: {paper.get('ranking_score', 0):.3f}]"
        
        print(f"{idx}. {paper['title']}{rank_info}")
        print(f"   Authors: {', '.join(paper['authors'][:3])}" + (" et al." if len(paper['authors']) > 3 else ""))
        print(f"   Year: {paper['year']} | Citations: {paper['citation_count']}")
        print(f"   PDF Available: {'✓' if paper['pdf_available'] else '✗'}")
        
        # Show score breakdown if available
        if show_ranking and "score_breakdown" in paper:
            breakdown = paper["score_breakdown"]
            print(f"   Score Breakdown: Rel={breakdown['relevance']:.2f} | "
                  f"Rec={breakdown['recency']:.2f} | Cit={breakdown['citations']:.2f} | "
                  f"Auth={breakdown['author_score']:.2f} | PDF={breakdown['pdf_available']:.0f}")
        
        if paper['abstract'] != "N/A":
            abstract_preview = paper['abstract'][:150] + "..." if len(paper['abstract']) > 150 else paper['abstract']
            print(f"   Abstract: {abstract_preview}")
        print()


def get_ranking_weights() -> Dict[str, float]:
    """Return current ranking weights for transparency."""
    return RANKING_WEIGHTS.copy()


def set_ranking_weights(weights: Dict[str, float]) -> None:
    """
    Update ranking weights (must sum to approximately 1.0).
    
    Args:
        weights: Dictionary with keys: relevance, recency, citations, author_score, pdf_available
    """
    global RANKING_WEIGHTS
    total = sum(weights.values())
    if abs(total - 1.0) > 0.01:
        logger.warning(f"Ranking weights sum to {total}, expected ~1.0. Normalizing...")
        weights = {k: v/total for k, v in weights.items()}
    RANKING_WEIGHTS.update(weights)
    logger.info(f"Updated ranking weights: {RANKING_WEIGHTS}")


# Demo and testing
if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("data/logs", exist_ok=True)
    
    # Example 1: Basic search with ranking
    print("Example 1: Search with Weighted Ranking")
    print("="*80)
    topic = "machine learning interpretability"
    
    # Step 1: Search for papers
    data = search_papers(topic, limit=10)
    
    # Step 2: Rank papers and select top 3
    print("\nApplying weighted ranking algorithm...")
    print(f"Weights: {get_ranking_weights()}")
    
    ranked_papers = rank_papers(data['papers'], topic, top_n=3)
    
    # Step 3: Display ranked results
    display_papers(ranked_papers, show_ranking=True)
    
    # Save metadata with rankings
    data['papers'] = ranked_papers
    data['ranking_applied'] = True
    data['ranking_weights'] = get_ranking_weights()
    save_metadata(data)
    
    print("\n" + "="*80)
    print("Example 2: Advanced Search with Filters and Ranking")
    print("="*80)
    
    data_filtered = search_papers(
        topic="deep learning computer vision",
        limit=10,
        year_min=2020,
        min_citations=50
    )
    
    ranked_filtered = rank_papers(data_filtered['papers'], "deep learning computer vision", top_n=3)
    display_papers(ranked_filtered, show_ranking=True)
    
    # Save with rankings
    data_filtered['papers'] = ranked_filtered
    data_filtered['ranking_applied'] = True
    data_filtered['ranking_weights'] = get_ranking_weights()
    save_metadata(data_filtered, "data/metadata/filtered_papers.json")
    
    print("\nSearch and ranking completed successfully!")
    print(f"Metadata saved to: data/metadata/paper_metadata.json")
