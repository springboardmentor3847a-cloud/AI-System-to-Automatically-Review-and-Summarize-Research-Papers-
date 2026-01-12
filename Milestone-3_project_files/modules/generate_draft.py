"""
Literature Review Draft Generation Module
==========================================
Generates a structured academic literature review from analyzed papers.

**OUTPUT STRUCTURE:**
1. Abstract (≤100 words)
2. Introduction
3. Methodology Comparison
4. Results Synthesis
5. Conclusion
6. APA Formatted References

**PRINCIPLES:**
- All content is grounded in extracted paper text (no hallucination)
- Comparative analysis across papers
- Academic writing style
- Proper citation formatting
"""

import json
import os
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

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


def format_apa_reference(paper: Dict[str, Any]) -> str:
	"""
	Format a paper citation in APA 7th edition style.
	
	Format: Author, A. A., & Author, B. B. (Year). Title of article. Journal Name.
	"""
	authors = paper.get("authors", [])
	year = paper.get("year", "n.d.")
	title = paper.get("title", "Untitled")
	
	# Format authors
	if not authors:
		author_str = "Unknown Author"
	elif len(authors) == 1:
		author_str = _format_author_name(authors[0])
	elif len(authors) == 2:
		author_str = f"{_format_author_name(authors[0])} & {_format_author_name(authors[1])}"
	elif len(authors) <= 20:
		author_parts = [_format_author_name(a) for a in authors[:-1]]
		author_str = ", ".join(author_parts) + f", & {_format_author_name(authors[-1])}"
	else:
		# More than 20 authors: list first 19, ..., and last
		author_parts = [_format_author_name(a) for a in authors[:19]]
		author_str = ", ".join(author_parts) + f", ... {_format_author_name(authors[-1])}"
	
	# Format reference
	url = paper.get("url", "")
	url_str = f" Retrieved from {url}" if url else ""
	
	return f"{author_str} ({year}). {title}.{url_str}"


def _format_author_name(name: str) -> str:
	"""Convert 'First Last' to 'Last, F.'"""
	if not name:
		return "Unknown"
	parts = name.strip().split()
	if len(parts) == 1:
		return parts[0]
	elif len(parts) >= 2:
		last = parts[-1]
		initials = "".join([p[0].upper() + "." for p in parts[:-1] if p])
		return f"{last}, {initials}"
	return name


def generate_abstract(papers: List[Dict[str, Any]], topic: str, cross_analysis: Dict[str, Any]) -> str:
	"""
	Generate a ≤100 word abstract summarizing the literature review.
	Grounded in actual paper content.
	"""
	num_papers = len(papers)
	
	# Extract key themes
	themes = cross_analysis.get("common_themes", {})
	common_terms = [term for term, _ in themes.get("common_terms", [])[:5]]
	
	# Get year range
	years = [p.get("year") for p in papers if p.get("year")]
	year_range = f"{min(years)}-{max(years)}" if years else "recent years"
	
	# Get methodology summary
	methods_summary = cross_analysis.get("methodology_comparison", {}).get("summary", {})
	dl_count = methods_summary.get("using_deep_learning", 0)
	
	# Construct abstract (grounded in actual data)
	abstract = (
		f"This literature review synthesizes {num_papers} research papers on {topic}, "
		f"published between {year_range}. "
	)
	
	if common_terms:
		abstract += f"Key themes include {', '.join(common_terms[:3])}. "
	
	if dl_count > 0:
		abstract += f"Deep learning approaches are employed in {dl_count} of {num_papers} papers. "
	
	# Add findings summary
	findings = cross_analysis.get("findings_synthesis", {})
	total_findings = findings.get("total_findings", 0)
	if total_findings > 0:
		abstract += f"The review identifies {total_findings} key findings across the literature. "
	
	abstract += "This review provides a comparative analysis of methodologies, synthesizes results, and identifies research gaps."
	
	# Ensure ≤100 words
	words = abstract.split()
	if len(words) > 100:
		abstract = " ".join(words[:97]) + "..."
	
	return abstract.strip()


