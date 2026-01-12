"""
LangGraph Workflow Orchestration Module
========================================
Implements the paper review pipeline as a directed graph per the architecture:

start → process_input → planner → researcher → search_articles
→ article_decisions → download_articles → paper_analyzer
→ write_* (parallel) → aggregate_paper → critique_paper
→ revise → revise_paper → final_draft → end

Uses LangGraph for state management and execution flow control.
"""

import logging
import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass, field

# Setup logging
LOG_DIR = "data/logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "workflow.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# =============================================================================
# STATE DEFINITIONS
# =============================================================================

class PipelineState(TypedDict, total=False):
    """State object passed through the workflow graph."""
    # Input
    topic: str
    limit: int
    year_min: Optional[int]
    min_citations: Optional[int]
    top_n: int
    
    # Search phase
    search_results: List[Dict[str, Any]]
    ranked_papers: List[Dict[str, Any]]
    selected_papers: List[Dict[str, Any]]
    
    # Download phase
    downloaded_papers: List[Dict[str, Any]]
    papers_with_text: List[Dict[str, Any]]
    
    # Analysis phase
    analysis_results: Dict[str, Any]
    cross_analysis: Dict[str, Any]
    
    # Writing phase
    sections: Dict[str, str]
    literature_review: Dict[str, Any]
    
    # Review phase
    critique: Dict[str, Any]
    revised_review: Dict[str, Any]
    final_draft: Dict[str, Any]
    
    # Meta
    errors: List[str]
    current_step: str
    status: str
    execution_log: List[Dict[str, Any]]


def create_initial_state(
    topic: str,
    limit: int = 10,
    year_min: Optional[int] = None,
    min_citations: Optional[int] = None,
    top_n: int = 3
) -> PipelineState:
    """Create initial pipeline state."""
    return PipelineState(
        topic=topic,
        limit=limit,
        year_min=year_min,
        min_citations=min_citations,
        top_n=top_n,
        search_results=[],
        ranked_papers=[],
        selected_papers=[],
        downloaded_papers=[],
        papers_with_text=[],
        analysis_results={},
        cross_analysis={},
        sections={},
        literature_review={},
        critique={},
        revised_review={},
        final_draft={},
        errors=[],
        current_step="start",
        status="initialized",
        execution_log=[]
    )


def log_step(state: PipelineState, step_name: str, status: str, details: Dict[str, Any] = None) -> None:
    """Log a workflow step execution."""
    entry = {
        "step": step_name,
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "details": details or {}
    }
    state["execution_log"].append(entry)
    logger.info(f"[{step_name}] {status} - {details}")


# =============================================================================
# WORKFLOW NODES (per PDF architecture)
# =============================================================================

def process_input(state: PipelineState) -> PipelineState:
    """
    Node: process_input
    Validate and normalize input parameters.
    """
    log_step(state, "process_input", "started")
    
    # Validate topic
    topic = state.get("topic", "").strip()
    if not topic or len(topic) < 3:
        state["errors"].append("Topic must be at least 3 characters")
        state["status"] = "error"
        return state
    
    # Normalize parameters
    state["limit"] = min(max(int(state.get("limit", 10)), 5), 20)
    state["top_n"] = min(max(int(state.get("top_n", 3)), 1), 10)
    
    if state.get("year_min"):
        state["year_min"] = max(int(state["year_min"]), 2000)
    
    if state.get("min_citations"):
        state["min_citations"] = max(int(state["min_citations"]), 0)
    
    state["current_step"] = "process_input"
    log_step(state, "process_input", "completed", {"topic": topic, "limit": state["limit"]})
    return state


def planner(state: PipelineState) -> PipelineState:
    """
    Node: planner
    Determine search strategy and execution plan.
    """
    log_step(state, "planner", "started")
    
    # Define execution plan based on input
    plan = {
        "search_strategy": "semantic_scholar",
        "ranking_criteria": ["pdf_available", "relevance", "recency", "citations", "author_score"],
        "sections_to_generate": ["abstract", "introduction", "methodology_comparison", "results_synthesis", "conclusion", "references"],
        "enable_critique": True,
        "enable_revision": True
    }
    
    state["execution_plan"] = plan
    state["current_step"] = "planner"
    log_step(state, "planner", "completed", plan)
    return state


