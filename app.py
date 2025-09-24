from flask import Flask, render_template, jsonify, request
import networkx as nx
import os

app = Flask(__name__)

# Load the knowledge graph when the application starts, with a safe fallback
GRAPH_PATH = os.getenv("GRAPH_PATH", "knowledge_graph.graphml")
try:
    G = nx.read_graphml(GRAPH_PATH)
except Exception:
    G = nx.Graph()

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/api/search')
def search_papers():
    """
    Searches for papers based on keyword, gene, mission, or year.
    Returns a list of paper details.
    """
    keyword = request.args.get('keyword', '').lower()
    
    results = []
    # Iterate through all nodes and find the ones that are publications
    for node, data in G.nodes(data=True):
        if data.get('type') == 'Publication':
            # Basic keyword search across title and text
            title = data.get('label', '').lower()
            full_text = data.get('full_text', '').lower()
            
            if keyword in title or keyword in full_text:
                results.append({
                    "id": node,
                    "title": data.get('label'),
                    "mission": data.get('mission'),
                    "year": data.get('year'),
                    "summary_objective": data.get('summary_objective'),
                    "summary_key_result": data.get('summary_key_result'),
                    "summary_why_it_matters": data.get('summary_why_it_matters'),
                    "pdf_link": data.get('pdf_link'),
                    "gene_lab_url": data.get('gene_lab_url')
                })
    
    # Sort results by year, newest first
    sorted_results = sorted(results, key=lambda x: x['year'], reverse=True)
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