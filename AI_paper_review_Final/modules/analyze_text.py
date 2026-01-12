"""
Text Analysis Module - Enhanced with Cross-Paper Comparison
============================================================
Reads extracted text files, computes statistics, performs cross-paper analysis,
and identifies comparative insights across the paper corpus.

**FEATURES:**
- Individual paper analysis (readability, key terms, statistics)
- Cross-paper comparison (common themes, methodology differences, findings synthesis)
- Key findings aggregation
- Research gap identification
- Comparative methodology analysis
"""

import json
import logging
import os
import re
from collections import Counter
from typing import Any, Dict, List, Tuple, Set

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


# =============================================================================
# STOPWORDS for term extraction
# =============================================================================
STOPWORDS = {
	"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
	"with", "by", "from", "as", "is", "was", "are", "were", "been", "be", "have",
	"has", "had", "do", "does", "did", "will", "would", "could", "should", "may",
	"might", "must", "shall", "can", "this", "that", "these", "those", "it", "its",
	"we", "our", "they", "their", "he", "she", "him", "her", "his", "them", "i",
	"you", "your", "who", "which", "what", "when", "where", "why", "how", "all",
	"each", "every", "both", "few", "more", "most", "other", "some", "such", "no",
	"not", "only", "same", "so", "than", "too", "very", "also", "just", "then",
	"now", "here", "there", "use", "used", "using", "based", "paper", "study",
	"work", "research", "results", "show", "shown", "shows", "proposed", "propose",
	"approach", "method", "methods", "model", "models", "data", "section", "figure",
	"table", "et", "al", "however", "therefore", "thus", "hence", "moreover",
	"furthermore", "although", "while", "since", "because", "if", "unless", "until",
	"about", "into", "over", "after", "before", "between", "under", "during",
	"through", "above", "below", "up", "down", "out", "off", "again", "further",
	"once", "any", "many", "much", "well", "even", "still", "already", "yet"
}


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
	if not sentences or not words:
		return 0.0
	return round(206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words)), 2)


def _flesch_kincaid_grade(words: List[str], sentences: List[str], syllables: int) -> float:
	if not sentences or not words:
		return 0.0
	return round(0.39 * (len(words) / len(sentences)) + 11.8 * (syllables / len(words)) - 15.59, 2)


def _estimate_syllables(word: str) -> int:
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


def _extract_meaningful_terms(words: List[str], top_k: int = 15) -> List[Tuple[str, int]]:
	"""Extract meaningful terms excluding stopwords."""
	filtered = [w for w in words if w not in STOPWORDS and len(w) > 3]
	counts = Counter(filtered)
	return counts.most_common(top_k)


def _top_ngrams(words: List[str], n: int, top_k: int = 5) -> List[List[Any]]:
	# Filter out stopwords for ngrams
	filtered = [w for w in words if w not in STOPWORDS and len(w) > 2]
	ngrams = [" ".join(filtered[i:i+n]) for i in range(len(filtered) - n + 1)]
	counts = Counter(ngrams)
	return [[term, freq] for term, freq in counts.most_common(top_k)]


def _noun_phrase_candidates(words: List[str]) -> List[str]:
	filtered = [w for w in words if w not in STOPWORDS and len(w) > 2]
	candidates = []
	for n in (2, 3):
		for i in range(len(filtered) - n + 1):
			gram = filtered[i:i+n]
			if all(w.isalpha() for w in gram):
				candidates.append(" ".join(gram))
	counts = Counter(candidates)
	return [term for term, _ in counts.most_common(5)]


def basic_stats(text: str) -> Dict[str, Any]:
	words = re.findall(r"\b[a-zA-Z']+\b", text.lower())
	sentences = re.split(r"(?<=[.!?])\s+", text.strip()) if text.strip() else []

	word_counts = Counter(words)
	top_terms = _extract_meaningful_terms(words, top_k=15)

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


