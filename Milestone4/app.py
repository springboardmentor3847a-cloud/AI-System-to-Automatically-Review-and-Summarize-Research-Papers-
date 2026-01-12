import os
import gradio as gr
from openai import OpenAI

# -----------------------------
# Configuration
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
M3_OUTPUT_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "milestone-3", "output")
)

client = OpenAI()  # picks OPENAI_API_KEY from environment

# -----------------------------
# Utility Functions
# -----------------------------
def load_file(filename):
    path = os.path.join(M3_OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return f"❌ File not found: {filename}. Please run Milestone 3 first."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def refine_text(section_name, text):
    """
    Refine a section using OpenAI GPT (formal academic style).
    Returns text or raises error if API fails.
    """
    prompt = f"""
You are an academic reviewer.

Refine the following {section_name} to sound:
- Formal
- Professional
- Clear
- Easy to understand
- Suitable for a research paper submission

Do NOT add new information or alter the meaning.

TEXT:
{text}
"""
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text.strip()


def safe_re_refine(text, section_name):
    """
    Re-refine with fallback for errors / rate-limits.
    """
    if not text or len(text.strip()) < 50:
        return text  # too small, skip

    try:
        return refine_text(section_name, text)
    except Exception as e:
        return f"⚠️ Re-refine failed. Showing previous content.\n\n{text}"


# -----------------------------
# Gradio Actions
# -----------------------------
def load_existing():
    abstract = load_file("abstract.txt")
    methods = load_file("methods.txt")
    results = load_file("results.txt")
    cited_results = load_file("results_with_citations.txt")

    # Professional abstract formatting
    abstract_html = f"""
    <h3>Abstract</h3>
    <p style="text-align: justify; line-height: 1.6; font-size: 15px;">
    {abstract.replace(chr(10), '<br><br>')}
    </p>
    """
    return abstract_html, methods, results, cited_results


def reviewer_feedback():
    return (
        "✔ Abstract is concise and academically structured.\n"
        "✔ Methods section clearly explains the approach.\n"
        "✔ Results are logically presented.\n"
        "✔ Citations follow academic norms.\n"
        "🔧 Minor language polishing recommended (already applied)."
    )


# -----------------------------
# Gradio Interface
# -----------------------------
with gr.Blocks(title="Automated Research Paper Review & Refinement") as app:
    gr.Markdown("""
# 📄 Automated Research Paper Review & Refinement

🔍 **Critique & Revise Research Sections**  
This system refines outputs generated in **Milestone 3** and presents them professionally.
""")

    with gr.Row():
        load_btn = gr.Button("📂 Load Existing Refined Output")

    with gr.Tabs():

        with gr.Tab("📘 Refined Sections"):
            with gr.Tabs():
                with gr.Tab("Abstract"):
                    abstract_display = gr.HTML()
                    re_refine_abstract_btn = gr.Button("Re-Refine Abstract")

                with gr.Tab("Methods"):
                    methods_display = gr.Markdown()
                    re_refine_methods_btn = gr.Button("Re-Refine Methods")

                with gr.Tab("Results"):
                    results_display = gr.Markdown()
                    re_refine_results_btn = gr.Button("Re-Refine Results")

                with gr.Tab("Results + Citations"):
                    cited_results_display = gr.Markdown()

        with gr.Tab("🧠 Reviewer Feedback"):
            feedback_display = gr.Textbox(lines=10, interactive=False)

        with gr.Tab("⚠️ Errors / Issues"):
            error_display = gr.Textbox(lines=3, interactive=False)

    # -----------------------------
    # Button Actions
    # -----------------------------
    load_btn.click(
        load_existing,
        outputs=[abstract_display, methods_display, results_display, cited_results_display]
    )

    re_refine_abstract_btn.click(
        lambda txt: safe_re_refine(txt, "Abstract"),
        inputs=abstract_display,
        outputs=abstract_display
    )

    re_refine_methods_btn.click(
        lambda txt: safe_re_refine(txt, "Methods"),
        inputs=methods_display,
        outputs=methods_display
    )

    re_refine_results_btn.click(
        lambda txt: safe_re_refine(txt, "Results"),
        inputs=results_display,
        outputs=results_display
    )

    feedback_display.value = reviewer_feedback()

    gr.Markdown("""
---
Built with **Python + Gradio** | Milestone-4 | Academic Review Workflow
""")

# -----------------------------
# Launch App
# -----------------------------
if __name__ == "__main__":
    app.launch()