def researcher(state: PipelineState) -> PipelineState:
    """
    Node: researcher
    Execute paper search using Semantic Scholar API.
    """
    log_step(state, "researcher", "started")
    
    try:
        from modules.search_papers import search_papers
        
        results = search_papers(
            topic=state["topic"],
            limit=state["limit"],
            year_min=state.get("year_min"),
            min_citations=state.get("min_citations")
        )
        
        state["search_results"] = results.get("papers", [])
        state["current_step"] = "researcher"
        log_step(state, "researcher", "completed", {"papers_found": len(state["search_results"])})
        
    except Exception as e:
        state["errors"].append(f"Search failed: {str(e)}")
        state["status"] = "error"
        log_step(state, "researcher", "failed", {"error": str(e)})
    
    return state


def article_decisions(state: PipelineState) -> PipelineState:
    """
    Node: article_decisions
    Rank papers and select top N with available PDFs.
    """
    log_step(state, "article_decisions", "started")
    
    try:
        from modules.search_papers import rank_papers
        
        papers = state.get("search_results", [])
        if not papers:
            state["errors"].append("No papers to rank")
            return state
        
        # Rank all papers
        ranked = rank_papers(papers, state["topic"], top_n=len(papers))
        state["ranked_papers"] = ranked
        
        # Select top N papers WITH PDF availability (mandatory per PDF spec)
        papers_with_pdf = [p for p in ranked if p.get("pdf_available")]
        state["selected_papers"] = papers_with_pdf[:state["top_n"]]
        
        state["current_step"] = "article_decisions"
        log_step(state, "article_decisions", "completed", {
            "total_ranked": len(ranked),
            "with_pdf": len(papers_with_pdf),
            "selected": len(state["selected_papers"])
        })
        
    except Exception as e:
        state["errors"].append(f"Ranking failed: {str(e)}")
        log_step(state, "article_decisions", "failed", {"error": str(e)})
    
    return state


def download_articles(state: PipelineState) -> PipelineState:
    """
    Node: download_articles
    Download PDFs for selected papers.
    """
    log_step(state, "download_articles", "started")
    
    try:
        from modules.download_pdf import download_papers, save_download_metadata
        
        papers = state.get("selected_papers", [])
        if not papers:
            state["errors"].append("No papers to download")
            return state
        
        downloaded = download_papers(papers)
        save_download_metadata(downloaded, "selected_papers.json")
        
        state["downloaded_papers"] = downloaded
        state["current_step"] = "download_articles"
        log_step(state, "download_articles", "completed", {"downloaded": len(downloaded)})
        
    except Exception as e:
        state["errors"].append(f"Download failed: {str(e)}")
        log_step(state, "download_articles", "failed", {"error": str(e)})
    
    return state


def paper_analyzer(state: PipelineState) -> PipelineState:
    """
    Node: paper_analyzer
    Extract text and analyze papers.
    """
    log_step(state, "paper_analyzer", "started")
    
    try:
        from modules.extract_text import extract_text_for_papers
        from modules.download_pdf import save_download_metadata
        from modules.analyze_text import process_analysis
        
        papers = state.get("downloaded_papers", [])
        if not papers:
            state["errors"].append("No papers to analyze")
            return state
        
        # Extract text
        papers_with_text = extract_text_for_papers(papers)
        save_download_metadata(papers_with_text, "selected_papers.json")
        state["papers_with_text"] = papers_with_text
        
        # Analyze
        analysis = process_analysis()
        state["analysis_results"] = analysis
        state["cross_analysis"] = analysis.get("cross_analysis", {})
        
        state["current_step"] = "paper_analyzer"
        log_step(state, "paper_analyzer", "completed", {
            "extracted": len([p for p in papers_with_text if p.get("extraction_status") == "success"]),
            "analyzed": analysis.get("success", 0)
        })
        
    except Exception as e:
        state["errors"].append(f"Analysis failed: {str(e)}")
        log_step(state, "paper_analyzer", "failed", {"error": str(e)})
    
    return state


