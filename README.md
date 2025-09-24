# AstroGraph

A small Flask app that visualizes a space biology knowledge graph built from papers. It provides:

- Search endpoint and UI to find publications
- Mini knowledge graph per publication (paper + neighbors)
- Frontend using vis-network for graph visualization

## Quickstart

1. Create and activate a virtual environment

```powershell
py -3 -m venv venv
./venv/Scripts/Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Set your API key (if you plan to run the data processor)

```powershell
# PowerShell
$env:GOOGLE_API_KEY = "your-google-ai-studio-key"
```

4. Run the web app

```powershell
python app.py
```

Then open http://127.0.0.1:5000/ in your browser.

## Project structure

- `app.py` – Flask server and API routes
- `templates/index.html` – Frontend shell
- `static/style.css`, `static/script.js` – UI styles and logic
- `data_processor.py` – Script to build `knowledge_graph.graphml` (uses Google Gemini optionally)
- `knowledge_graph.graphml` – Generated graph data (ignored by git)
- `data/` – Source texts (ignored by git)

## Notes
- Secrets should be provided via environment variables, not committed.
- The app expects `knowledge_graph.graphml` to exist; run `data_processor.py` to regenerate it.

## License
MIT
