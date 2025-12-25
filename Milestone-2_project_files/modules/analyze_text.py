"""
Text Analysis Module
====================
Reads extracted text files, computes lightweight stats, and writes an analysis
summary per paper to data/metadata/analyzed_papers.json.
"""

import json
import logging
import os
import re
from collections import Counter
from typing import Any, Dict, List, Tuple

LOG_DIR = "data/logs"
TEXT_DIR = "data/extracted"
METADATA_PATH = "data/metadata/selected_papers.json"
OUTPUT_PATH = "data/metadata/analyzed_papers.json"

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	handlers=[
		logging.FileHandler(os.path.join(LOG_DIR, "analyze_text.log")),
		logging.StreamHandler(),
	],
)
logger = logging.getLogger(__name__)


def load_dataset(path: str = METADATA_PATH) -> Dict[str, Any]:
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)


def save_analysis(data: Dict[str, Any], path: str = OUTPUT_PATH) -> None:
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		json.dump(data, f, indent=4, ensure_ascii=False)
	logger.info("Analysis written to %s", path)


def read_text_file(path: str) -> str:
	with open(path, "r", encoding="utf-8", errors="ignore") as f:
		return f.read()


def _flesch_reading_ease(words: List[str], sentences: List[str], syllables: int) -> float:
	# Classic Flesch Reading Ease formula; guard against zero divisions
	if not sentences or not words:
		return 0.0
	return round(206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words)), 2)


def _flesch_kincaid_grade(words: List[str], sentences: List[str], syllables: int) -> float:
	if not sentences or not words:
		return 0.0
	return round(0.39 * (len(words) / len(sentences)) + 11.8 * (syllables / len(words)) - 15.59, 2)


def _estimate_syllables(word: str) -> int:
	# Rough heuristic syllable estimator
	word = word.lower()
	vowels = "aeiouy"
	count = 0
	prev_is_vowel = False
	for ch in word:
		is_vowel = ch in vowels
		if is_vowel and not prev_is_vowel:
			count += 1
		prev_is_vowel = is_vowel
	if word.endswith("e") and count > 1:
		count -= 1
	return max(count, 1)


def _top_ngrams(words: List[str], n: int, top_k: int = 5) -> List[List[Any]]:
	ngrams = [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]
	counts = Counter(ngrams)
	return [[term, freq] for term, freq in counts.most_common(top_k)]


def _noun_phrase_candidates(words: List[str]) -> List[str]:
	# Lightweight NP heuristic: keep bigrams/trigrams that are alphabetic and not too short
	candidates = []
	for n in (2, 3):
		for i in range(len(words) - n + 1):
			gram = words[i:i+n]
			if all(len(w) > 2 and w.isalpha() for w in gram):
				candidates.append(" ".join(gram))
	counts = Counter(candidates)
	return [term for term, _ in counts.most_common(5)]


def basic_stats(text: str) -> Dict[str, Any]:
	# Simple tokenization by words
	words = re.findall(r"\b[a-zA-Z']+\b", text.lower())
	sentences = re.split(r"(?<=[.!?])\s+", text.strip()) if text.strip() else []

	word_counts = Counter(words)
	top_terms = word_counts.most_common(10)

	# Derived metrics
	total_words = len(words)
	total_sentences = len([s for s in sentences if s.strip()])
	syllable_est = sum(_estimate_syllables(w) for w in words)
	fk_grade = _flesch_kincaid_grade(words, sentences, syllable_est)
	noun_phrases = _noun_phrase_candidates(words)

	return {
		"characters": len(text),
		"words": total_words,
		"sentences": total_sentences,
		"avg_word_length": round(sum(len(w) for w in words) / total_words, 2) if total_words else 0,
		"avg_sentence_length": round(total_words / total_sentences, 2) if total_sentences else 0,
		"type_token_ratio": round(len(word_counts) / total_words, 3) if total_words else 0,
		"flesch_reading_ease": _flesch_reading_ease(words, sentences, syllable_est),
		"flesch_kincaid_grade": fk_grade,
		"top_terms": top_terms,
		"top_bigrams": _top_ngrams(words, 2),
		"top_trigrams": _top_ngrams(words, 3),
		"noun_phrases": noun_phrases,
	}


def analyze_papers(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
	results = []
	total = len(papers)
	logger.info("Starting analysis for %d papers", total)

	for idx, paper in enumerate(papers, 1):
		print(f"\n[{idx}/{total}] Analyzing: {paper.get('title', 'Unknown')[:60]}...")
		text_path = paper.get("text_path")

		if not text_path or not os.path.exists(text_path):
			results.append({
				"paper_id": paper.get("paper_id"),
				"title": paper.get("title"),
				"analysis_status": "missing_text",
				"analysis_error": "Text file not found",
			})
			continue

		try:
			text = read_text_file(text_path)
			stats = basic_stats(text)
			results.append({
				"paper_id": paper.get("paper_id"),
				"title": paper.get("title"),
				"analysis_status": "success",
				"text_path": text_path,
				"stats": stats,
			})
		except Exception as exc:
			logger.error("Failed to analyze %s: %s", paper.get("title", "unknown"), exc)
			results.append({
				"paper_id": paper.get("paper_id"),
				"title": paper.get("title"),
				"analysis_status": "failed",
				"analysis_error": str(exc),
				"text_path": text_path,
			})

	success = sum(1 for r in results if r.get("analysis_status") == "success")
	logger.info("Analysis complete. Success: %d / %d", success, total)
	return results


def process_analysis(
	metadata_path: str = METADATA_PATH,
	output_path: str = OUTPUT_PATH,
) -> Dict[str, Any]:
	if not os.path.exists(metadata_path):
		raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

	dataset = load_dataset(metadata_path)
	papers = dataset.get("papers", [])

	if not papers:
		logger.warning("No papers found in dataset for analysis")
		return {}

	results = analyze_papers(papers)

	summary = {
		"total": len(results),
		"success": sum(1 for r in results if r.get("analysis_status") == "success"),
		"failed": sum(1 for r in results if r.get("analysis_status") == "failed"),
		"missing_text": sum(1 for r in results if r.get("analysis_status") == "missing_text"),
		"results": results,
	}

	save_analysis(summary, output_path)
	return summary


if __name__ == "__main__":
	try:
		summary = process_analysis()
		print("\nAnalysis Summary:")
		print(f"  Total:   {summary.get('total', 0)}")
		print(f"  Success: {summary.get('success', 0)}")
		print(f"  Failed:  {summary.get('failed', 0)}")
		print(f"  Missing: {summary.get('missing_text', 0)}")
	except Exception as exc:  # pragma: no cover - CLI entry point
		logger.error("Analysis run failed: %s", exc)
		raise