def aggregate_paper(state: PipelineState) -> PipelineState:
    """
    Node: aggregate_paper
    Generate literature review from analysis.
    """
    log_step(state, "aggregate_paper", "started")
    
    try:
        from modules.generate_draft import generate_drafts
        
        drafts = generate_drafts()
        state["literature_review"] = drafts.get("literature_review", {})
        state["sections"] = state["literature_review"].get("sections", {})
        
        state["current_step"] = "aggregate_paper"
        log_step(state, "aggregate_paper", "completed", {
            "word_count": state["literature_review"].get("word_count", 0),
            "sections": list(state["sections"].keys())
        })
        
    except Exception as e:
        state["errors"].append(f"Draft generation failed: {str(e)}")
        log_step(state, "aggregate_paper", "failed", {"error": str(e)})
    
    return state


def critique_paper(state: PipelineState) -> PipelineState:
    """
    Node: critique_paper
    Critique the generated literature review.
    """
    log_step(state, "critique_paper", "started")
    
    try:
        from modules.critique_draft import critique_drafts
        
        critique_result = critique_drafts()
        state["critique"] = critique_result.get("critique", {})
        
        state["current_step"] = "critique_paper"
        log_step(state, "critique_paper", "completed", {
            "score": state["critique"].get("overall_score", 0),
            "issues": state["critique"].get("total_issues", 0)
        })
        
    except Exception as e:
        state["errors"].append(f"Critique failed: {str(e)}")
        log_step(state, "critique_paper", "failed", {"error": str(e)})
    
    return state


def revise_paper(state: PipelineState) -> PipelineState:
    """
    Node: revise_paper
    Apply revisions based on critique.
    """
    log_step(state, "revise_paper", "started")
    
    try:
        from modules.critique_draft import load_json
        
        # Load the critique data which includes revised review
        critique_path = "data/metadata/critiques.json"
        if os.path.exists(critique_path):
            critique_data = load_json(critique_path)
            state["revised_review"] = critique_data.get("revised_review", {})
        
        state["current_step"] = "revise_paper"
        log_step(state, "revise_paper", "completed", {
            "improvements": state["revised_review"].get("improvements_made", 0)
        })
        
    except Exception as e:
        state["errors"].append(f"Revision failed: {str(e)}")
        log_step(state, "revise_paper", "failed", {"error": str(e)})
    
    return state


def final_draft(state: PipelineState) -> PipelineState:
    """
    Node: final_draft
    Compile final output.
    """
    log_step(state, "final_draft", "started")
    
    # Use revised if available, otherwise original
    if state.get("revised_review", {}).get("full_text"):
        final = state["revised_review"]
    else:
        final = state["literature_review"]
    
    state["final_draft"] = {
        "topic": state["topic"],
        "papers_reviewed": len(state.get("selected_papers", [])),
        "sections": state.get("sections", {}),
        "full_text": final.get("full_text", ""),
        "word_count": final.get("word_count", 0),
        "quality_score": state.get("critique", {}).get("overall_score", 0),
        "generated_at": datetime.now().isoformat()
    }
    
    state["status"] = "completed"
    state["current_step"] = "final_draft"
    log_step(state, "final_draft", "completed", {
        "word_count": state["final_draft"]["word_count"],
        "quality_score": state["final_draft"]["quality_score"]
    })
    
    return state


# =============================================================================
# WORKFLOW EXECUTION
# =============================================================================