def generate_introduction(papers: List[Dict[str, Any]], topic: str, cross_analysis: Dict[str, Any]) -> str:
	"""
	Generate an introduction section grounded in paper content.
	"""
	num_papers = len(papers)
	years = [p.get("year") for p in papers if p.get("year")]
	year_range = f"{min(years)} to {max(years)}" if years else "recent years"
	
	# Get citation statistics
	citations = cross_analysis.get("citation_statistics", {})
	total_citations = citations.get("total", 0)
	
	# Get themes
	themes = cross_analysis.get("common_themes", {})
	common_terms = [term for term, _ in themes.get("common_terms", [])[:7]]
	
	intro = f"""## Introduction

The field of {topic} has seen significant research activity in recent years. This literature review examines {num_papers} peer-reviewed research papers published from {year_range}, collectively accumulating {total_citations} citations in the academic literature.

### Research Context

The papers under review address various aspects of {topic}, with particular focus on {', '.join(common_terms[:3]) if common_terms else 'core technical challenges'}. The research spans multiple methodological approaches and application domains, reflecting the interdisciplinary nature of this field.

### Review Objectives

This review aims to:
1. Synthesize the current state of research in {topic}
2. Compare methodological approaches across studies
3. Identify key findings and contributions
4. Highlight research gaps and future directions

### Papers Reviewed

The following papers form the basis of this review:
"""
	
	# Add paper list with citations
	for idx, paper in enumerate(papers, 1):
		authors = paper.get("authors", ["Unknown"])
		first_author = authors[0].split()[-1] if authors else "Unknown"
		year = paper.get("year", "n.d.")
		title = paper.get("title", "Untitled")[:80]
		citations = paper.get("citation_count", 0)
		intro += f"\n{idx}. **{first_author} et al. ({year})**: {title} [{citations} citations]"
	
	return intro


def generate_methodology_comparison(papers: List[Dict[str, Any]], cross_analysis: Dict[str, Any]) -> str:
	"""
	Generate methodology comparison section based on actual paper content.
	"""
	methods_data = cross_analysis.get("methodology_comparison", {})
	papers_methods = methods_data.get("papers", [])
	summary = methods_data.get("summary", {})
	
	section = """## Methodology Comparison

This section presents a comparative analysis of the methodological approaches employed across the reviewed papers.

### Overview of Approaches

"""
	
	total = summary.get("total_papers", len(papers))
	
	# Deep Learning usage
	dl_count = summary.get("using_deep_learning", 0)
	if dl_count > 0:
		section += f"**Deep Learning**: {dl_count} of {total} papers ({round(dl_count/total*100)}%) employ deep learning techniques.\n\n"
	
	# Transformer usage
	transformer_count = summary.get("using_transformer", 0)
	if transformer_count > 0:
		section += f"**Transformer/Attention Models**: {transformer_count} of {total} papers utilize transformer-based architectures or attention mechanisms.\n\n"
	
	# CNN usage
	cnn_count = summary.get("using_cnn", 0)
	if cnn_count > 0:
		section += f"**Convolutional Neural Networks**: {cnn_count} of {total} papers apply CNN-based methods.\n\n"
	
	# RNN usage
	rnn_count = summary.get("using_rnn", 0)
	if rnn_count > 0:
		section += f"**Recurrent Neural Networks**: {rnn_count} of {total} papers use RNN/LSTM/GRU architectures.\n\n"
	
	# Pretrained models
	pretrained_count = summary.get("using_pretrained", 0)
	if pretrained_count > 0:
		section += f"**Transfer Learning/Pretrained Models**: {pretrained_count} of {total} papers leverage pretrained models or transfer learning.\n\n"
	
	# Per-paper methodology details
	section += "### Paper-Specific Methodologies\n\n"
	section += "| Paper | Deep Learning | Transformer | CNN | RNN | Pretrained |\n"
	section += "|-------|---------------|-------------|-----|-----|------------|\n"
	
	for idx, method_info in enumerate(papers_methods):
		title = method_info.get("title", "Unknown")[:40]
		dl = "✓" if method_info.get("uses_deep_learning") else "—"
		trans = "✓" if method_info.get("uses_transformer") else "—"
		cnn = "✓" if method_info.get("uses_cnn") else "—"
		rnn = "✓" if method_info.get("uses_rnn") else "—"
		pre = "✓" if method_info.get("uses_pretrained") else "—"
		section += f"| {title}... | {dl} | {trans} | {cnn} | {rnn} | {pre} |\n"
	
	return section


