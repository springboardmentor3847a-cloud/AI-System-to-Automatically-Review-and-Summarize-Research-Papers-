"""
AI Paper Review System - Gradio UI
===================================
Complete academic interface for automated research paper review and literature synthesis.

**FEATURES:**
- Topic input with research parameters
- Paper ranking display with scores
- Generated literature review sections
- Critique and revision functionality
- Export to PDF/DOCX
- Professional academic styling
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Ensure project root on path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Change to project root for relative paths
os.chdir(ROOT)

import gradio as gr

# Import modules
from modules.search_papers import search_papers, rank_papers, save_metadata, get_ranking_weights
from modules.download_pdf import download_papers, save_download_metadata
from modules.extract_text import extract_text_for_papers
from modules.analyze_text import process_analysis
from modules.generate_draft import generate_drafts
from modules.critique_draft import critique_drafts


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_ranking_table(papers: List[Dict[str, Any]]) -> str:
    """Format papers into a ranking table."""
    if not papers:
        return "No papers found."
    
    table = "| Rank | Score | Title | Year | Citations | PDF |\n"
    table += "|------|-------|-------|------|-----------|-----|\n"
    
    for paper in papers:
        rank = paper.get("rank", "-")
        score = paper.get("ranking_score", 0)
        title = paper.get("title", "Unknown")[:50] + "..." if len(paper.get("title", "")) > 50 else paper.get("title", "Unknown")
        year = paper.get("year", "N/A")
        citations = paper.get("citation_count", 0)
        pdf = "✅" if paper.get("pdf_available") else "❌"
        
        table += f"| #{rank} | {score:.3f} | {title} | {year} | {citations} | {pdf} |\n"
    
    return table


def format_score_breakdown(papers: List[Dict[str, Any]]) -> str:
    """Format detailed score breakdown."""
    if not papers:
        return "No papers to display."
    
    output = "## 📊 Ranking Score Breakdown\n\n"
    output += "**Weights Applied:**\n"
    weights = get_ranking_weights()
    for key, value in weights.items():
        output += f"- {key.replace('_', ' ').title()}: {value:.0%}\n"
    output += "\n---\n\n"
    
    for paper in papers[:5]:  # Top 5
        output += f"### #{paper.get('rank', '?')} - {paper.get('title', 'Unknown')[:60]}...\n\n"
        
        breakdown = paper.get("score_breakdown", {})
        output += f"- **Total Score**: {paper.get('ranking_score', 0):.4f}\n"
        output += f"- Relevance: {breakdown.get('relevance', 0):.3f}\n"
        output += f"- Recency: {breakdown.get('recency', 0):.3f}\n"
        output += f"- Citations: {breakdown.get('citations', 0):.3f}\n"
        output += f"- Author Score: {breakdown.get('author_score', 0):.3f}\n"
        output += f"- PDF Available: {breakdown.get('pdf_available', 0):.0f}\n\n"
    
    return output


def run_full_pipeline(topic: str, limit: int, min_year: int, min_citations: int, top_n: int, progress=gr.Progress()):
    """Run the complete paper processing pipeline with progress tracking."""
    try:
        results = {
            "status": "running",
            "steps": [],
            "papers_ranked": [],
            "papers_selected": [],
            "errors": []
        }
        
        # Step 1: Search for papers
        progress(0.1, desc="🔍 Searching for papers...")
        results["steps"].append("Step 1: Searching papers...")
        
        search_results = search_papers(
            topic=topic,
            limit=int(limit),
            year_min=int(min_year),
            min_citations=int(min_citations)
        )
        
        papers = search_results.get("papers", [])
        results["steps"].append(f"  ✓ Found {len(papers)} papers")
        
        if not papers:
            return {
                "status": "error",
                "message": "No papers found for the given criteria",
                "papers_ranked": [],
                "papers_selected": []
            }, "No papers found", "", "", "", ""
        
        # Step 2: Rank papers
        progress(0.2, desc="📊 Ranking papers...")
        results["steps"].append("Step 2: Ranking papers...")
        
        ranked_papers = rank_papers(papers, topic, top_n=int(top_n))
        results["papers_ranked"] = ranked_papers
        results["steps"].append(f"  ✓ Ranked {len(ranked_papers)} papers (selected top {top_n})")
        
        # Save search results with ranking
        search_results["papers"] = ranked_papers
        search_results["ranking_applied"] = True
        search_results["topic"] = topic
        save_metadata(search_results)
        
        # Step 3: Filter papers with PDFs
        progress(0.3, desc="📁 Filtering papers with PDFs...")
        papers_with_pdf = [p for p in ranked_papers if p.get("pdf_available")]
        results["steps"].append(f"Step 3: {len(papers_with_pdf)}/{len(ranked_papers)} papers have PDFs available")
        
        if not papers_with_pdf:
            return {
                "status": "partial",
                "message": "No papers with available PDFs",
                "papers_ranked": ranked_papers,
                "papers_selected": []
            }, format_ranking_table(ranked_papers), format_score_breakdown(ranked_papers), "", "", ""
        
        # Step 4: Download PDFs
        progress(0.4, desc="⬇️ Downloading PDFs...")
        results["steps"].append("Step 4: Downloading PDFs...")
        
        downloaded_papers = download_papers(papers_with_pdf)
        results["papers_selected"] = downloaded_papers
        results["steps"].append(f"  ✓ Downloaded {len(downloaded_papers)} PDFs")
        
        if not downloaded_papers:
            return {
                "status": "partial",
                "message": "PDF download failed",
                "papers_ranked": ranked_papers,
                "papers_selected": []
            }, format_ranking_table(ranked_papers), format_score_breakdown(ranked_papers), "", "", ""
        
        # Step 5: Extract text
        progress(0.5, desc="📄 Extracting text...")
        results["steps"].append("Step 5: Extracting text from PDFs...")
        
        downloaded_papers = extract_text_for_papers(downloaded_papers)
        save_download_metadata(downloaded_papers, "selected_papers.json")
        
        extracted_count = sum(1 for p in downloaded_papers if p.get("extraction_status") == "success")
        results["steps"].append(f"  ✓ Extracted text from {extracted_count} papers")
        
        # Step 6: Analyze text
        progress(0.6, desc="🔬 Analyzing papers...")
        results["steps"].append("Step 6: Analyzing extracted text...")
        
        analysis_summary = process_analysis()
        results["steps"].append(f"  ✓ Analysis complete: {analysis_summary.get('success', 0)} papers analyzed")
        
        # Step 7: Generate literature review
        progress(0.8, desc="📝 Generating literature review...")
        results["steps"].append("Step 7: Generating literature review...")
        
        drafts_summary = generate_drafts()
        review = drafts_summary.get("literature_review", {})
        results["steps"].append(f"  ✓ Literature review generated ({review.get('word_count', 0)} words)")
        
        # Step 8: Critique and revise
        progress(0.9, desc="✍️ Critiquing and revising...")
        results["steps"].append("Step 8: Critiquing and revising...")
        
        critique_summary = critique_drafts()
        critique = critique_summary.get("critique", {})
        results["steps"].append(f"  ✓ Critique complete: Score {critique.get('overall_score', 0):.0%} ({critique.get('grade', 'N/A')})")
        
        # Finalize
        progress(1.0, desc="✅ Complete!")
        results["status"] = "success"
        results["steps"].append("\n✅ Pipeline completed successfully!")
        
        # Format outputs
        ranking_table = format_ranking_table(ranked_papers)
        score_breakdown = format_score_breakdown(ranked_papers)
        
        # Get literature review sections
        sections = review.get("sections", {})
        abstract = sections.get("abstract", "Abstract not generated.")
        full_review = review.get("full_text", "Literature review not generated.")
        
        # Format critique
        critique_output = format_critique_output(critique_summary)
        
        return (
            results,
            ranking_table,
            score_breakdown,
            abstract,
            full_review,
            critique_output
        )
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return (
            {"status": "error", "message": str(e), "trace": error_trace},
            "Error occurred",
            "",
            "",
            "",
            f"Error: {str(e)}"
        )


def format_critique_output(critique_summary: Dict[str, Any]) -> str:
    """Format critique results for display."""
    if not critique_summary:
        return "No critique available."
    
    critique = critique_summary.get("critique", {})
    
    output = f"""## 📋 Literature Review Critique

