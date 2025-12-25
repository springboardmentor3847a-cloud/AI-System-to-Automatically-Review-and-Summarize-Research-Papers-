"""
PDF Text Extraction Module
==========================
Extract text from downloaded PDFs and store plain-text files under data/extracted.
Updates paper metadata entries with text extraction details.
"""

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

# Third-party imports are optional at runtime; fallbacks are handled gracefully
try:
	import pymupdf4llm  # type: ignore
except Exception:  # pragma: no cover - handled at call time
	pymupdf4llm = None  # fallback detected later

try:
	import fitz  # type: ignore
except Exception:  # pragma: no cover - handled at call time
	fitz = None


# Paths
LOG_DIR = "data/logs"
EXTRACTED_DIR = "data/extracted"
METADATA_PATH = "data/metadata/selected_papers.json"
USE_PYMUPDF_LAYOUT = os.getenv("USE_PYMUPDF_LAYOUT", "false").lower() in {"1", "true", "yes"}


# Logging
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	handlers=[
		logging.FileHandler(os.path.join(LOG_DIR, "extract_text.log")),
		logging.StreamHandler(),
	],
)
logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
	"""Return a filesystem-safe filename."""
	invalid_chars = '<>:"/\\|?*'
	for char in invalid_chars:
		filename = filename.replace(char, "_")
	return filename[:200]


def load_dataset(path: str = METADATA_PATH) -> Dict[str, Any]:
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)


def save_dataset(data: Dict[str, Any], path: str = METADATA_PATH) -> None:
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		json.dump(data, f, indent=4, ensure_ascii=False)
	logger.info("Updated dataset written to %s", path)


def _extract_with_pymupdf4llm(pdf_path: str) -> str:
	if pymupdf4llm is None or not hasattr(pymupdf4llm, "to_text"):
		raise ImportError("pymupdf4llm.to_text not available")
	return pymupdf4llm.to_text(pdf_path)


def _extract_with_fitz(pdf_path: str) -> str:
	if fitz is None:
		raise ImportError("PyMuPDF (fitz) is not installed")
	doc = fitz.open(pdf_path)
	texts = [page.get_text() for page in doc]
	doc.close()
	return "\n".join(texts)


def get_extractor_plan(
	use_layout: bool = USE_PYMUPDF_LAYOUT,
	have_pymupdf4llm: bool = pymupdf4llm is not None,
	have_fitz: bool = fitz is not None,
) -> List[str]:
	"""Return the ordered extractor plan for testing and runtime clarity."""
	plan: List[str] = []
	if use_layout and have_pymupdf4llm:
		plan.append("pymupdf4llm")
	if have_fitz:
		plan.append("pymupdf")
	if not use_layout and have_pymupdf4llm:
		plan.append("pymupdf4llm")
	seen = set()
	ordered: List[str] = []
	for name in plan:
		if name not in seen:
			ordered.append(name)
			seen.add(name)
	return ordered


def extract_pdf_text(pdf_path: str) -> Tuple[str, str]:
	"""
	Extract text from a PDF.

	Order:
	- If USE_PYMUPDF_LAYOUT=true and pymupdf4llm.to_text is available, try it first.
	- Otherwise try PyMuPDF (fitz) first.
	- Fallback to the other extractor.

	Returns a tuple of (text, method_used).
	Raises exceptions if all methods fail.
	"""
	last_error: Optional[Exception] = None
	extractor_plan = get_extractor_plan()

	for method in extractor_plan:
		try:
			if method == "pymupdf4llm":
				extractor = _extract_with_pymupdf4llm
			elif method == "pymupdf":
				extractor = _extract_with_fitz
			else:  # pragma: no cover - future-proof guard
				continue

			text = extractor(pdf_path)
			if text and text.strip():
				return text, method
		except Exception as exc:  # pragma: no cover - robustness path
			last_error = exc
			logger.warning("Extraction with %s failed for %s: %s", method, pdf_path, exc)

	raise RuntimeError(f"All extraction methods failed for {pdf_path}: {last_error}")


def write_text_file(text: str, paper_id: str, title: str, output_dir: str = EXTRACTED_DIR) -> str:
	os.makedirs(output_dir, exist_ok=True)
	safe_title = sanitize_filename(title or "untitled")
	filename = f"{paper_id}_{safe_title}.txt"
	output_path = os.path.join(output_dir, filename)
	with open(output_path, "w", encoding="utf-8") as f:
		f.write(text)
	return output_path


def extract_paper_text(paper: Dict[str, Any], output_dir: str = EXTRACTED_DIR) -> Dict[str, Any]:
	"""Extract text for a single paper and return updated metadata."""
	pdf_path = paper.get("pdf_path")
	if not pdf_path or not os.path.exists(pdf_path):
		paper["extraction_status"] = "missing_pdf"
		paper["text_path"] = None
		paper["extraction_error"] = "PDF path missing or file not found"
		return paper

	try:
		text, method = extract_pdf_text(pdf_path)
		text_path = write_text_file(text, paper.get("paper_id", "paper"), paper.get("title", "untitled"), output_dir)

		paper["text_path"] = text_path
		paper["extraction_status"] = "success"
		paper["extraction_method"] = method
		paper["extraction_date"] = time.strftime("%Y-%m-%d %H:%M:%S")
		paper["text_characters"] = len(text)
		paper.pop("extraction_error", None)
	except Exception as exc:
		paper["text_path"] = None
		paper["extraction_status"] = "failed"
		paper["extraction_error"] = str(exc)
		logger.error("Failed to extract text for %s: %s", paper.get("title", "unknown"), exc)
	return paper


def extract_text_for_papers(papers: List[Dict[str, Any]], output_dir: str = EXTRACTED_DIR) -> List[Dict[str, Any]]:
	updated = []
	total = len(papers)
	logger.info("Starting text extraction for %d papers", total)

	for idx, paper in enumerate(papers, 1):
		print(f"\n[{idx}/{total}] Extracting: {paper.get('title', 'Unknown')[:60]}...")
		updated.append(extract_paper_text(paper, output_dir))

	successes = sum(1 for p in updated if p.get("extraction_status") == "success")
	logger.info("Extraction complete. Success: %d / %d", successes, total)
	return updated


def process_dataset(
	metadata_path: str = METADATA_PATH,
	output_dir: str = EXTRACTED_DIR,
) -> Dict[str, Any]:
	"""
	Load the dataset, extract text for each paper, and rewrite the dataset with
	updated metadata.
	"""
	if not os.path.exists(metadata_path):
		raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

	dataset = load_dataset(metadata_path)
	papers = dataset.get("papers", [])

	if not papers:
		logger.warning("No papers found in dataset for extraction")
		return dataset

	updated_papers = extract_text_for_papers(papers, output_dir)
	dataset["papers"] = updated_papers

	save_dataset(dataset, metadata_path)

	return {
		"total": len(updated_papers),
		"success": sum(1 for p in updated_papers if p.get("extraction_status") == "success"),
		"failed": sum(1 for p in updated_papers if p.get("extraction_status") == "failed"),
	}


if __name__ == "__main__":
	try:
		stats = process_dataset()
		print("\nExtraction Summary:")
		print(f"  Total:   {stats['total']}")
		print(f"  Success: {stats['success']}")
		print(f"  Failed:  {stats['failed']}")
	except Exception as exc:  # pragma: no cover - CLI entry point
		logger.error("Extraction run failed: %s", exc)
		raise

