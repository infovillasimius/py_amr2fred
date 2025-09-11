import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from py_amr2fred import Amr2fred, Glossary
from IPython.display import Image, display
from rdflib import Graph
import networkx as nx
import matplotlib.pyplot as plt

if __name__ == "__main__":

    amr = Amr2fred()

    texts = [
        "The quick brown fox jumps over the lazy dog.",
    ]

    graphs = []
    for t in texts:
        g = amr.translate(
            text=t,
            serialize=False,                       # get an rdflib.Graph
            mode=Glossary.RdflibMode.TURTLE,       # output format if serialize=True
            multilingual=("preparano" in t),       # demo: enable multilingual for non-EN
            post_processing=True                   # WSD + Wikidata enrichment
        )
        graphs.append(g)

    # 2) Merge and persist
    kg = Graph()
    for g in graphs:
        kg += g

    out = Path("examples/amr2fred_output.ttl")
    kg.serialize(destination=out, format="turtle")
    print(f"Wrote {out.resolve()}")

    # Display the TTL output
    with open(out, "r") as f:
        print(f.read())


    # 3) Visual check for a single sentence
    dot_content = amr.translate(text=texts[0], graphic="dot")
    amr_path = "examples/check.dot"
    with open(amr_path, "w") as f:
        f.write(dot_content)
    
    # Load the DOT file into a NetworkX DiGraph using manual parsing
    try:
        # Create a simple graph by parsing DOT content manually
        G = nx.DiGraph()
        with open(amr_path, 'r') as f:
            content = f.read()
            # Simple regex parsing for nodes and edges (basic implementation)
            import re
            # Find nodes with labels (handle quoted node names)
            node_pattern = r'"([^"]+)"\s*\[.*?label="([^"]*)".*?\]'
            edge_pattern = r'"([^"]+)"\s*->\s*"([^"]+)"\s*(?:\[.*?label="([^"]*)".*?\])?'
            
            for match in re.finditer(node_pattern, content):
                node_id, label = match.groups()
                G.add_node(node_id, label=label)
            
            for match in re.finditer(edge_pattern, content):
                src, dst, label = match.groups()
                edge_attrs = {'label': label} if label else {}
                G.add_edge(src, dst, **edge_attrs)

        print(f"Graph loaded successfully: {len(G.nodes())} nodes, {len(G.edges())} edges")
        
        # Draw the graph with node and edge labels
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=10, iterations=1)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=1000)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='black', arrows=True, arrowsize=20)
        
        # Draw node labels
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
        
        # Draw edge labels
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6)
        
        plt.title("AMR Graph Visualization")
        plt.axis('off')
        plt.tight_layout()
        
        # Save the plot
        output_path = "examples/check.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Graph visualization saved to: {output_path}")
        
        plt.show()
        
    except FileNotFoundError:
        print(f"Error: The DOT file '{amr_path}' was not found.")
    except Exception as e:
        print(f"An error occurred while loading or visualizing the graph: {e}")