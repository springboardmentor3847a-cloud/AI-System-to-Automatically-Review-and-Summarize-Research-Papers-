"""
Gradio UI for the paper pipeline: search → download → extract → analyze → draft → critique.
"""

import os
import sys
import gradio as gr

# Ensure project root on path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
	sys.path.insert(0, ROOT)

from scripts.prepare_dataset import create_dataset, validate_dataset


def run_pipeline(topic: str, limit: int, min_year: int, min_citations: int):
	stats = create_dataset(
		topic=topic,
		limit=limit,
		year_min=min_year,
		min_citations=min_citations,
		download_pdfs=True,
	)
	# Validation output to console; return stats to UI
	validate_dataset()
	return stats


with gr.Blocks(title="AI Paper Reviewer") as demo:
	gr.Markdown("## AI System to Review and Summarize Research Papers")
	with gr.Row():
		topic = gr.Textbox(label="Research topic", value="deep learning natural language processing")
		limit = gr.Slider(1, 20, value=10, step=1, label="Max papers")
		min_year = gr.Slider(2000, 2025, value=2020, step=1, label="Min year")
		min_citations = gr.Slider(0, 2000, value=50, step=10, label="Min citations")
	run_btn = gr.Button("Run full pipeline", variant="primary")
	stats_out = gr.JSON(label="Pipeline stats")
	run_btn.click(run_pipeline, inputs=[topic, limit, min_year, min_citations], outputs=stats_out)

if __name__ == "__main__":
	demo.launch()
