def format_references(papers):
    ref_text = "\n\n### References\n"
    for p in papers:
        ref_text += f"* {p['title']}. Retrieved from Semantic Scholar.\n"
    return ref_text