import pandas as pd
import networkx as nx
from itertools import combinations
from pyvis.network import Network

# --- 1. Setup ---
# Placeholder for the author whose network you want to visualize
TARGET_AUTHOR_ID = 143977260

# Load the full dataset
authorships_df = pd.read_csv('data/authorships.csv')


# --- 2. Filter for Target Author's Network ---
# Find all paper IDs for the target author
target_paper_ids = authorships_df[authorships_df['author_id'] == TARGET_AUTHOR_ID]['paper_id'].unique()

# Create a new DataFrame containing only the data related to those papers.
# This includes the target author and all of their co-authors.
network_df = authorships_df[authorships_df['paper_id'].isin(target_paper_ids)]


# --- 3. Create Author Name Map ---
# Build the name map from the smaller, filtered DataFrame for efficiency.
author_name_map = network_df[['author_id', 'author_name']].drop_duplicates().set_index('author_id')


# --- 4. Build the Graph ---
G = nx.Graph()

# Build the graph using only the filtered network_df
for paper_id, group in network_df.groupby('paper_id'):
    author_pairs = list(combinations(group['author_id'], 2))
    
    for u, v in author_pairs:
        if G.has_edge(u, v):
            G[u][v]['weight'] += 1
        else:
            G.add_edge(u, v, weight=1)


# --- 5. Add Attributes and Highlight the Target Author ---
def clean_text(text):
    """Clean text to avoid encoding issues"""
    if pd.isna(text):
        return "Unknown"
    # Remove or replace problematic characters
    text = str(text).encode('ascii', 'ignore').decode('ascii')
    return text

for node in G.nodes():
    try:
        name = author_name_map.loc[node, 'author_name']
        clean_name = clean_text(name)
        G.nodes[node]['label'] = clean_name
        G.nodes[node]['title'] = clean_name
    except KeyError:
        G.nodes[node]['label'] = str(node)
        G.nodes[node]['title'] = str(node)

    # Highlight the target author's node
    if node == TARGET_AUTHOR_ID:
        G.nodes[node]['color'] = '#FF5733' # A distinct color for the main author
        G.nodes[node]['size'] = 25        # Make the node larger


# --- 6. Visualize with Pyvis ---
net = Network(height="750px", width="100%", notebook=True, cdn_resources='in_line')
net.from_nx(G)

# Save the visualization to a file with proper encoding
output_file = f"visualizations/coauthor_map_author_{TARGET_AUTHOR_ID}.html"
try:
    # Try the normal way first
    net.write_html(output_file, open_browser=False, notebook=True)
except UnicodeEncodeError:
    # If that fails, manually write with UTF-8 encoding
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(net.html)
print(f"Network visualization saved to: {output_file}")