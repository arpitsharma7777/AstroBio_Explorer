document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const resultsContainer = document.getElementById('results-container');
    const detailsPanel = document.getElementById('details-panel');
    const graphContainer = document.getElementById('graph-container');
    let network = null; // To hold the graph visualization object

    // Handle the search form submission
    searchForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const keyword = searchInput.value;
        if (!keyword) return;

    resultsContainer.innerHTML = '<p style="color:#666">Searching…</p>';

        try {
            const response = await fetch(`/api/search?keyword=${encodeURIComponent(keyword)}`);
            const papers = await response.json();
            displayResults(papers);
        } catch (error) {
            console.error('Search failed:', error);
            resultsContainer.innerHTML = '<p style="color:#b91c1c">Error during search. Please try again.</p>';
        }
    });

    // Function to display the search results as cards
    function displayResults(papers) {
        resultsContainer.innerHTML = ''; // Clear previous results
        if (!Array.isArray(papers) || papers.length === 0) {
            resultsContainer.innerHTML = '<p style="color:#666">No publications found.</p>';
            return;
        }

        papers.forEach(paper => {
            const card = document.createElement('div');
            card.className = 'result-card';
            card.dataset.paperId = paper.id;

            card.innerHTML = `
                <h3>${paper.title}</h3>
                <p><strong>Mission:</strong> ${paper.mission || '—'} | <strong>Year:</strong> ${paper.year || '—'}</p>
            `;

            // Add click event to each card
            card.addEventListener('click', () => {
                // Highlight the active card
                document.querySelectorAll('.result-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');

                displayDetails(paper);
                loadGraph(paper.id);
            });

            resultsContainer.appendChild(card);
        });
    }

    // Function to display the detailed information of a selected paper
    function displayDetails(paper) {
        detailsPanel.innerHTML = `
            <h2>${paper.title}</h2>
            <ul>
                <li><strong>Objective:</strong> ${paper.summary_objective || '—'}</li>
                <li><strong>Key Result:</strong> ${paper.summary_key_result || '—'}</li>
                <li><strong>Why it Matters:</strong> ${paper.summary_why_it_matters || '—'}</li>
            </ul>
            <p>
                ${paper.pdf_link? `<a href="${paper.pdf_link}" target="_blank" rel="noopener noreferrer">Read Full PDF</a>` : ''}
                ${paper.gene_lab_url? ` | <a href="${paper.gene_lab_url}" target="_blank" rel="noopener noreferrer">View Raw Data on GeneLab</a>` : ''}
            </p>
        `;
    }

    // Function to fetch and render the knowledge graph for a paper
    async function loadGraph(paperId) {
        try {
            const response = await fetch(`/api/graph/${paperId}`);
            const graphData = await response.json();
            drawGraph(graphData);
        } catch (error) {
            console.error('Failed to load graph:', error);
            graphContainer.innerHTML = 'Could not load graph.';
        }
    }

    // Function to draw the graph using Vis.js
    function drawGraph(graphData) {
        if (network) {
            network.destroy();
        }
        const data = {
            nodes: new vis.DataSet(graphData.nodes),
            edges: new vis.DataSet(graphData.edges),
        };
        const options = {
            nodes: {
                shape: 'dot',
                size: 20,
                font: { size: 14, color: '#333' },
                borderWidth: 2,
            },
            edges: {
                width: 2,
                color: { inherit: 'from' }
            },
            physics: {
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {
                    gravitationalConstant: -50,
                    centralGravity: 0.01,
                    springLength: 100,
                    springConstant: 0.08,
                },
                minVelocity: 0.75,
            },
            interaction: {
                hover: true,
                tooltipDelay: 200,
            },
        };
        network = new vis.Network(graphContainer, data, options);
    }
});