def generate_results_synthesis(papers: List[Dict[str, Any]], cross_analysis: Dict[str, Any]) -> str:
	"""
	Synthesize results and key findings from all papers.
	"""
	findings_data = cross_analysis.get("findings_synthesis", {})
	all_findings = findings_data.get("all_findings", [])
	performance_findings = findings_data.get("performance_findings", [])
	contribution_findings = findings_data.get("contribution_findings", [])
	
	section = """## Results Synthesis

This section synthesizes the key findings and results reported across the reviewed papers.

### Key Contributions

"""
	
	if contribution_findings:
		section += "The papers make the following notable contributions:\n\n"
		for idx, item in enumerate(contribution_findings[:5], 1):
			paper_title = item.get("paper_title", "Unknown")[:40]
			finding = item.get("finding", "")
			section += f"{idx}. **{paper_title}...**: {finding}\n\n"
	else:
		section += "The papers collectively contribute to advancing the field through novel methods and insights.\n\n"
	
	section += "### Performance Results\n\n"
	
	if performance_findings:
		section += "The following performance-related findings were reported:\n\n"
		for idx, item in enumerate(performance_findings[:5], 1):
			paper_title = item.get("paper_title", "Unknown")[:40]
			finding = item.get("finding", "")
			section += f"- **{paper_title}...**: {finding}\n"
		section += "\n"
	else:
		section += "Performance metrics vary across papers based on specific tasks and datasets used.\n\n"
	
	# Cross-paper comparison
	section += "### Cross-Paper Findings\n\n"
	
	findings_by_paper = findings_data.get("findings_by_paper", {})
	if findings_by_paper:
		section += "| Paper | Findings Count | Key Themes |\n"
		section += "|-------|----------------|------------|\n"
		for paper_id, info in findings_by_paper.items():
			title = info.get("title", "Unknown")[:35]
			count = info.get("count", 0)
			# Extract first finding as theme
			findings_list = info.get("findings", [])
			theme = findings_list[0][:50] + "..." if findings_list else "Not extracted"
			section += f"| {title}... | {count} | {theme} |\n"
	
	return section


def generate_conclusion(papers: List[Dict[str, Any]], topic: str, cross_analysis: Dict[str, Any]) -> str:
	"""
	Generate conclusion section with research gaps and future directions.
	"""
	research_gaps = cross_analysis.get("research_gaps", [])
	num_papers = len(papers)
	
	section = f"""## Conclusion

This literature review has examined {num_papers} research papers on {topic}, providing a comprehensive analysis of current methodological approaches, key findings, and research contributions.

### Summary of Findings

"""
	
	# Summary based on methodology comparison
	methods_summary = cross_analysis.get("methodology_comparison", {}).get("summary", {})
	if methods_summary:
		section += "The reviewed papers demonstrate diverse methodological approaches:\n\n"
		if methods_summary.get("using_deep_learning", 0) > 0:
			section += f"- Deep learning techniques are prevalent, appearing in {methods_summary.get('using_deep_learning', 0)} papers\n"
		if methods_summary.get("using_transformer", 0) > 0:
			section += f"- Transformer-based approaches are emerging, used in {methods_summary.get('using_transformer', 0)} papers\n"
		if methods_summary.get("using_pretrained", 0) > 0:
			section += f"- Transfer learning and pretrained models appear in {methods_summary.get('using_pretrained', 0)} papers\n"
		section += "\n"
	
	# Research gaps
	section += "### Research Gaps and Future Directions\n\n"
	
	if research_gaps:
		section += "Based on the analysis, the following research gaps and opportunities have been identified:\n\n"
		for idx, gap in enumerate(research_gaps[:5], 1):
			section += f"{idx}. {gap}\n\n"
	else:
		section += "The field continues to evolve with opportunities for further research in methodology refinement, cross-domain applications, and scalability improvements.\n\n"
	
	# Closing statement
	section += """### Final Remarks

This review provides a foundation for researchers seeking to understand the current landscape of this research area. The synthesized findings and identified gaps can guide future research efforts toward addressing open challenges and advancing the state of the art."""
	
	return section


def generate_references(papers: List[Dict[str, Any]]) -> str:
	"""
	Generate APA formatted references section.
	"""
	section = "## References\n\n"
	
	# Sort papers by first author last name
	sorted_papers = sorted(papers, key=lambda p: (p.get("authors", ["ZZZ"])[0].split()[-1] if p.get("authors") else "ZZZ").lower())
	
	for paper in sorted_papers:
		ref = format_apa_reference(paper)
		section += f"- {ref}\n\n"
	
	return section


