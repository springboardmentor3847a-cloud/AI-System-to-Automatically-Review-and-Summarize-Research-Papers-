import time
from openai import OpenAI
from openai import RateLimitError, APIError

client = OpenAI()

MODEL = "gpt-4.1-mini"


def call_llm(prompt, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            response = client.responses.create(
                model=MODEL,
                input=prompt,
                max_output_tokens=800
            )
            return response.output_text.strip()

        except RateLimitError:
            wait_time = 25
            print(f"⏳ Rate limit hit. Waiting {wait_time}s (attempt {attempt}/{max_retries})")
            time.sleep(wait_time)

        except APIError as e:
            raise RuntimeError(f"❌ OpenAI API error: {e}")

    raise RuntimeError("❌ Failed after multiple retries due to rate limits.")


def generate_abstract(text):
    prompt = f"""
Write a concise academic abstract synthesizing the following research papers.
Focus on objectives, methods, and key findings.

{text}
"""
    return call_llm(prompt)


def generate_methods(text):
    prompt = f"""
Write a unified Methods section based on the methodologies described
in the following research papers.

{text}
"""
    return call_llm(prompt)


def generate_results(text):
    prompt = f"""
Summarize the main results and findings across the following research papers.
Avoid citations here.

{text}
"""
    return call_llm(prompt)


def generate_results_with_citations(text):
    prompt = f"""
Summarize the results across these papers and include
inline APA-style citations like (Author, Year).

{text}
"""
    return call_llm(prompt)
