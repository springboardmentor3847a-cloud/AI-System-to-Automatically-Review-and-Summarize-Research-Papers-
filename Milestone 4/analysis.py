import re

def clean_and_chunk(text, max_chars=12000):
    # Flatten whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Limit size to avoid Token Limits
    return text[:max_chars]