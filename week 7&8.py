# ============================================================
# MILESTONE 4: REVIEW, REFINEMENT & UI INTEGRATION (FINAL)
# Week 7–8
# ============================================================

import os
import json
from datetime import datetime
from dotenv import load_dotenv
import gradio as gr

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

DRAFT_PATH = "milestone3_output/final_draft.json"
OUTPUT_DIR = "milestone4_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ============================================================
# 1. LOAD DRAFT FROM MILESTONE 3
# ============================================================

def load_draft():
    if not os.path.exists(DRAFT_PATH):
        raise RuntimeError("❌ Milestone 3 draft not found.")
    with open(DRAFT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# ============================================================
# 2. GEMINI MODEL SELECTION (2.5 FLASH PREFERRED)
# ============================================================

def select_gemini_model(client):
    preferred_models = [
        "models/gemini-2.5-flash",
        "models/gemini-1.5-pro",
        "models/gemini-1.0-pro"
    ]

    available = {m.name for m in client.models.list()}

    for model in preferred_models:
        if model in available:
            return model

    # Final fallback: trial generation
    for m in client.models.list():
        try:
            client.models.generate_content(
                model=m.name,
                contents="Test"
            )
            return m.name
        except Exception:
            continue

    raise RuntimeError("❌ No usable Gemini model found")

# ============================================================
# 3. QUALITY EVALUATION MODULE (RULE-BASED)
# ============================================================

def evaluate_quality(text: str) -> str:
    feedback = []

    if len(text.split()) < 150:
        feedback.append("Section is too short; consider expanding analysis.")

    if "." not in text:
        feedback.append("Lacks sentence-level structure.")

    if not feedback:
        return "✔ Quality looks good. Minor refinements only."

    return "⚠ Needs improvement:\n- " + "\n- ".join(feedback)

# ============================================================
# 4. REVISION SUGGESTIONS (GEMINI)
# ============================================================

def suggest_revision(text: str) -> str:
    if not GEMINI_API_KEY:
        return "⚠ Revision unavailable (Gemini API key missing)."

    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        model = select_gemini_model(client)

        prompt = f"""
You are a senior academic reviewer.
Provide constructive revision suggestions (do not rewrite fully).

TEXT:
{text}
"""

        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        return response.text.strip()

    except Exception as e:
        return f"⚠ Revision unavailable due to error: {e}"

# ============================================================
# 5. REVISION / REWRITE MODULE (USER-TRIGGERED)
# ============================================================

def revise_section(text: str) -> str:
    if not GEMINI_API_KEY:
        return text + "\n\n[Revision skipped – API unavailable]"

    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        model = select_gemini_model(client)

        prompt = f"""
Rewrite the following academic section by improving clarity,
coherence, and academic tone without changing meaning.

TEXT:
{text}
"""

        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        return response.text.strip()

    except Exception:
        return text + "\n\n[Revision failed – fallback applied]"

# ============================================================
# 6. FINAL REPORT SAVE
# ============================================================

def save_final_report(draft):
    path = os.path.join(
        OUTPUT_DIR,
        f"final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(draft, f, indent=4, ensure_ascii=False)
    return path

# ============================================================
# 7. GRADIO UI
# ============================================================

def launch_ui():
    draft = load_draft()

    def critique_and_revise(text):
        quality = evaluate_quality(text)
        suggestions = suggest_revision(text)
        revised = revise_section(text)
        return quality, suggestions, revised

    with gr.Blocks(title="Milestone 4 – Research Draft Review & Refinement") as demo:
        gr.Markdown("## 📄 Automated Research Draft – Final Review")

        with gr.Tabs():
            for section in ["abstract", "methods", "results"]:
                with gr.Tab(section.capitalize()):
                    original = gr.Textbox(
                        value=draft[section],
                        label="Original Section",
                        lines=14
                    )

                    critique_btn = gr.Button("🔍 Critique / Revise")

                    quality = gr.Textbox(label="Quality Evaluation")
                    suggestions = gr.Textbox(label="Revision Suggestions", lines=6)
                    revised = gr.Textbox(label="Revised Section", lines=14)

                    critique_btn.click(
                        critique_and_revise,
                        inputs=original,
                        outputs=[quality, suggestions, revised]
                    )

        gr.Markdown("### 📚 APA References")
        gr.Textbox("\n".join(draft["references"]), lines=10)

    demo.launch()

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    launch_ui()
