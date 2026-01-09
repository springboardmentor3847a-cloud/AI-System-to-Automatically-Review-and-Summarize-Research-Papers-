import csv
import os

def generate_apa_references():
    metadata_path = os.path.abspath(
        os.path.join("..", "milestone-1", "data", "dataset", "papers_dataset.csv")
    )

    if not os.path.exists(metadata_path):
        return "APA references unavailable (metadata missing)."

    references = []

    with open(metadata_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ref = f"{row['title']} ({row['year']}). {row['venue']}."
            references.append(ref)

    return "\n".join(references)
