"""
PDF Download Module 
==================================
Implements PDF download functionality with:
- Download papers from URLs
- Save PDFs to data/pdfs/
- Validate downloaded files
- Store metadata in JSON format
- Progress tracking with tqdm
- Error handling and retry logic
- Logging
"""

import os
import json
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any
import requests
from tqdm import tqdm
from dotenv import load_dotenv
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/download_pdf.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
PDF_DIR = "data/pdfs"
METADATA_DIR = "data/metadata"
CHUNK_SIZE = 8192  # 8KB chunks for download
MAX_RETRIES = 3
TIMEOUT = 30  # seconds
MAX_HTML_SNIFF = 200000  # cap HTML reads when looking for fallback PDF links


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove invalid characters.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename


def validate_pdf(filepath: str) -> bool:
    """
    Validate that the downloaded file is a valid PDF.
    
    Args:
        filepath: Path to the PDF file
    
    Returns:
        True if valid PDF, False otherwise
    """
    try:
        # Check file exists and has content
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            logger.warning(f"File does not exist or is empty: {filepath}")
            return False
        
        # Check PDF magic number (starts with %PDF)
        with open(filepath, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                logger.warning(f"File does not have PDF header: {filepath}")
                return False
        
        logger.info(f"PDF validation successful: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Error validating PDF {filepath}: {str(e)}")
        return False


def _is_probable_pdf_response(response: requests.Response) -> bool:
    content_type = response.headers.get("content-type", "").lower()
    if "pdf" in content_type:
        return True
    disp = response.headers.get("content-disposition", "").lower()
    return "pdf" in disp


def _expand_candidate_urls(url: str) -> List[str]:
    """Return a list of candidate PDF URLs with simple heuristics (e.g., arXiv abs→pdf)."""
    candidates = [url]
    if "arxiv.org/abs/" in url:
        pdf_url = url.replace("/abs/", "/pdf/")
        if not pdf_url.lower().endswith(".pdf"):
            pdf_url += ".pdf"
        candidates.append(pdf_url)
    # Deduplicate while preserving order
    seen = set()
    ordered = []
    for u in candidates:
        if u not in seen:
            ordered.append(u)
            seen.add(u)
    return ordered


def _extract_pdf_link_from_html(html: str, base_url: str) -> Optional[str]:
    """Find a likely PDF link in HTML by looking for hrefs ending with .pdf."""
    import re  # local import to avoid global dependency for non-HTML paths

    match = re.search(r'href=["\']([^"\']+\.pdf)["\']', html, re.IGNORECASE)
    if match:
        href = match.group(1)
        return urljoin(base_url, href)
    return None


def download_pdf(
    url: str,
    paper_id: str,
    title: str,
    output_dir: str = PDF_DIR
) -> Optional[str]:
    """
    Download a single PDF from URL with retry logic.
    
    Args:
        url: PDF download URL
        paper_id: Unique paper identifier
        title: Paper title (used for filename)
        output_dir: Directory to save PDF (default: data/pdfs/)
    
    Returns:
        Path to downloaded PDF file, or None if download failed
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    safe_title = sanitize_filename(title)
    filename = f"{paper_id}_{safe_title}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Check if already downloaded
    if os.path.exists(filepath) and validate_pdf(filepath):
        logger.info(f"PDF already exists: {filepath}")
        return filepath
    
    candidate_urls = _expand_candidate_urls(url)
    tried: set[str] = set()
    attempt = 0

    while candidate_urls and attempt < MAX_RETRIES:
        current_url = candidate_urls.pop(0)
        if current_url in tried:
            continue
        tried.add(current_url)
        attempt += 1

        try:
            logger.info(f"Downloading PDF (attempt {attempt}/{MAX_RETRIES}): {current_url}")

            response = requests.get(
                current_url,
                stream=True,
                timeout=TIMEOUT,
                headers={'User-Agent': 'Mozilla/5.0'},
            )
            response.raise_for_status()

            # If the response is HTML, sniff for a PDF link and retry it.
            if not _is_probable_pdf_response(response):
                content_type = response.headers.get("content-type", "").lower()
                if "text/html" in content_type:
                    try:
                        html = response.content[:MAX_HTML_SNIFF].decode(errors="ignore")
                        fallback_pdf = _extract_pdf_link_from_html(html, current_url)
                        if fallback_pdf and fallback_pdf not in tried and fallback_pdf not in candidate_urls:
                            logger.info("Found fallback PDF link in HTML: %s", fallback_pdf)
                            candidate_urls.insert(0, fallback_pdf)
                            continue
                    except Exception as sniff_exc:
                        logger.warning("HTML sniff failed for %s: %s", current_url, sniff_exc)
                logger.warning(f"Response is not a PDF for: {current_url}")
                continue

            # Get total file size
            total_size = int(response.headers.get('content-length', 0))
            
            # Download with progress bar
            with open(filepath, 'wb') as f, tqdm(
                desc=f"Downloading {safe_title[:50]}",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
            
            # Validate downloaded PDF
            if validate_pdf(filepath):
                logger.info(f"Successfully downloaded PDF: {filepath}")
                return filepath
            else:
                logger.warning(f"Downloaded file is not a valid PDF: {filepath}")
                if os.path.exists(filepath):
                    os.remove(filepath)
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Download attempt {attempt} failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error downloading PDF: {str(e)}")

        if attempt < MAX_RETRIES:
            wait_time = 2 ** attempt
            logger.info(f"Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
        else:
            logger.error(f"All download attempts failed for: {url}")
    
    return None


def download_papers(
    papers: List[Dict[str, Any]],
    output_dir: str = PDF_DIR
) -> List[Dict[str, Any]]:
    """
    Download multiple papers and track results.
    
    Args:
        papers: List of paper metadata dictionaries (must include pdf_url)
        output_dir: Directory to save PDFs
    
    Returns:
        List of successfully downloaded paper metadata with pdf_path added
    """
    logger.info(f"Starting batch download of {len(papers)} papers")
    
    downloaded_papers = []
    failed_downloads = []
    
    for idx, paper in enumerate(papers, 1):
        print(f"\n[{idx}/{len(papers)}] Processing: {paper.get('title', 'Unknown')[:60]}...")
        
        pdf_url = paper.get('pdf_url')
        if not pdf_url:
            logger.warning(f"No PDF URL available for paper: {paper.get('title')}")
            failed_downloads.append(paper)
            continue
        
        # Download PDF
        pdf_path = download_pdf(
            url=pdf_url,
            paper_id=paper.get('paper_id', f'unknown_{idx}'),
            title=paper.get('title', f'paper_{idx}'),
            output_dir=output_dir
        )
        
        if pdf_path:
            # Add PDF path to paper metadata
            paper['pdf_path'] = pdf_path
            paper['download_status'] = 'success'
            paper['download_date'] = time.strftime("%Y-%m-%d %H:%M:%S")
            downloaded_papers.append(paper)
        else:
            paper['download_status'] = 'failed'
            failed_downloads.append(paper)
    
    # Summary
    print("\n" + "="*80)
    print(f"Download Summary:")
    print(f"  Total papers: {len(papers)}")
    print(f"  Successfully downloaded: {len(downloaded_papers)}")
    print(f"  Failed: {len(failed_downloads)}")
    print("="*80)
    
    logger.info(f"Batch download complete. Success: {len(downloaded_papers)}, Failed: {len(failed_downloads)}")
    
    return downloaded_papers


def save_download_metadata(
    papers: List[Dict[str, Any]],
    filename: str = "selected_papers.json"
) -> str:
    """
    Save metadata of downloaded papers to JSON file.
    
    Args:
        papers: List of paper metadata dictionaries
        filename: Output filename (default: selected_papers.json)
    
    Returns:
        Path to saved metadata file
    """
    os.makedirs(METADATA_DIR, exist_ok=True)
    filepath = os.path.join(METADATA_DIR, filename)
    
    metadata = {
        "download_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_papers": len(papers),
        "papers": papers
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Metadata saved successfully to: {filepath}")
        print(f"\nMetadata saved to: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Failed to save metadata: {str(e)}")
        raise


def load_metadata(filepath: str) -> Dict[str, Any]:
    """
    Load paper metadata from JSON file.
    
    Args:
        filepath: Path to metadata JSON file
    
    Returns:
        Dictionary containing paper metadata
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Metadata loaded successfully from: {filepath}")
        return data
    except Exception as e:
        logger.error(f"Failed to load metadata from {filepath}: {str(e)}")
        raise


def get_pdf_info(filepath: str) -> Dict[str, Any]:
    """
    Get information about a PDF file.
    
    Args:
        filepath: Path to PDF file
    
    Returns:
        Dictionary with file size, hash, etc.
    """
    try:
        file_size = os.path.getsize(filepath)
        
        # Calculate MD5 hash
        md5_hash = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hash.update(chunk)
        
        return {
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "md5_hash": md5_hash.hexdigest(),
            "is_valid": validate_pdf(filepath)
        }
    except Exception as e:
        logger.error(f"Error getting PDF info for {filepath}: {str(e)}")
        return {}


# Demo and testing
if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(METADATA_DIR, exist_ok=True)
    
    # Example: Load papers from search results and download
    search_metadata_path = "data/metadata/paper_metadata.json"
    
    if os.path.exists(search_metadata_path):
        print("Loading papers from search results...")
        with open(search_metadata_path, 'r', encoding='utf-8') as f:
            search_data = json.load(f)
        
        papers = search_data.get('papers', [])
        
        # Filter papers with available PDFs
        papers_with_pdf = [p for p in papers if p.get('pdf_available')]
        
        print(f"\nFound {len(papers_with_pdf)} papers with available PDFs")
        
        if papers_with_pdf:
            # Download papers
            downloaded = download_papers(papers_with_pdf)
            
            # Save metadata
            if downloaded:
                save_download_metadata(downloaded, "selected_papers.json")
                
                # Display some info
                print("\nDownloaded papers:")
                for paper in downloaded[:3]:
                    print(f"  - {paper['title']}")
                    print(f"    PDF: {paper['pdf_path']}")
                    pdf_info = get_pdf_info(paper['pdf_path'])
                    print(f"    Size: {pdf_info.get('file_size_mb', 'N/A')} MB")
                    print()
    else:
        print(f"No search results found at {search_metadata_path}")
        print("Run search_papers.py first to generate paper metadata.")