### Overall Assessment
- **Score**: {critique.get('overall_score', 0):.0%} ({critique.get('grade', 'N/A')})
- **Verdict**: {critique.get('verdict', 'N/A')}
- **Total Issues**: {critique.get('total_issues', 0)}

### Section Scores
"""
    
    section_critiques = critique.get("section_critiques", {})
    for section_name, section_critique in section_critiques.items():
        if section_name in ["citation_quality", "coherence"]:
            continue
        score = section_critique.get("score", 0)
        emoji = "✅" if score >= 0.8 else "⚠️" if score >= 0.6 else "❌"
        output += f"- {emoji} **{section_name.replace('_', ' ').title()}**: {score:.0%}\n"
    
    output += "\n### Suggestions for Improvement\n"
    suggestions = critique.get("all_suggestions", [])
    for idx, suggestion in enumerate(suggestions[:10], 1):
        output += f"{idx}. {suggestion}\n"
    
    if len(suggestions) > 10:
        output += f"\n*...and {len(suggestions) - 10} more suggestions*\n"
    
    # Add revised review info
    revised = critique_summary.get("revised_review", {})
    if revised:
        output += f"\n### Revision Summary\n"
        output += f"- Sections Revised: {revised.get('improvements_made', 0)}\n"
        output += f"- New Word Count: {revised.get('word_count', 0)}\n"
    
    return output


def load_existing_data() -> Tuple[str, str, str, str]:
    """Load existing data from files."""
    ranking_table = "No existing data."
    score_breakdown = ""
    review = "No review generated."
    critique = "No critique available."
    
    try:
        # Load paper metadata
        papers_path = os.path.join(ROOT, "data/metadata/paper_metadata.json")
        if os.path.exists(papers_path):
            with open(papers_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            papers = data.get("papers", [])
            if papers and "rank" in papers[0]:
                ranking_table = format_ranking_table(papers)
                score_breakdown = format_score_breakdown(papers)
        
        # Load literature review
        drafts_path = os.path.join(ROOT, "data/metadata/drafts.json")
        if os.path.exists(drafts_path):
            with open(drafts_path, "r", encoding="utf-8") as f:
                drafts_data = json.load(f)
            lit_review = drafts_data.get("literature_review", {})
            review = lit_review.get("full_text", "No review in file.")
        
        # Load critique
        critique_path = os.path.join(ROOT, "data/metadata/critiques.json")
        if os.path.exists(critique_path):
            with open(critique_path, "r", encoding="utf-8") as f:
                critique_data = json.load(f)
            critique = format_critique_output(critique_data)
        
    except Exception as e:
        ranking_table = f"Error loading data: {str(e)}"
    
    return ranking_table, score_breakdown, review, critique


def run_critique_revision():
    """Run critique and revision on existing draft."""
    try:
        critique_summary = critique_drafts()
        
        # Also get revised review
        revised = critique_summary.get("revised_review", {})
        revised_text = revised.get("full_text", "No revision generated.")
        
        critique_output = format_critique_output(critique_summary)
        
        return critique_output, revised_text
    except Exception as e:
        return f"Error: {str(e)}", ""


def export_to_markdown():
    """Export literature review to Markdown file."""
    try:
        drafts_path = os.path.join(ROOT, "data/metadata/drafts.json")
        if not os.path.exists(drafts_path):
            return "No literature review found to export."
        
        with open(drafts_path, "r", encoding="utf-8") as f:
            drafts_data = json.load(f)
        
        review = drafts_data.get("literature_review", {})
        full_text = review.get("full_text", "")
        
        if not full_text:
            return "Literature review is empty."
        
        # Save to file
        output_path = os.path.join(ROOT, "data", "literature_review.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        
        return f"✅ Exported to: {output_path}"
    except Exception as e:
        return f"❌ Export failed: {str(e)}"


def export_to_docx():
    """Export literature review to DOCX file."""
    try:
        # Check if python-docx is available
        try:
            from docx import Document
            from docx.shared import Inches, Pt
            from docx.enum.text import WD_ALIGN_PARAGRAPH
        except ImportError:
            return "❌ python-docx not installed. Run: pip install python-docx"
        
        drafts_path = os.path.join(ROOT, "data/metadata/drafts.json")
        if not os.path.exists(drafts_path):
            return "No literature review found to export."
        
        with open(drafts_path, "r", encoding="utf-8") as f:
            drafts_data = json.load(f)
        
        review = drafts_data.get("literature_review", {})
        sections = review.get("sections", {})
        topic = review.get("topic", "Literature Review")
        
        # Create document
        doc = Document()
        
        # Title
        title = doc.add_heading(f"Literature Review: {topic.title()}", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Metadata
        doc.add_paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}")
        doc.add_paragraph(f"Papers Reviewed: {review.get('papers_count', 0)}")
        doc.add_paragraph("")
        
        # Sections
        section_order = ["abstract", "introduction", "methodology_comparison", "results_synthesis", "conclusion", "references"]
        
        for section_name in section_order:
            content = sections.get(section_name, "")
            if content:
                # Add section heading
                heading = section_name.replace("_", " ").title()
                doc.add_heading(heading, 1)
                
                # Add content (basic - strips markdown)
                clean_content = content.replace("## ", "").replace("### ", "").replace("**", "").replace("*", "")
                for para in clean_content.split("\n\n"):
                    if para.strip():
                        doc.add_paragraph(para.strip())
        
        # Save
        output_path = os.path.join(ROOT, "data", "literature_review.docx")
        doc.save(output_path)
        
        return f"✅ Exported to: {output_path}"
    except Exception as e:
        return f"❌ Export failed: {str(e)}"


def export_to_pdf():
    """Export literature review to PDF file."""
    try:
        # Check if required libraries are available
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        except ImportError:
            return "❌ reportlab not installed. Run: pip install reportlab"
        
        drafts_path = os.path.join(ROOT, "data/metadata/drafts.json")
        if not os.path.exists(drafts_path):
            return "No literature review found to export."
        
        with open(drafts_path, "r", encoding="utf-8") as f:
            drafts_data = json.load(f)
        
        review = drafts_data.get("literature_review", {})
        sections = review.get("sections", {})
        topic = review.get("topic", "Literature Review")
        
        # Create PDF
        output_path = os.path.join(ROOT, "data", "literature_review.pdf")
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            leading=14
        )
        
        # Build content
        story = []
        
        # Title
        story.append(Paragraph(f"Literature Review: {topic.title()}", title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Paragraph(f"Papers Reviewed: {review.get('papers_count', 0)}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Sections
        section_order = ["abstract", "introduction", "methodology_comparison", "results_synthesis", "conclusion", "references"]
        
        for section_name in section_order:
            content = sections.get(section_name, "")
            if content:
                # Section heading
                heading = section_name.replace("_", " ").title()
                story.append(Paragraph(heading, heading_style))
                
                # Clean content (remove markdown)
                clean_content = content.replace("## ", "").replace("### ", "").replace("**", "").replace("*", "")
                clean_content = clean_content.replace("|", " ").replace("-", "")  # Remove table markers
                
                for para in clean_content.split("\n\n"):
                    if para.strip() and not para.strip().startswith("|"):
                        # Escape special characters
                        safe_para = para.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        story.append(Paragraph(safe_para, body_style))
        
        doc.build(story)
        
        return f"✅ Exported to: {output_path}"
    except Exception as e:
        return f"❌ Export failed: {str(e)}"


# =============================================================================
# GRADIO INTERFACE
# =============================================================================

# Custom CSS for academic styling
CUSTOM_CSS = """
.gradio-container {
    font-family: 'Georgia', 'Times New Roman', serif !important;
}
.markdown-text h1 {
    color: #1a365d !important;
    border-bottom: 2px solid #2c5282 !important;
}
.markdown-text h2 {
    color: #2c5282 !important;
}
.markdown-text table {
    border-collapse: collapse !important;
    width: 100% !important;
}
.markdown-text th, .markdown-text td {
    border: 1px solid #cbd5e0 !important;
    padding: 8px !important;
    text-align: left !important;
}
.markdown-text th {
    background-color: #edf2f7 !important;
}
"""

with gr.Blocks() as demo:
    
    # Header
    gr.Markdown("""
    # 📚 AI System for Automated Research Paper Review and Summarization
    
    **An advanced academic tool for automated literature review generation**
    
    This system automatically searches, ranks, downloads, analyzes, and synthesizes research papers
    into a structured academic literature review with critique and revision capabilities.
    """)
    
    with gr.Tabs():
        # =================================================================
        # TAB 1: RUN PIPELINE
        # =================================================================
        with gr.TabItem("🚀 Run Pipeline", id="pipeline"):
            gr.Markdown("### Configure and Execute the Research Pipeline")
            
            with gr.Row():
                with gr.Column(scale=2):
                    topic_input = gr.Textbox(
                        label="Research Topic",
                        placeholder="Enter your research topic (e.g., 'deep learning natural language processing')",
                        value="deep learning natural language processing",
                        info="Be specific for better results"
                    )
                
                with gr.Column(scale=1):
                    limit_slider = gr.Slider(
                        minimum=5,
                        maximum=20,
                        value=10,
                        step=1,
                        label="Papers to Search",
                        info="Number of papers to retrieve from Semantic Scholar"
                    )
            
            with gr.Row():
                min_year_slider = gr.Slider(
                    minimum=2015,
                    maximum=2026,
                    value=2020,
                    step=1,
                    label="Minimum Publication Year"
                )
                min_citations_slider = gr.Slider(
                    minimum=0,
                    maximum=500,
                    value=50,
                    step=10,
                    label="Minimum Citation Count"
                )
                top_n_slider = gr.Slider(
                    minimum=3,
                    maximum=10,
                    value=3,
                    step=1,
                    label="Top Papers to Select",
                    info="Number of highest-ranked papers to process"
                )
            
            run_btn = gr.Button("▶️ Run Full Pipeline", variant="primary", size="lg")
            
            with gr.Row():
                status_output = gr.JSON(label="Pipeline Status", scale=1)
            
            gr.Markdown("---")
            gr.Markdown("### 📊 Paper Ranking Results")
            
            with gr.Row():
                with gr.Column():
                    ranking_output = gr.Markdown(label="Ranked Papers Table")
                with gr.Column():
                    breakdown_output = gr.Markdown(label="Score Breakdown")
            
            gr.Markdown("---")
            gr.Markdown("### 📝 Generated Literature Review")
            
            abstract_output = gr.Textbox(
                label="Abstract (≤100 words)",
                lines=4,
                interactive=False
            )
            
            review_output = gr.Markdown(label="Full Literature Review")
            
            gr.Markdown("---")
            gr.Markdown("### ✍️ Critique and Quality Assessment")
            
            critique_output = gr.Markdown(label="Critique Results")
            
            # Connect button
            run_btn.click(
                fn=run_full_pipeline,
                inputs=[topic_input, limit_slider, min_year_slider, min_citations_slider, top_n_slider],
                outputs=[status_output, ranking_output, breakdown_output, abstract_output, review_output, critique_output]
            )
        
        # =================================================================
        # TAB 2: VIEW & REVISE
        # =================================================================
        with gr.TabItem("📖 View & Revise", id="view"):
            gr.Markdown("### View Existing Results and Perform Revisions")
            
            with gr.Row():
                load_btn = gr.Button("🔄 Load Existing Data", variant="secondary")
                revise_btn = gr.Button("✍️ Run Critique & Revision", variant="primary")
            
            with gr.Row():
                with gr.Column():
                    view_ranking = gr.Markdown(label="Paper Rankings")
                with gr.Column():
                    view_breakdown = gr.Markdown(label="Score Details")
            
            gr.Markdown("---")
            gr.Markdown("### Literature Review")
            view_review = gr.Markdown(label="Review Content")
            
            gr.Markdown("---")
            gr.Markdown("### Critique & Suggestions")
            
            with gr.Row():
                with gr.Column():
                    view_critique = gr.Markdown(label="Critique")
                with gr.Column():
                    view_revised = gr.Markdown(label="Revised Review")
            
            load_btn.click(
                fn=load_existing_data,
                inputs=[],
                outputs=[view_ranking, view_breakdown, view_review, view_critique]
            )
            
            revise_btn.click(
                fn=run_critique_revision,
                inputs=[],
                outputs=[view_critique, view_revised]
            )
        
        # =================================================================
        # TAB 3: EXPORT
        # =================================================================
        with gr.TabItem("📤 Export", id="export"):
            gr.Markdown("### Export Literature Review")
            gr.Markdown("Export the generated literature review to various formats for academic use.")
            
            with gr.Row():
                export_md_btn = gr.Button("📄 Export to Markdown", variant="secondary")
                export_docx_btn = gr.Button("📝 Export to DOCX", variant="secondary")
                export_pdf_btn = gr.Button("📑 Export to PDF", variant="secondary")
            
            export_status = gr.Textbox(label="Export Status", lines=2, interactive=False)
            
            gr.Markdown("""
            **Export Locations:**
            - All exports are saved to the `data/` folder
            - Markdown: `data/literature_review.md`
            - DOCX: `data/literature_review.docx`
            - PDF: `data/literature_review.pdf`
            
            **Note:** DOCX export requires `python-docx`. PDF export requires `reportlab`.
            Install with: `pip install python-docx reportlab`
            """)
            
            export_md_btn.click(fn=export_to_markdown, inputs=[], outputs=[export_status])
            export_docx_btn.click(fn=export_to_docx, inputs=[], outputs=[export_status])
            export_pdf_btn.click(fn=export_to_pdf, inputs=[], outputs=[export_status])
        
        # =================================================================
        # TAB 4: ABOUT
        # =================================================================
        with gr.TabItem("ℹ️ About", id="about"):
            gr.Markdown("""
            ## AI System for Automated Research Paper Review and Summarization
            
            ### 🎯 System Objectives
            
            This system automates the process of creating academic literature reviews by:
            
            1. **Searching** for research papers on any topic via Semantic Scholar API
            2. **Ranking** papers using a weighted scoring algorithm
            3. **Downloading** and validating PDF files
            4. **Extracting** structured sections (Abstract, Introduction, Methods, Results, Conclusion)
            5. **Analyzing** content and comparing across papers
            6. **Generating** a comprehensive literature review
            7. **Critiquing** and revising the generated content
            
            ---
            
            ### 📊 Ranking Algorithm
            
            Papers are scored using the following weighted formula:
            
            ```
            Score = w₁×Relevance + w₂×Recency + w₃×Citations + w₄×AuthorScore + w₅×PDFAvailable
            ```
            
            **Default Weights:**
            - Relevance (w₁): 30% - Topic match in title and abstract
            - Recency (w₂): 20% - Publication year freshness
            - Citations (w₃): 25% - Citation count (log-normalized)
            - Author Score (w₄): 10% - Author collaboration and impact
            - PDF Available (w₅): 15% - Bonus for accessible PDF
            
            ---
            
            ### 📋 Literature Review Structure
            
            The generated review follows academic standards:
            
            1. **Abstract** (≤100 words) - Concise summary
            2. **Introduction** - Context, objectives, papers reviewed
            3. **Methodology Comparison** - Cross-paper methodology analysis
            4. **Results Synthesis** - Key findings comparison
            5. **Conclusion** - Summary and research gaps
            6. **References** - APA 7th edition formatted citations
            
            ---
            
            ### 📁 Data Files
            
            | File | Description |
            |------|-------------|
            | `data/metadata/paper_metadata.json` | Search results with rankings |
            | `data/metadata/selected_papers.json` | Downloaded papers metadata |
            | `data/metadata/analyzed_papers.json` | Analysis results |
            | `data/metadata/drafts.json` | Generated literature review |
            | `data/metadata/critiques.json` | Critique and revisions |
            | `data/pdfs/` | Downloaded PDF files |
            | `data/extracted/` | Extracted text files |
            
            ---
            
            ### 🔧 Technical Requirements
            
            - Python 3.8+
            - Semantic Scholar API access
            - Required packages: `semanticscholar`, `PyMuPDF`, `gradio`, `requests`
            - Optional: `python-docx`, `reportlab` (for export)
            
            ---
            
            ### 🎓 Academic Integrity
            
            - All generated content is grounded in actual paper content
            - No hallucinated information
            - Proper citations included
            - Designed for research assistance, not plagiarism
            """)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AI Paper Review System - Starting...")
    print("=" * 60)
    print("\nAccess the interface at: http://127.0.0.1:7860")
    print("\nPress Ctrl+C to stop the server.\n")
    
    # Launch Gradio app (use defaults for Gradio 6.x compatibility)
    demo.launch()
