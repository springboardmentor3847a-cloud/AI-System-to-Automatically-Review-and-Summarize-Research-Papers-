from typing import TypedDict, List
from langgraph.graph import StateGraph, END

import paper_search, pdf_handler, analysis, writer, reviewer, apa_formatter

class ResearchState(TypedDict):
    topic: str
    papers: List[dict] # Stores metadata + path
    combined_text: str
    draft: str
    review: str
    final_output: str

# 1. Search
def search_step(state: ResearchState):
    searcher = paper_search.PaperSearcher()
    # MANDATORY: Try to get 3 papers
    papers = searcher.search_and_download(state["topic"], target_count=3)
    return {"papers": papers}

# 2. Extract
def extract_step(state: ResearchState):
    if not state.get("papers"):
        return {"combined_text": "No PDFs found."}
    full_text = ""
    for paper in state["papers"]:
        raw = pdf_handler.extract_text(paper["path"])
        clean = analysis.clean_and_chunk(raw)
        full_text += f"\n--- PAPER: {paper['title']} ---\n{clean}\n"
    return {"combined_text": full_text}

# 3. Write
def write_step(state: ResearchState):
    if "No PDFs" in state["combined_text"]:
        return {"draft": "Could not find enough valid PDFs to generate a report."}
    draft = writer.generate_summary(state["combined_text"])
    return {"draft": draft}

# 4. Review
def review_step(state: ResearchState):
    if "Could not" in state["draft"]:
        return {"review": ""}
    review = reviewer.review_draft(state["draft"])
    return {"review": review}

# 5. Finalize
def finalize_step(state: ResearchState):
    refs = apa_formatter.format_references(state.get("papers", []))
    final = f"# Research Report: {state['topic']}\n\n{state['draft']}\n\n## Peer Review\n{state['review']}{refs}"
    return {"final_output": final}

# Build Graph
workflow = StateGraph(ResearchState)
workflow.add_node("search", search_step)
workflow.add_node("extract", extract_step)
workflow.add_node("write", write_step)
workflow.add_node("review", review_step)
workflow.add_node("finalize", finalize_step)

workflow.set_entry_point("search")
workflow.add_edge("search", "extract")
workflow.add_edge("extract", "write")
workflow.add_edge("write", "review")
workflow.add_edge("review", "finalize")
workflow.add_edge("finalize", END)

app_graph = workflow.compile()

# Return BOTH the report text AND the list of papers
def run_research(topic):
    result = app_graph.invoke({"topic": topic})
    return result["final_output"], result.get("papers", [])