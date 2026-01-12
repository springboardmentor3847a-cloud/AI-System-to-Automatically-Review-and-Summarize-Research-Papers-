"""
Literature Review Critique and Revision Module
==============================================
Provides automated critique and revision capabilities for generated literature reviews.

**FEATURES:**
- Quality assessment of generated content
- Identification of weak sections
- Academic writing style checks
- Citation verification
- Automated revision suggestions
- Section-by-section improvement recommendations
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime

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


# =============================================================================
# QUALITY CRITERIA
# =============================================================================
QUALITY_CRITERIA = {
	"abstract": {
		"min_words": 50,
		"max_words": 150,
		"required_elements": ["papers", "review", "findings"],
		"weight": 0.15
	},
	"introduction": {
		"min_words": 150,
		"max_words": 800,
		"required_elements": ["objective", "research", "papers"],
		"weight": 0.20
	},
	"methodology_comparison": {
		"min_words": 200,
		"max_words": 1000,
		"required_elements": ["approach", "method", "comparison"],
		"weight": 0.25
	},
	"results_synthesis": {
		"min_words": 150,
		"max_words": 800,
		"required_elements": ["findings", "results", "paper"],
		"weight": 0.25
	},
	"conclusion": {
		"min_words": 100,
		"max_words": 500,
		"required_elements": ["summary", "future", "research"],
		"weight": 0.10
	},
	"references": {
		"min_words": 50,
		"max_words": 2000,
		"required_elements": [],
		"weight": 0.05
	}
}

# Academic writing issues to check
ACADEMIC_STYLE_CHECKS = [
	{
		"pattern": r"\b(very|really|extremely|absolutely)\b",
		"issue": "informal_intensifiers",
		"suggestion": "Replace informal intensifiers with more precise academic language"
	},
	{
		"pattern": r"\b(thing|stuff|lots|bunch)\b",
		"issue": "informal_nouns",
		"suggestion": "Use specific, technical terminology instead of vague nouns"
	},
	{
		"pattern": r"\b(I think|I believe|I feel)\b",
		"issue": "first_person_subjective",
		"suggestion": "Use objective, third-person academic voice"
	},
	{
		"pattern": r"\b(etc\.|and so on|and so forth)\b",
		"issue": "incomplete_lists",
		"suggestion": "Provide complete lists or use 'among others' for academic writing"
	},
	{
		"pattern": r"[!]{2,}|[?]{2,}",
		"issue": "excessive_punctuation",
		"suggestion": "Use single punctuation marks for academic writing"
	},
	{
		"pattern": r"\b(gonna|wanna|gotta|kinda|sorta)\b",
		"issue": "colloquial_language",
		"suggestion": "Use formal language in academic writing"
	}
]


def load_json(path: str) -> Dict[str, Any]:
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)


def save_json(data: Dict[str, Any], path: str = OUTPUT_PATH) -> None:
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		json.dump(data, f, indent=4, ensure_ascii=False)
	logger.info("Critiques written to %s", path)


def count_words(text: str) -> int:
	"""Count words in text."""
	return len(text.split()) if text else 0


def check_section_quality(section_name: str, content: str) -> Dict[str, Any]:
	"""
	Evaluate quality of a specific section.
	
	Returns:
		Dictionary with quality score, issues, and suggestions
	"""
	if not content:
		return {
			"score": 0.0,
			"issues": ["section_empty"],
			"suggestions": [f"Add content to the {section_name} section"],
			"word_count": 0
		}
	
	criteria = QUALITY_CRITERIA.get(section_name, {
		"min_words": 50,
		"max_words": 500,
		"required_elements": [],
		"weight": 0.1
	})
	
	issues = []
	suggestions = []
	score_deductions = 0.0
	
	word_count = count_words(content)
	
	# Check word count
	if word_count < criteria["min_words"]:
		issues.append("too_short")
		suggestions.append(f"Expand {section_name} to at least {criteria['min_words']} words (current: {word_count})")
		score_deductions += 0.3
	elif word_count > criteria["max_words"]:
		issues.append("too_long")
		suggestions.append(f"Consider condensing {section_name} to under {criteria['max_words']} words (current: {word_count})")
		score_deductions += 0.1
	
	# Check required elements
	content_lower = content.lower()
	missing_elements = []
	for element in criteria["required_elements"]:
		if element.lower() not in content_lower:
			missing_elements.append(element)
	
	if missing_elements:
		issues.append("missing_elements")
		suggestions.append(f"Consider addressing: {', '.join(missing_elements)}")
		score_deductions += 0.1 * len(missing_elements)
	
	# Academic style checks
	for check in ACADEMIC_STYLE_CHECKS:
		matches = re.findall(check["pattern"], content, re.IGNORECASE)
		if matches:
			issues.append(check["issue"])
			suggestions.append(f"{check['suggestion']} (found: {', '.join(set(matches)[:3])})")
			score_deductions += 0.05
	
	# Calculate score
	base_score = 1.0
	final_score = max(0.0, min(1.0, base_score - score_deductions))
	
	return {
		"score": round(final_score, 2),
		"issues": issues,
		"suggestions": suggestions,
		"word_count": word_count,
		"weight": criteria["weight"]
	}


def check_citation_quality(references: str, papers_count: int) -> Dict[str, Any]:
	"""
	Verify citation quality and completeness.
	"""
	issues = []
	suggestions = []
	
	# Count references
	ref_count = len(re.findall(r"^- ", references, re.MULTILINE))
	
	if ref_count < papers_count:
		issues.append("missing_references")
		suggestions.append(f"Expected {papers_count} references, found {ref_count}")
	
	# Check for year patterns (YYYY)
	year_pattern = r"\(\d{4}\)"
	years_found = len(re.findall(year_pattern, references))
	
	if years_found < ref_count:
		issues.append("incomplete_citations")
		suggestions.append("Ensure all references include publication year in parentheses")
	
	# Check for author names
	# Simple check: references should have comma after last name
	author_pattern = r"[A-Z][a-z]+,"
	if len(re.findall(author_pattern, references)) < ref_count:
		issues.append("author_format_issues")
		suggestions.append("Verify author names follow APA format (LastName, F. I.)")
	
	score = 1.0 - (0.2 * len(issues))
	
	return {
		"score": max(0.0, round(score, 2)),
		"issues": issues,
		"suggestions": suggestions,
		"reference_count": ref_count,
		"expected_count": papers_count
	}


def check_coherence(sections: Dict[str, str]) -> Dict[str, Any]:
	"""
	Check coherence and flow between sections.
	"""
	issues = []
	suggestions = []
	
	# Check if key terms appear consistently across sections
	all_content = " ".join(sections.values())
	
	# Extract topic-related terms from introduction
	intro = sections.get("introduction", "")
	intro_words = set(re.findall(r"\b[A-Za-z]{5,}\b", intro.lower()))
	
	# Check if conclusion references introduction themes
	conclusion = sections.get("conclusion", "")
	conclusion_words = set(re.findall(r"\b[A-Za-z]{5,}\b", conclusion.lower()))
	
	common_terms = intro_words & conclusion_words
	if len(common_terms) < 5:
		issues.append("weak_coherence")
		suggestions.append("Ensure conclusion references key themes from introduction")
	
	# Check section order and presence
	expected_sections = ["abstract", "introduction", "methodology_comparison", "results_synthesis", "conclusion", "references"]
	present_sections = [s for s in expected_sections if sections.get(s)]
	
	if len(present_sections) < len(expected_sections):
		missing = set(expected_sections) - set(present_sections)
		issues.append("missing_sections")
		suggestions.append(f"Add missing sections: {', '.join(missing)}")
	
	score = 1.0 - (0.15 * len(issues))
	
	return {
		"score": max(0.0, round(score, 2)),
		"issues": issues,
		"suggestions": suggestions,
		"sections_present": len(present_sections),
		"sections_expected": len(expected_sections)
	}


def generate_revision(section_name: str, content: str, issues: List[str], suggestions: List[str]) -> str:
	"""
	Generate a revised version of the section based on identified issues.
	This provides concrete textual improvements.
	"""
	if not content:
		return f"[{section_name.upper()} SECTION NEEDS TO BE WRITTEN]"
	
	revised = content
	
	# Apply automatic fixes for certain issues
	for check in ACADEMIC_STYLE_CHECKS:
		if check["issue"] in issues:
			# Simple replacement for common issues
			if check["issue"] == "informal_intensifiers":
				revised = re.sub(r"\bvery\b", "notably", revised, flags=re.IGNORECASE)
				revised = re.sub(r"\breally\b", "substantially", revised, flags=re.IGNORECASE)
				revised = re.sub(r"\bextremely\b", "significantly", revised, flags=re.IGNORECASE)
			elif check["issue"] == "colloquial_language":
				revised = re.sub(r"\bgonna\b", "going to", revised, flags=re.IGNORECASE)
				revised = re.sub(r"\bwanna\b", "want to", revised, flags=re.IGNORECASE)
				revised = re.sub(r"\bgotta\b", "have to", revised, flags=re.IGNORECASE)
	
	# Add note about remaining manual revisions needed
	if issues:
		remaining_issues = [i for i in issues if i not in ["informal_intensifiers", "colloquial_language"]]
		if remaining_issues:
			revision_note = f"\n\n<!-- REVISION NOTE: Address these issues: {', '.join(remaining_issues)} -->"
			revised += revision_note
	
	return revised


def critique_literature_review(review: Dict[str, Any]) -> Dict[str, Any]:
	"""
	Comprehensive critique of the literature review.
	
	Args:
		review: The literature review dictionary from generate_draft
	
	Returns:
		Detailed critique with scores, issues, and suggestions
	"""
	sections = review.get("sections", {})
	papers_count = review.get("papers_count", 0)
	
	# Critique each section
	section_critiques = {}
	total_weighted_score = 0.0
	total_weight = 0.0
	
	for section_name, content in sections.items():
		critique = check_section_quality(section_name, content)
		section_critiques[section_name] = critique
		
		# Calculate weighted score
		weight = critique.get("weight", 0.1)
		total_weighted_score += critique["score"] * weight
		total_weight += weight
	
	# Check citation quality
	citation_critique = check_citation_quality(sections.get("references", ""), papers_count)
	section_critiques["citation_quality"] = citation_critique
	
	# Check coherence
	coherence_critique = check_coherence(sections)
	section_critiques["coherence"] = coherence_critique
	
	# Calculate overall score
	if total_weight > 0:
		base_score = total_weighted_score / total_weight
	else:
		base_score = 0.5
	
	# Adjust for citation and coherence
	overall_score = (
		base_score * 0.7 +
		citation_critique["score"] * 0.15 +
		coherence_critique["score"] * 0.15
	)
	
	# Collect all issues and suggestions
	all_issues = []
	all_suggestions = []
	priority_revisions = []
	
	for section_name, critique in section_critiques.items():
		for issue in critique.get("issues", []):
			all_issues.append(f"{section_name}: {issue}")
		for suggestion in critique.get("suggestions", []):
			all_suggestions.append(f"[{section_name}] {suggestion}")
		
		# Mark low-scoring sections for priority revision
		if critique.get("score", 1.0) < 0.6:
			priority_revisions.append(section_name)
	
	# Determine quality grade
	if overall_score >= 0.9:
		grade = "A"
		verdict = "Excellent quality, minor improvements possible"
	elif overall_score >= 0.8:
		grade = "B"
		verdict = "Good quality, some improvements recommended"
	elif overall_score >= 0.7:
		grade = "C"
		verdict = "Acceptable quality, several improvements needed"
	elif overall_score >= 0.6:
		grade = "D"
		verdict = "Below average, significant revisions required"
	else:
		grade = "F"
		verdict = "Poor quality, major revisions required"
	
	return {
		"overall_score": round(overall_score, 2),
		"grade": grade,
		"verdict": verdict,
		"section_critiques": section_critiques,
		"all_issues": all_issues,
		"all_suggestions": all_suggestions,
		"priority_revisions": priority_revisions,
		"total_issues": len(all_issues),
		"critique_date": datetime.now().isoformat()
	}


def generate_revised_review(review: Dict[str, Any], critique: Dict[str, Any]) -> Dict[str, Any]:
	"""
	Generate a revised version of the literature review based on critique.
	
	Args:
		review: Original review
		critique: Critique results
	
	Returns:
		Revised review with improvements
	"""
	sections = review.get("sections", {})
	section_critiques = critique.get("section_critiques", {})
	
	revised_sections = {}
	revision_log = []
	
	for section_name, content in sections.items():
		section_critique = section_critiques.get(section_name, {})
		issues = section_critique.get("issues", [])
		suggestions = section_critique.get("suggestions", [])
		
		if issues:
			revised_content = generate_revision(section_name, content, issues, suggestions)
			revised_sections[section_name] = revised_content
			revision_log.append({
				"section": section_name,
				"issues_addressed": issues,
				"changes_made": True
			})
		else:
			revised_sections[section_name] = content
			revision_log.append({
				"section": section_name,
				"issues_addressed": [],
				"changes_made": False
			})
	
	# Compile revised full text
	topic = review.get("topic", "Research Topic")
	
	revised_full_text = f"""# Literature Review: {topic.title()} (REVISED)