def generate_literature_review(
	papers: List[Dict[str, Any]],
	cross_analysis: Dict[str, Any],
	topic: str
) -> Dict[str, Any]:
	"""
	Generate complete structured literature review.
	
	Args:
		papers: List of paper metadata with analysis
		cross_analysis: Cross-paper analysis results
		topic: Research topic
	
	Returns:
		Dictionary containing all review sections
	"""
	logger.info("Generating literature review for %d papers on topic: %s", len(papers), topic)
	
	# Generate all sections
	abstract = generate_abstract(papers, topic, cross_analysis)
	introduction = generate_introduction(papers, topic, cross_analysis)
	methodology = generate_methodology_comparison(papers, cross_analysis)
	results = generate_results_synthesis(papers, cross_analysis)
	conclusion = generate_conclusion(papers, topic, cross_analysis)
	references = generate_references(papers)
	
	# Compile full review
	full_text = f"""# Literature Review: {topic.title()}

**Generated**: {datetime.now().strftime("%B %d, %Y")}
**Papers Reviewed**: {len(papers)}

---

## Abstract

{abstract}

---

{introduction}

---

{methodology}

---

{results}

---

{conclusion}

---

{references}
"""
	
	review = {
		"topic": topic,
		"generated_date": datetime.now().isoformat(),
		"papers_count": len(papers),
		"sections": {
			"abstract": abstract,
			"introduction": introduction,
			"methodology_comparison": methodology,
			"results_synthesis": results,
			"conclusion": conclusion,
			"references": references,
		},
		"full_text": full_text,
		"word_count": len(full_text.split()),
		"papers_included": [
			{
				"paper_id": p.get("paper_id"),
				"title": p.get("title"),
				"year": p.get("year"),
				"authors": p.get("authors", [])[:3],
				"citation_count": p.get("citation_count"),
			}
			for p in papers
		]
	}
	
	return review


def generate_drafts(
	metadata_path: str = METADATA_PATH,
	analysis_path: str = ANALYSIS_PATH,
	output_path: str = OUTPUT_PATH,
) -> Dict[str, Any]:
	"""
	Main entry point for literature review generation.
	"""
	if not os.path.exists(metadata_path):
		raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
	if not os.path.exists(analysis_path):
		raise FileNotFoundError(f"Analysis file not found: {analysis_path}")

	# Load data
	dataset = load_json(metadata_path)
	analysis = load_json(analysis_path)
	
	# Get topic from dataset
	topic = dataset.get("topic", "research papers")
	
	# Get papers and cross-analysis
	papers = dataset.get("papers", [])
	analysis_results = analysis.get("results", [])
	cross_analysis = analysis.get("cross_paper_analysis", {})
	
	# Merge paper data with analysis results
	analysis_by_id = {r.get("paper_id"): r for r in analysis_results}
	enriched_papers = []
	
	for paper in papers:
		paper_id = paper.get("paper_id")
		if paper_id in analysis_by_id:
			# Merge analysis data into paper
			merged = {**paper, **analysis_by_id[paper_id]}
			enriched_papers.append(merged)
		else:
			enriched_papers.append(paper)
	
	# Generate the literature review
	review = generate_literature_review(enriched_papers, cross_analysis, topic)
	
	# Also generate individual paper drafts for reference
	individual_drafts = []
	for paper in enriched_papers:
		draft = {
			"paper_id": paper.get("paper_id"),
			"title": paper.get("title"),
			"year": paper.get("year"),
			"abstract": paper.get("abstract"),
			"key_findings": paper.get("key_findings", []),
			"sections": paper.get("sections", {}),
			"apa_reference": format_apa_reference(paper),
		}
		individual_drafts.append(draft)
	
	summary = {
		"total": len(enriched_papers),
		"topic": topic,
		"generated_date": datetime.now().isoformat(),
		"literature_review": review,
		"individual_drafts": individual_drafts,
	}

	save_json(summary, output_path)
	
	logger.info("Literature review generated successfully")
	logger.info("  - Word count: %d", review.get("word_count", 0))
	logger.info("  - Papers included: %d", review.get("papers_count", 0))
	
	return summary


if __name__ == "__main__":
	try:
		summary = generate_drafts()
		print("\n" + "=" * 60)
		print("LITERATURE REVIEW GENERATION COMPLETE")
		print("=" * 60)
		print(f"  Topic: {summary.get('topic')}")
		print(f"  Papers Included: {summary.get('total')}")
		
		review = summary.get("literature_review", {})
		print(f"  Word Count: {review.get('word_count', 0)}")
		print(f"  Sections Generated: {len(review.get('sections', {}))}")
		
		print("\nSections:")
		for section_name in review.get("sections", {}).keys():
			print(f"  - {section_name}")
		
		print("=" * 60)
	except Exception as exc:
		logger.error("Draft generation failed: %s", exc)
		raise