def run_pipeline(
    topic: str,
    limit: int = 10,
    year_min: Optional[int] = None,
    min_citations: Optional[int] = None,
    top_n: int = 3,
    progress_callback=None
) -> PipelineState:
    """
    Execute the full paper review pipeline.
    
    Args:
        topic: Research topic to search
        limit: Maximum papers to search
        year_min: Minimum publication year
        min_citations: Minimum citation count
        top_n: Number of top papers to select
        progress_callback: Optional callback for progress updates
    
    Returns:
        Final pipeline state with all results
    """
    logger.info("=" * 60)
    logger.info("STARTING PAPER REVIEW PIPELINE")
    logger.info("=" * 60)
    
    # Initialize state
    state = create_initial_state(
        topic=topic,
        limit=limit,
        year_min=year_min,
        min_citations=min_citations,
        top_n=top_n
    )
    
    # Define execution order (per PDF architecture)
    workflow_steps = [
        ("process_input", process_input, 0.05),
        ("planner", planner, 0.10),
        ("researcher", researcher, 0.20),
        ("article_decisions", article_decisions, 0.30),
        ("download_articles", download_articles, 0.45),
        ("paper_analyzer", paper_analyzer, 0.60),
        ("aggregate_paper", aggregate_paper, 0.75),
        ("critique_paper", critique_paper, 0.85),
        ("revise_paper", revise_paper, 0.92),
        ("final_draft", final_draft, 1.0)
    ]
    
    # Execute workflow
    for step_name, step_fn, progress in workflow_steps:
        if state.get("status") == "error":
            logger.warning(f"Skipping {step_name} due to previous error")
            continue
        
        if progress_callback:
            progress_callback(progress, f"Executing: {step_name}")
        
        try:
            state = step_fn(state)
        except Exception as e:
            state["errors"].append(f"{step_name}: {str(e)}")
            state["status"] = "error"
            logger.error(f"Pipeline failed at {step_name}: {str(e)}")
            break
    
    # Save execution log
    log_path = os.path.join(LOG_DIR, "workflow_execution.json")
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump({
            "topic": topic,
            "status": state["status"],
            "execution_log": state["execution_log"],
            "errors": state["errors"],
            "completed_at": datetime.now().isoformat()
        }, f, indent=2)
    
    logger.info("=" * 60)
    logger.info(f"PIPELINE COMPLETED - Status: {state['status']}")
    logger.info("=" * 60)
    
    return state


# =============================================================================
# OPTIONAL: LangGraph Integration
# =============================================================================

def create_langgraph_workflow():
    """
    Create a LangGraph StateGraph for the pipeline.
    Requires: pip install langgraph
    
    Returns the compiled graph or None if langgraph not available.
    """
    try:
        from langgraph.graph import StateGraph, END
        
        # Create graph
        workflow = StateGraph(PipelineState)
        
        # Add nodes
        workflow.add_node("process_input", process_input)
        workflow.add_node("planner", planner)
        workflow.add_node("researcher", researcher)
        workflow.add_node("article_decisions", article_decisions)
        workflow.add_node("download_articles", download_articles)
        workflow.add_node("paper_analyzer", paper_analyzer)
        workflow.add_node("aggregate_paper", aggregate_paper)
        workflow.add_node("critique_paper", critique_paper)
        workflow.add_node("revise_paper", revise_paper)
        workflow.add_node("final_draft", final_draft)
        
        # Add edges (linear flow per PDF architecture)
        workflow.set_entry_point("process_input")
        workflow.add_edge("process_input", "planner")
        workflow.add_edge("planner", "researcher")
        workflow.add_edge("researcher", "article_decisions")
        workflow.add_edge("article_decisions", "download_articles")
        workflow.add_edge("download_articles", "paper_analyzer")
        workflow.add_edge("paper_analyzer", "aggregate_paper")
        workflow.add_edge("aggregate_paper", "critique_paper")
        workflow.add_edge("critique_paper", "revise_paper")
        workflow.add_edge("revise_paper", "final_draft")
        workflow.add_edge("final_draft", END)
        
        # Compile
        return workflow.compile()
        
    except ImportError:
        logger.warning("LangGraph not installed. Using sequential execution.")
        return None


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import sys
    
    topic = sys.argv[1] if len(sys.argv) > 1 else "deep learning natural language processing"
    
    result = run_pipeline(
        topic=topic,
        limit=10,
        year_min=2020,
        min_citations=50,
        top_n=3
    )
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Status: {result['status']}")
    print(f"Papers Selected: {len(result.get('selected_papers', []))}")
    print(f"Final Draft Words: {result.get('final_draft', {}).get('word_count', 0)}")
    print(f"Quality Score: {result.get('final_draft', {}).get('quality_score', 0):.0%}")
    
    if result["errors"]:
        print("\nErrors:")
        for err in result["errors"]:
            print(f"  - {err}")