**Generated**: {review.get('generated_date', '')}
**Revised**: {datetime.now().strftime("%B %d, %Y")}
**Papers Reviewed**: {review.get('papers_count', 0)}
**Quality Score**: {critique.get('overall_score', 0):.0%} ({critique.get('grade', 'N/A')})

---

## Abstract

{revised_sections.get('abstract', '[Abstract pending]')}

---

{revised_sections.get('introduction', '[Introduction pending]')}

---

{revised_sections.get('methodology_comparison', '[Methodology comparison pending]')}

---

{revised_sections.get('results_synthesis', '[Results synthesis pending]')}

---

{revised_sections.get('conclusion', '[Conclusion pending]')}

---

{revised_sections.get('references', '[References pending]')}
"""
	
	return {
		"topic": topic,
		"revision_date": datetime.now().isoformat(),
		"original_score": critique.get("overall_score"),
		"sections": revised_sections,
		"full_text": revised_full_text,
		"word_count": count_words(revised_full_text),
		"revision_log": revision_log,
		"improvements_made": sum(1 for r in revision_log if r["changes_made"])
	}


def critique_drafts(
	drafts_path: str = DRAFTS_PATH,
	output_path: str = OUTPUT_PATH,
) -> Dict[str, Any]:
	"""
	Main entry point for critique and revision.
	"""
	if not os.path.exists(drafts_path):
		raise FileNotFoundError(f"Drafts file not found: {drafts_path}")

	data = load_json(drafts_path)
	
	# Get the literature review
	review = data.get("literature_review", {})
	
	if not review:
		logger.warning("No literature review found in drafts")
		return {"error": "No literature review found"}
	
	# Generate critique
	critique = critique_literature_review(review)
	
	# Generate revised version
	revised_review = generate_revised_review(review, critique)
	
	# Compile output
	summary = {
		"topic": review.get("topic"),
		"critique_date": datetime.now().isoformat(),
		"original_review": {
			"word_count": review.get("word_count", 0),
			"papers_count": review.get("papers_count", 0),
		},
		"critique": critique,
		"revised_review": revised_review,
		"improvement_summary": {
			"original_score": critique.get("overall_score"),
			"issues_identified": critique.get("total_issues", 0),
			"sections_revised": revised_review.get("improvements_made", 0),
			"priority_revisions": critique.get("priority_revisions", [])
		}
	}

	save_json(summary, output_path)
	
	logger.info("Critique complete")
	logger.info("  - Overall Score: %.0f%% (%s)", 
			   critique.get("overall_score", 0) * 100, 
			   critique.get("grade", "N/A"))
	logger.info("  - Issues Found: %d", critique.get("total_issues", 0))
	logger.info("  - Sections Revised: %d", revised_review.get("improvements_made", 0))
	
	return summary


if __name__ == "__main__":
	try:
		summary = critique_drafts()
		
		print("\n" + "=" * 60)
		print("CRITIQUE AND REVISION COMPLETE")
		print("=" * 60)
		
		critique = summary.get("critique", {})
		print(f"\n📊 Overall Score: {critique.get('overall_score', 0):.0%} ({critique.get('grade', 'N/A')})")
		print(f"📝 Verdict: {critique.get('verdict', 'N/A')}")
		
		print(f"\n🔍 Issues Identified: {critique.get('total_issues', 0)}")
		
		if critique.get("priority_revisions"):
			print(f"\n⚠️  Priority Revisions Needed:")
			for section in critique.get("priority_revisions", []):
				print(f"   - {section}")
		
		print(f"\n✅ Sections Revised: {summary.get('revised_review', {}).get('improvements_made', 0)}")
		
		print("\n📋 Suggestions:")
		for idx, suggestion in enumerate(critique.get("all_suggestions", [])[:5], 1):
			print(f"   {idx}. {suggestion}")
		
		if len(critique.get("all_suggestions", [])) > 5:
			print(f"   ... and {len(critique.get('all_suggestions', [])) - 5} more suggestions")
		
		print("=" * 60)
		
	except Exception as exc:
		logger.error("Critique generation failed: %s", exc)
		raise
