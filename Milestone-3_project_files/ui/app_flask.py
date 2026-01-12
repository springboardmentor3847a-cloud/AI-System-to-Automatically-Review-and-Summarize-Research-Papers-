"""
Simple Web UI for the paper pipeline using Flask.
This is an alternative to the Gradio UI for Python 3.13 compatibility.
"""

import os
import sys
import json
from flask import Flask, render_template_string, request, jsonify

# Ensure project root on path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Change to project root for relative paths
os.chdir(ROOT)

app = Flask(__name__)

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Paper Reviewer</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #2c3e50; }
        .container {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        label { display: block; margin: 10px 0 5px; font-weight: bold; }
        input[type="text"], input[type="number"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .row { display: flex; gap: 20px; }
        .col { flex: 1; }
        button {
            background: #3498db;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 15px;
        }
        button:hover { background: #2980b9; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .result {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
            white-space: pre-wrap;
            font-family: monospace;
            max-height: 400px;
            overflow-y: auto;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            background: #ddd;
            border: none;
            border-radius: 5px 5px 0 0;
            cursor: pointer;
        }
        .tab.active { background: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .info { background: #d1ecf1; color: #0c5460; }
    </style>
</head>
<body>
    <h1>📚 AI Paper Review System</h1>
    
    <div class="tabs">
        <button class="tab active" onclick="showTab('pipeline')">🚀 Run Pipeline</button>
        <button class="tab" onclick="showTab('results')">📊 View Results</button>
        <button class="tab" onclick="showTab('about')">ℹ️ About</button>
    </div>
    
    <div id="pipeline" class="tab-content active">
        <div class="container">
            <h2>Configure Pipeline</h2>
            <label>Research Topic</label>
            <input type="text" id="topic" value="deep learning natural language processing">
            
            <div class="row">
                <div class="col">
                    <label>Max Papers</label>
                    <input type="number" id="limit" value="10" min="1" max="20">
                </div>
                <div class="col">
                    <label>Min Year</label>
                    <input type="number" id="min_year" value="2020" min="2000" max="2026">
                </div>
                <div class="col">
                    <label>Min Citations</label>
                    <input type="number" id="min_citations" value="50" min="0" max="2000">
                </div>
            </div>
            
            <button id="runBtn" onclick="runPipeline()">▶️ Run Full Pipeline</button>
            
            <div id="pipelineStatus" class="status info" style="display:none;"></div>
            <div id="pipelineResult" class="result" style="display:none;"></div>
        </div>
    </div>
    
    <div id="results" class="tab-content">
        <div class="container">
            <h2>Existing Results</h2>
            <button onclick="loadResults()">🔄 Load Data</button>
            <div id="resultsData" class="result" style="display:none;"></div>
        </div>
    </div>
    
    <div id="about" class="tab-content">
        <div class="container">
            <h2>About</h2>
            <p>This AI system automatically reviews and summarizes research papers.</p>
            <h3>Features:</h3>
            <ul>
                <li>✅ Automated Paper Search via Semantic Scholar API</li>
                <li>✅ PDF Download with validation</li>
                <li>✅ Text Extraction from PDFs</li>
                <li>✅ Text Analysis (readability, key terms, statistics)</li>
                <li>✅ Draft Generation</li>
                <li>✅ Automated Critique</li>
            </ul>
        </div>
    </div>
    
    <script>
        function showTab(tabId) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelector(`#${tabId}`).classList.add('active');
            event.target.classList.add('active');
        }
        
        async function runPipeline() {
            const btn = document.getElementById('runBtn');
            const status = document.getElementById('pipelineStatus');
            const result = document.getElementById('pipelineResult');
            
            btn.disabled = true;
            btn.textContent = '⏳ Running...';
            status.style.display = 'block';
            status.className = 'status info';
            status.textContent = 'Pipeline running... This may take a few minutes.';
            
            try {
                const response = await fetch('/run_pipeline', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        topic: document.getElementById('topic').value,
                        limit: parseInt(document.getElementById('limit').value),
                        min_year: parseInt(document.getElementById('min_year').value),
                        min_citations: parseInt(document.getElementById('min_citations').value)
                    })
                });
                
                const data = await response.json();
                
                status.className = 'status success';
                status.textContent = '✅ Pipeline completed successfully!';
                result.style.display = 'block';
                result.textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                status.className = 'status error';
                status.textContent = '❌ Error: ' + error.message;
            }
            
            btn.disabled = false;
            btn.textContent = '▶️ Run Full Pipeline';
        }
        
        async function loadResults() {
            const resultsDiv = document.getElementById('resultsData');
            try {
                const response = await fetch('/load_results');
                const data = await response.json();
                resultsDiv.style.display = 'block';
                resultsDiv.textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                resultsDiv.style.display = 'block';
                resultsDiv.textContent = 'Error loading results: ' + error.message;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/run_pipeline', methods=['POST'])
def run_pipeline():
    try:
        from scripts.prepare_dataset import create_dataset, validate_dataset
        
        data = request.json
        stats = create_dataset(
            topic=data.get('topic', 'deep learning'),
            limit=data.get('limit', 10),
            year_min=data.get('min_year', 2020),
            min_citations=data.get('min_citations', 50),
            download_pdfs=True
        )
        validate_dataset()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/load_results')
def load_results():
    results = {}
    
    files = [
        ("analyzed_papers", "data/metadata/analyzed_papers.json"),
        ("drafts", "data/metadata/drafts.json"),
        ("critiques", "data/metadata/critiques.json"),
        ("selected_papers", "data/metadata/selected_papers.json"),
    ]
    
    for name, path in files:
        full_path = os.path.join(ROOT, path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Summarize data to avoid huge responses
                if name == "analyzed_papers":
                    results[name] = {
                        "total": data.get("total"),
                        "success": data.get("success"),
                        "papers": [r.get("title") for r in data.get("results", [])]
                    }
                elif name == "selected_papers":
                    results[name] = {
                        "total": data.get("total_papers"),
                        "papers": [p.get("title") for p in data.get("papers", [])]
                    }
                else:
                    results[name] = {"total": data.get("total", len(data))}
    
    return jsonify(results)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI Paper Review System - Web UI")
    print("="*60)
    print("\nStarting server...")
    print("Open http://127.0.0.1:5000 in your browser")
    print("Press Ctrl+C to stop\n")
    
    app.run(host='127.0.0.1', port=5000, debug=False)
