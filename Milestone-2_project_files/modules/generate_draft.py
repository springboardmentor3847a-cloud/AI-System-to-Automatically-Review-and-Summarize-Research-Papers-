"""
Draft Generation Module
=======================
Creates lightweight draft summaries for each paper using metadata and analysis
outputs. No external LLMs required.
"""

import json
import os
import logging
from typing import Any, Dict, List

LOG_DIR = "data/logs"
METADATA_PATH = "data/metadata/selected_papers.json"
ANALYSIS_PATH = "data/metadata/analyzed_papers.json"
OUTPUT_PATH = "data/metadata/drafts.json"

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	handlers=[
		logging.FileHandler(os.path.join(LOG_DIR, "generate_draft.log")),
		logging.StreamHandler(),
	],
)
logger = logging.getLogger(__name__)


def load_json(path: str) -> Dict[str, Any]:
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)


def save_json(data: Dict[str, Any], path: str = OUTPUT_PATH) -> None:
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		json.dump(data, f, indent=4, ensure_ascii=False)
	logger.info("Drafts written to %s", path)


def pick_top_terms(stats: Dict[str, Any], k: int = 5) -> List[str]:
	terms = stats.get("top_terms", [])
	return [t for t, _ in terms[:k]]


def fill_sections(paper: Dict[str, Any], stats: Dict[str, Any], key_terms: List[str]) -> Dict[str, str]:
	phrases = stats.get("noun_phrases", [])
	main_term = phrases[0] if phrases else (key_terms[0] if key_terms else "the main topic")
	secondary = key_terms[1:3]

	contrib = f"Addresses {main_term} with focus on {', '.join(secondary)}." if secondary else f"Addresses {main_term}."
	method_terms = stats.get("top_bigrams", [])[:2]
	method = "Uses common NLP/deep learning techniques." if not method_terms else f"Method centers on {', '.join(mt for mt, _ in method_terms)}."
	results = "Results not explicitly provided in metadata; highlight key findings and evaluation metrics when available."

	return {
		"contribution": contrib,
		"method": method,
		"results": results,
	}


def compose_narrative(paper: Dict[str, Any], stats: Dict[str, Any], key_terms: List[str]) -> str:
	abstract = paper.get("abstract") or "Abstract not available."
	year = paper.get("year") or "N/A"
	citations = paper.get("citation_count")
	cite_txt = f" (citations: {citations})" if citations is not None else ""

	profile_bits = []
	if stats.get("words"):
		profile_bits.append(f"~{stats['words']} words")
	if stats.get("avg_sentence_length"):
		profile_bits.append(f"avg sentence {stats['avg_sentence_length']} words")
	if stats.get("flesch_reading_ease"):
		profile_bits.append(f"Flesch {stats['flesch_reading_ease']}")
	profile = "; ".join(profile_bits)

	terms_txt = ", ".join(key_terms[:5]) if key_terms else "(no dominant terms)"

	return (
		f"{paper.get('title', 'Untitled')} ({year}){cite_txt}. "
		f"Content profile: {profile}. "
		f"Key terms: {terms_txt}. "
		f"Abstract: {abstract}"
	)


def make_draft_entry(paper: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
	stats = analysis.get("stats", {})
	top_terms = pick_top_terms(stats, k=5)
	strengths = []

	if stats.get("flesch_reading_ease"):
		strengths.append(f"Readable score: {stats['flesch_reading_ease']}")
	if stats.get("flesch_kincaid_grade"):
		strengths.append(f"Grade level: {stats['flesch_kincaid_grade']}")
	if stats.get("avg_sentence_length"):
		strengths.append(f"Avg sentence length: {stats['avg_sentence_length']}")
	if stats.get("top_terms"):
		strengths.append("Top terms: " + ", ".join(top_terms))
	if stats.get("noun_phrases"):
		strengths.append("Key noun phrases: " + ", ".join(stats.get("noun_phrases", [])[:5]))

	narrative = compose_narrative(paper, stats, top_terms)
	sections = fill_sections(paper, stats, top_terms)

	summary = {
		"title": paper.get("title"),
		"paper_id": paper.get("paper_id"),
		"year": paper.get("year"),
		"citations": paper.get("citation_count"),
		"abstract": paper.get("abstract"),
		"text_path": paper.get("text_path"),
		"analysis_status": analysis.get("analysis_status"),
		"stats": stats,
		"strengths": strengths,
		"key_terms": top_terms,
		"draft_text": narrative,
		"sections": sections,
	}

	return summary


def generate_drafts(
	metadata_path: str = METADATA_PATH,
	analysis_path: str = ANALYSIS_PATH,
	output_path: str = OUTPUT_PATH,
) -> Dict[str, Any]:
	if not os.path.exists(metadata_path):
		raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
	if not os.path.exists(analysis_path):
		raise FileNotFoundError(f"Analysis file not found: {analysis_path}")

	dataset = load_json(metadata_path)
	analysis = load_json(analysis_path)

	papers_by_id = {p.get("paper_id"): p for p in dataset.get("papers", [])}
	drafts: List[Dict[str, Any]] = []

	for result in analysis.get("results", []):
		pid = result.get("paper_id")
		paper = papers_by_id.get(pid)
		if not paper:
			continue
		drafts.append(make_draft_entry(paper, result))

	summary = {
		"total": len(drafts),
		"drafts": drafts,
	}

	save_json(summary, output_path)
	return summary


if __name__ == "__main__":
	try:
		summary = generate_drafts()
		print("\nDraft Generation Summary:")
		print(f"  Drafts created: {summary.get('total', 0)}")
	except Exception as exc:
		logger.error("Draft generation failed: %s", exc)
		raise


