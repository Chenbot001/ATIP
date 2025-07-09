import pandas as pd
import networkx as nx
from itertools import combinations
import matplotlib.pyplot as plt

# --- 1. Setup ---
# Placeholder for the author whose network you want to visualize
TARGET_AUTHOR_ID = 143977260 # Replace with the actual author_id you want to focus on

# Load the full dataset
authorships_df = pd.read_csv('data/authorships.csv')


# --- 2. Filter for Target Author's Network ---
# Find all paper IDs for the target author
target_paper_ids = authorships_df[authorships_df['author_id'] == TARGET_AUTHOR_ID]['paper_id'].unique()

# Create a new DataFrame containing only the data related to those papers
network_df = authorships_df[authorships_df['paper_id'].isin(target_paper_ids)]


# --- 3. Create Author Name Map ---
author_name_map = network_df[['author_id', 'author_name']].drop_duplicates().set_index('author_id')


# --- 4. Build the Graph ---
G = nx.Graph()

for paper_id, group in network_df.groupby('paper_id'):
    author_pairs = list(combinations(group['author_id'], 2))
    for u, v in author_pairs:
        if G.has_edge(u, v):
            G[u][v]['weight'] += 1
        else:
            G.add_edge(u, v, weight=1)


# --- 5. Add Author Names to Nodes ---
# This step is still useful for getting labels for the Matplotlib plot
for node in G.nodes():
    try:
        name = author_name_map.loc[node, 'author_name']
        G.nodes[node]['label'] = name
    except KeyError:
        G.nodes[node]['label'] = str(node)


# --- 6. Visualize with Matplotlib ---
# Define a layout for the graph's nodes
pos = nx.spring_layout(G, seed=42) # Use a seed for a reproducible layout

# Prepare drawing options
node_colors = ['#FF5733' if node == TARGET_AUTHOR_ID else '#1f78b4' for node in G.nodes()]
edge_widths = [G[u][v]['weight'] * 0.5 for u, v in G.edges()] # Scale weights for better visuals
labels = {node: data['label'] for node, data in G.nodes(data=True)}
target_author_name = labels.get(TARGET_AUTHOR_ID, f"ID {TARGET_AUTHOR_ID}")

# Draw the network
plt.figure(figsize=(15, 15))
nx.draw(
    G,
    pos,
    with_labels=True,
    labels=labels,
    node_color=node_colors,
    width=edge_widths,
    edge_color='grey',
    font_size=10
)

# Add a title and display the plot
plt.title(f"Co-author Network for {target_author_name}", size=15)
plt.show()