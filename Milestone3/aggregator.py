import os
import json


def load_json_files(input_dir):
    """
    Load all JSON files generated in Milestone 2.
    """
    papers = []
    for file in os.listdir(input_dir):
        if file.endswith(".json"):
            file_path = os.path.join(input_dir, file)
            with open(file_path, "r", encoding="utf-8") as f:
                papers.append(json.load(f))
    return papers


def build_structured_text(papers):
    """
    Convert structured JSON papers into a single
    synthesis-friendly academic text.
    """
    combined_text = []

    for idx, paper in enumerate(papers, start=1):
        combined_text.append(f"\n===== PAPER {idx} =====")

        combined_text.append(f"Title: {paper.get('title', 'Unknown Title')}")

        if paper.get("abstract"):
            combined_text.append("\nAbstract:")
            combined_text.append(paper["abstract"])

        for sec, content in paper.get("sections", {}).items():
            combined_text.append(f"\n{sec}:")
            combined_text.append(content)

        if paper.get("keywords"):
            combined_text.append("\nKeywords:")
            combined_text.append(", ".join(paper["keywords"]))

        if paper.get("key_findings"):
            combined_text.append("\nKey Findings:")
            for f in paper["key_findings"]:
                combined_text.append(f"- {f}")

    return "\n".join(combined_text)

def aggregate_papers(input_dir, max_chars=12000):
    """
    Aggregate Milestone-2 papers into a compact synthesis-friendly text.
    Hard limits size to avoid API rate/token limits.
    """
    print("📥 Loading Milestone 2 JSON files...")
    papers = load_json_files(input_dir)

    if not papers:
        raise ValueError("❌ No JSON files found in Milestone 2 directory")

    print(f"📄 Papers loaded: {len(papers)}")
    print("🧩 Structuring paper contents...")

    structured_text = build_structured_text(papers)

    # 🔥 HARD TRIM to avoid token overflow
    if len(structured_text) > max_chars:
        structured_text = structured_text[:max_chars]
        structured_text += "\n\n[Text truncated for synthesis efficiency]"

    print("📦 Aggregation complete (compressed input)")
    print(f"📏 Final input size: {len(structured_text)} characters")

    return structured_text
