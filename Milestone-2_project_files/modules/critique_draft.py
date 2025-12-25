"""
Draft Critique Module
=====================
Generates heuristic critiques for drafts without external LLMs and writes
results to data/metadata/critiques.json.
"""

import json
import logging
import os
from typing import Any, Dict, List

LOG_DIR = "data/logs"
DRAFTS_PATH = "data/metadata/drafts.json"
OUTPUT_PATH = "data/metadata/critiques.json"

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	handlers=[
		logging.FileHandler(os.path.join(LOG_DIR, "critique_draft.log")),
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
	logger.info("Critiques written to %s", path)


def critique_entry(draft: Dict[str, Any]) -> Dict[str, Any]:
	stats = draft.get("stats", {})
	flags: List[str] = []
	suggestions: List[str] = []

	sections = draft.get("sections", {})

	if stats.get("flesch_reading_ease") is not None and stats["flesch_reading_ease"] < 40:
		flags.append("hard_to_read")
		suggestions.append("Improve readability (shorter sentences, simpler words).")

	if stats.get("flesch_kincaid_grade") is not None and stats["flesch_kincaid_grade"] > 14:
		flags.append("high_grade_level")
		suggestions.append("Lower grade level: shorter sentences, simpler phrasing.")

	if stats.get("avg_sentence_length") and stats["avg_sentence_length"] > 25:
		flags.append("long_sentences")
		suggestions.append("Split long sentences to improve clarity.")

	if len(draft.get("key_terms", [])) < 3:
		flags.append("thin_keywords")
		suggestions.append("Highlight more domain-specific terms.")

	if not draft.get("abstract"):
		flags.append("missing_abstract")
		suggestions.append("Add an abstract excerpt to ground the draft.")

	if draft.get("citations") is None:
		flags.append("missing_citation_data")
		suggestions.append("Surface citation count or key references to strengthen context.")

	if not draft.get("draft_text") or len(draft.get("draft_text", "")) < 300:
		flags.append("draft_too_short")
		suggestions.append("Expand draft_text with contribution, method, results.")

	# Check required sections presence
	for sec in ("contribution", "method", "results"):
		content = sections.get(sec, "")
		if not content:
			flags.append(f"missing_{sec}")
			suggestions.append(f"Add a concise {sec} summary.")
		elif content.startswith("(") or len(content) < 40:
			flags.append(f"weak_{sec}")
			suggestions.append(f"Strengthen the {sec} section with specifics.")

	if draft.get("citations") and draft.get("draft_text") and str(draft.get("citations")) not in draft.get("draft_text", ""):
		flags.append("missing_citation_reference")
		suggestions.append("Mention citation impact (e.g., citation count or key prior work).")

	critique = {
		"paper_id": draft.get("paper_id"),
		"title": draft.get("title"),
		"flags": flags,
		"suggestions": suggestions,
		"draft_text": draft.get("draft_text"),
	}
	return critique


def critique_drafts(
	drafts_path: str = DRAFTS_PATH,
	output_path: str = OUTPUT_PATH,
) -> Dict[str, Any]:
	if not os.path.exists(drafts_path):
		raise FileNotFoundError(f"Drafts file not found: {drafts_path}")

	data = load_json(drafts_path)
	drafts = data.get("drafts", [])

	critiques = [critique_entry(d) for d in drafts]

	summary = {
		"total": len(critiques),
		"critiques": critiques,
	}

	save_json(summary, output_path)
	return summary


if __name__ == "__main__":
	try:
		summary = critique_drafts()
		print("\nCritique Summary:")
		print(f"  Critiques generated: {summary.get('total', 0)}")
	except Exception as exc:
		logger.error("Critique generation failed: %s", exc)
		raise


