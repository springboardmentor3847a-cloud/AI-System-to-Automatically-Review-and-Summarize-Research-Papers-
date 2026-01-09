import os
from aggregator import aggregate_papers
from generator import (
    generate_abstract,
    generate_methods,
    generate_results,
    generate_results_with_citations
)
from apa_formatter import generate_apa_references


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MILESTONE2_JSON_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "milestone-2", "extracted_text")
)

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def main():
    print("\n=== MILESTONE 3 STARTED ===\n")
    print(f"📂 Reading Milestone-2 JSONs from:\n{MILESTONE2_JSON_DIR}\n")

    # Step 1: Aggregate once
    aggregated_text = aggregate_papers(MILESTONE2_JSON_DIR)

    print("🧠 Generating Abstract...")
    abstract = generate_abstract(aggregated_text)

    print("🧠 Generating Methods...")
    methods = generate_methods(aggregated_text)

    print("🧠 Generating Results...")
    results = generate_results(aggregated_text)

    print("🧠 Generating Results with Citations...")
    results_cited = generate_results_with_citations(aggregated_text)

    print("📚 Generating APA References...")
    references = generate_apa_references()

    # Save outputs
    files = {
        "abstract.txt": abstract,
        "methods.txt": methods,
        "results.txt": results,
        "results_with_citations.txt": results_cited,
        "references.txt": references
    }

    for filename, content in files.items():
        with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
            f.write(content)

    print("\n✅ Milestone 3 completed successfully")
    print(f"📁 Outputs saved in: {OUTPUT_DIR}\n")


if __name__ == "__main__":
    main()
