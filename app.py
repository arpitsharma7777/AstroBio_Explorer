from flask import Flask, render_template, jsonify, request
import networkx as nx
import os

app = Flask(__name__)

# Load the knowledge graph when the application starts, with a safe fallback
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPH_PATH = os.getenv("GRAPH_PATH", os.path.join(BASE_DIR, "knowledge_graph.graphml"))
FALLBACK_GRAPH_PATH = os.path.join(BASE_DIR, "sample_graph.graphml")
LOADED_GRAPH_PATH = None
try:
    G = nx.read_graphml(GRAPH_PATH)
    LOADED_GRAPH_PATH = GRAPH_PATH
except Exception:
    try:
        G = nx.read_graphml(FALLBACK_GRAPH_PATH)
        LOADED_GRAPH_PATH = FALLBACK_GRAPH_PATH
    except Exception:
        G = nx.Graph()
        LOADED_GRAPH_PATH = None

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/api/health')
def health():
    """Simple health and diagnostics endpoint for debugging."""
    node_count = G.number_of_nodes()
    edge_count = G.number_of_edges()
    publications = sum(1 for _, d in G.nodes(data=True) if str(d.get('type','')).lower() == 'publication')
    return jsonify({
        "status": "ok",
        "nodes": node_count,
        "edges": edge_count,
        "publications": publications,
        "graph_path": LOADED_GRAPH_PATH
    })

@app.route('/api/search')
def search_papers():
    """
    Searches for papers based on keyword, gene, mission, or year.
    Returns a list of paper details.
    """
    keyword = request.args.get('keyword', '').lower().strip()
    
    results = {}
    
    def parse_year(y):
        """Return an int year if possible, else -1 for unknown/missing."""
        try:
            return int(str(y).strip())
        except Exception:
            return -1
    # Iterate through all nodes and find the ones that are publications
    for node, data in G.nodes(data=True):
        if str(data.get('type', '')).lower() == 'publication':
            # Basic keyword search across multiple fields
            fields = [
                str(data.get('label', '')).lower(),
                str(data.get('full_text', '')).lower(),
                str(data.get('mission', '')).lower(),
                str(data.get('year', '')).lower(),
                str(data.get('summary_objective', '')).lower(),
                str(data.get('summary_key_result', '')).lower(),
                str(data.get('summary_why_it_matters', '')).lower(),
            ]
            if not keyword or any(keyword in f for f in fields):
                results[node] = {
                    "id": node,
                    "title": data.get('label'),
                    "mission": data.get('mission'),
                    "year": data.get('year'),
                    "summary_objective": data.get('summary_objective'),
                    "summary_key_result": data.get('summary_key_result'),
                    "summary_why_it_matters": data.get('summary_why_it_matters'),
                    "pdf_link": data.get('pdf_link'),
                    "gene_lab_url": data.get('gene_lab_url')
                }

    # Also: match entities (non-publication nodes) and include neighboring publications
    type_aliases = {
        'gene': ['gene', 'genes', 'protein', 'proteins'],
        'biological process': ['process', 'processes', 'biological process', 'go process'],
        'organ': ['organ', 'tissue', 'muscle'],
    }
    def type_matches(node_type: str, q: str) -> bool:
        nt = (node_type or '').lower()
        if q in nt:
            return True
        # check aliases
        for base, alist in type_aliases.items():
            if q in alist and base in nt:
                return True
        return False

    for node, data in G.nodes(data=True):
        if str(data.get('type', '')).lower() != 'publication':
            node_type = str(data.get('type', '')).lower()
            label = str(data.get('label', '')).lower()
            if keyword and (keyword in label or type_matches(node_type, keyword)):
                for nbr in G.neighbors(node):
                    nbr_data = G.nodes[nbr]
                    if str(nbr_data.get('type', '')).lower() == 'publication' and nbr not in results:
                        results[nbr] = {
                            "id": nbr,
                            "title": nbr_data.get('label'),
                            "mission": nbr_data.get('mission'),
                            "year": nbr_data.get('year'),
                            "summary_objective": nbr_data.get('summary_objective'),
                            "summary_key_result": nbr_data.get('summary_key_result'),
                            "summary_why_it_matters": nbr_data.get('summary_why_it_matters'),
                            "pdf_link": nbr_data.get('pdf_link'),
                            "gene_lab_url": nbr_data.get('gene_lab_url')
                        }
    
    # Sort results by year (parsed), newest first; unknown years at the end
    sorted_results = sorted(results.values(), key=lambda x: parse_year(x.get('year')), reverse=True)
    # Limit to 20 entries to keep UI responsive
    sorted_results = sorted_results[:20]
    return jsonify(sorted_results)

@app.route('/api/graph/<paper_id>')
def get_graph_for_paper(paper_id):
    """
    Returns the mini knowledge graph for a specific paper.
    The graph includes the paper node and its direct neighbors.
    """
    if paper_id not in G:
        return jsonify({"error": "Paper not found"}), 404

    # Create a subgraph containing the paper and its direct connections
    nodes_to_include = [paper_id] + list(G.neighbors(paper_id))
    subgraph = G.subgraph(nodes_to_include)

    # Format data for the frontend visualization library
    nodes_for_viz = [
        {
            "id": node,
            "label": G.nodes[node].get("label", node),
            "type": G.nodes[node].get("type", "entity")
        }
        for node in subgraph.nodes()
    ]
    edges_for_viz = [
        {"from": u, "to": v} for u, v in subgraph.edges()
    ]

    return jsonify({"nodes": nodes_for_viz, "edges": edges_for_viz})

if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)