def analyze_single_paper(paper: Dict[str, Any]) -> Dict[str, Any]:
	"""Analyze a single paper and return comprehensive analysis."""
	text_path = paper.get("text_path")
	
	result = {
		"paper_id": paper.get("paper_id"),
		"title": paper.get("title"),
		"year": paper.get("year"),
		"citation_count": paper.get("citation_count"),
		"authors": paper.get("authors", []),
		"sections": paper.get("sections", {}),
		"key_findings": paper.get("key_findings", []),
	}
	
	if not text_path or not os.path.exists(text_path):
		result["analysis_status"] = "missing_text"
		result["analysis_error"] = "Text file not found"
		return result

	try:
		text = read_text_file(text_path)
		stats = basic_stats(text)
		
		result["analysis_status"] = "success"
		result["text_path"] = text_path
		result["stats"] = stats
		
		# Extract domain-specific terms
		result["domain_terms"] = [term for term, _ in stats.get("top_terms", [])[:10]]
		
	except Exception as exc:
		logger.error("Failed to analyze %s: %s", paper.get("title", "unknown"), exc)
		result["analysis_status"] = "failed"
		result["analysis_error"] = str(exc)
		result["text_path"] = text_path

	return result


def find_common_themes(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
	"""Identify common themes and terms across all papers."""
	all_terms = Counter()
	all_phrases = Counter()
	methodology_terms = Counter()
	
	# Methodology-related keywords
	method_keywords = {
		"neural", "network", "deep", "learning", "transformer", "attention",
		"cnn", "rnn", "lstm", "bert", "gpt", "embedding", "classification",
		"training", "dataset", "evaluation", "accuracy", "precision", "recall",
		"optimization", "gradient", "loss", "feature", "representation",
		"supervised", "unsupervised", "reinforcement", "pretrained", "finetuning"
	}
	
	for paper in papers:
		stats = paper.get("stats", {})
		
		# Aggregate terms
		for term, freq in stats.get("top_terms", []):
			all_terms[term] += freq
			if term.lower() in method_keywords:
				methodology_terms[term] += freq
		
		# Aggregate phrases
		for phrase, freq in stats.get("top_bigrams", []) + stats.get("top_trigrams", []):
			all_phrases[phrase] += freq
	
	return {
		"common_terms": all_terms.most_common(20),
		"common_phrases": all_phrases.most_common(15),
		"methodology_terms": methodology_terms.most_common(10),
		"theme_coverage": len(all_terms)
	}


def compare_methodologies(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
	"""Compare methodologies across papers."""
	methodologies = []
	
	for paper in papers:
		sections = paper.get("sections", {})
		methods_section = sections.get("methods", "")
		
		method_info = {
			"paper_id": paper.get("paper_id"),
			"title": paper.get("title"),
			"has_methods_section": bool(methods_section),
			"methods_length": len(methods_section) if methods_section else 0,
		}
		
		# Extract methodology indicators
		if methods_section:
			method_text = methods_section.lower()
			method_info["uses_deep_learning"] = any(kw in method_text for kw in ["deep learning", "neural network", "deep neural"])
			method_info["uses_transformer"] = any(kw in method_text for kw in ["transformer", "attention mechanism", "bert", "gpt"])
			method_info["uses_cnn"] = any(kw in method_text for kw in ["cnn", "convolutional", "convnet"])
			method_info["uses_rnn"] = any(kw in method_text for kw in ["rnn", "lstm", "gru", "recurrent"])
			method_info["is_supervised"] = "supervised" in method_text
			method_info["is_unsupervised"] = "unsupervised" in method_text
			method_info["uses_pretrained"] = any(kw in method_text for kw in ["pretrained", "pre-trained", "fine-tuning", "finetuning"])
		else:
			method_info["uses_deep_learning"] = False
			method_info["uses_transformer"] = False
			method_info["uses_cnn"] = False
			method_info["uses_rnn"] = False
			method_info["is_supervised"] = False
			method_info["is_unsupervised"] = False
			method_info["uses_pretrained"] = False
		
		methodologies.append(method_info)
	
	# Aggregate methodology statistics
	total = len(methodologies)
	if total == 0:
		return {"papers": [], "summary": {}}
	
	summary = {
		"total_papers": total,
		"with_methods_section": sum(1 for m in methodologies if m["has_methods_section"]),
		"using_deep_learning": sum(1 for m in methodologies if m["uses_deep_learning"]),
		"using_transformer": sum(1 for m in methodologies if m["uses_transformer"]),
		"using_cnn": sum(1 for m in methodologies if m["uses_cnn"]),
		"using_rnn": sum(1 for m in methodologies if m["uses_rnn"]),
		"using_pretrained": sum(1 for m in methodologies if m["uses_pretrained"]),
	}
	
	return {
		"papers": methodologies,
		"summary": summary
	}


def synthesize_findings(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
	"""Synthesize and compare key findings across papers."""
	all_findings = []
	findings_by_paper = {}
	
	for paper in papers:
		paper_findings = paper.get("key_findings", [])
		findings_by_paper[paper.get("paper_id")] = {
			"title": paper.get("title"),
			"findings": paper_findings,
			"count": len(paper_findings)
		}
		
		for finding in paper_findings:
			all_findings.append({
				"paper_id": paper.get("paper_id"),
				"paper_title": paper.get("title"),
				"finding": finding
			})
	
	# Categorize findings by type
	performance_findings = []
	methodology_findings = []
	contribution_findings = []
	
	for item in all_findings:
		finding = item["finding"].lower()
		if any(kw in finding for kw in ["accuracy", "precision", "recall", "f1", "performance", "outperform", "achieve", "%"]):
			performance_findings.append(item)
		elif any(kw in finding for kw in ["method", "approach", "technique", "algorithm", "model"]):
			methodology_findings.append(item)
		elif any(kw in finding for kw in ["propose", "introduce", "present", "novel", "new", "first"]):
			contribution_findings.append(item)
	
	return {
		"total_findings": len(all_findings),
		"findings_by_paper": findings_by_paper,
		"performance_findings": performance_findings,
		"methodology_findings": methodology_findings,
		"contribution_findings": contribution_findings,
		"all_findings": all_findings
	}


def identify_research_gaps(papers: List[Dict[str, Any]], common_themes: Dict[str, Any]) -> List[str]:
	"""Identify potential research gaps based on paper analysis."""
	gaps = []
	
	# Check conclusion sections for future work mentions
	future_work_patterns = [
		r"future\s+work",
		r"future\s+research",
		r"limitation",
		r"could\s+be\s+improved",
		r"remains?\s+(?:a\s+)?challenge",
		r"open\s+(?:problem|question|issue)",
	]
	
	for paper in papers:
		conclusion = paper.get("sections", {}).get("conclusion", "")
		if conclusion:
			conclusion_lower = conclusion.lower()
			for pattern in future_work_patterns:
				matches = re.findall(rf"[^.]*{pattern}[^.]*\.", conclusion_lower)
				for match in matches[:2]:  # Limit per paper
					if len(match) > 30 and len(match) < 300:
						gaps.append(f"From '{paper.get('title', 'Unknown')[:40]}...': {match.strip()}")
	
	# Add generic observations
	methodology_summary = compare_methodologies(papers).get("summary", {})
	
	if methodology_summary.get("using_transformer", 0) < methodology_summary.get("total_papers", 1) / 2:
		gaps.append("Potential gap: Limited exploration of transformer-based approaches in this domain.")
	
	if methodology_summary.get("using_pretrained", 0) < methodology_summary.get("total_papers", 1) / 2:
		gaps.append("Potential gap: Transfer learning and pretrained models underutilized.")
	
	return gaps[:10]  # Limit to top 10 gaps


def perform_cross_paper_analysis(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
	"""Perform comprehensive cross-paper analysis."""
	logger.info("Starting cross-paper analysis for %d papers", len(papers))
	
	# Find common themes
	common_themes = find_common_themes(papers)
	
	# Compare methodologies
	methodology_comparison = compare_methodologies(papers)
	
	# Synthesize findings
	findings_synthesis = synthesize_findings(papers)
	
	# Identify research gaps
	research_gaps = identify_research_gaps(papers, common_themes)
	
	# Calculate temporal distribution
	years = [p.get("year") for p in papers if p.get("year")]
	year_distribution = Counter(years)
	
	# Citation analysis
	citations = [p.get("citation_count", 0) for p in papers]
	avg_citations = sum(citations) / len(citations) if citations else 0
	
	cross_analysis = {
		"papers_analyzed": len(papers),
		"common_themes": common_themes,
		"methodology_comparison": methodology_comparison,
		"findings_synthesis": findings_synthesis,
		"research_gaps": research_gaps,
		"temporal_distribution": dict(year_distribution),
		"citation_statistics": {
			"average": round(avg_citations, 1),
			"max": max(citations) if citations else 0,
			"min": min(citations) if citations else 0,
			"total": sum(citations)
		}
	}
	
	logger.info("Cross-paper analysis complete")
	return cross_analysis


def analyze_papers(papers: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
	"""
	Analyze all papers individually and perform cross-paper analysis.
	
	Returns:
		Tuple of (individual_results, cross_paper_analysis)
	"""
	results = []
	total = len(papers)
	logger.info("Starting analysis for %d papers", total)

	for idx, paper in enumerate(papers, 1):
		print(f"\n[{idx}/{total}] Analyzing: {paper.get('title', 'Unknown')[:60]}...")
		results.append(analyze_single_paper(paper))

	success_count = sum(1 for r in results if r.get("analysis_status") == "success")
	logger.info("Individual analysis complete. Success: %d / %d", success_count, total)
	
	# Perform cross-paper analysis on successfully analyzed papers
	successful_papers = [r for r in results if r.get("analysis_status") == "success"]
	cross_analysis = perform_cross_paper_analysis(successful_papers) if successful_papers else {}
	
	return results, cross_analysis


def process_analysis(
	metadata_path: str = METADATA_PATH,
	output_path: str = OUTPUT_PATH,
) -> Dict[str, Any]:
	"""Main entry point for analysis pipeline."""
	if not os.path.exists(metadata_path):
		raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

	dataset = load_dataset(metadata_path)
	papers = dataset.get("papers", [])

	if not papers:
		logger.warning("No papers found in dataset for analysis")
		return {}

	results, cross_analysis = analyze_papers(papers)

	summary = {
		"total": len(results),
		"success": sum(1 for r in results if r.get("analysis_status") == "success"),
		"failed": sum(1 for r in results if r.get("analysis_status") == "failed"),
		"missing_text": sum(1 for r in results if r.get("analysis_status") == "missing_text"),
		"results": results,
		"cross_paper_analysis": cross_analysis,
	}

	save_analysis(summary, output_path)
	return summary


if __name__ == "__main__":
	try:
		summary = process_analysis()
		print("\n" + "=" * 60)
		print("ANALYSIS SUMMARY")
		print("=" * 60)
		print(f"  Total Papers:   {summary.get('total', 0)}")
		print(f"  Success:        {summary.get('success', 0)}")
		print(f"  Failed:         {summary.get('failed', 0)}")
		print(f"  Missing Text:   {summary.get('missing_text', 0)}")
		
		cross = summary.get("cross_paper_analysis", {})
		if cross:
			print("\nCross-Paper Analysis:")
			themes = cross.get("common_themes", {})
			if themes.get("common_terms"):
				print(f"  Common Terms: {', '.join(t for t, _ in themes['common_terms'][:5])}")
			
			methods = cross.get("methodology_comparison", {}).get("summary", {})
			if methods:
				print(f"  Using Deep Learning: {methods.get('using_deep_learning', 0)}/{methods.get('total_papers', 0)}")
				print(f"  Using Transformers: {methods.get('using_transformer', 0)}/{methods.get('total_papers', 0)}")
			
			findings = cross.get("findings_synthesis", {})
			print(f"  Total Findings Extracted: {findings.get('total_findings', 0)}")
			
			gaps = cross.get("research_gaps", [])
			if gaps:
				print(f"  Research Gaps Identified: {len(gaps)}")
		
		print("=" * 60)
	except Exception as exc:
		logger.error("Analysis run failed: %s", exc)
		raise

