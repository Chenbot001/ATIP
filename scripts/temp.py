import pandas as pd
import os

def add_existence_flags(paper_info_path: str, citation_edges_path: str, output_path: str):
    """
    Adds boolean flags to citation_edges.csv indicating if citing/cited papers
    are present in the main paper_info dataset.
    """
    # 1. Load known paper IDs
    known_paper_ids = set()
    if os.path.exists(paper_info_path):
        paper_info_df = pd.read_csv(paper_info_path)
        if 's2_id' in paper_info_df.columns:
            known_paper_ids = set(paper_info_df['s2_id'].astype(str)) # Ensure string type
        print(f"Loaded {len(known_paper_ids)} known paper IDs from {paper_info_path}")
    else:
        print(f"Warning: paper_info.csv not found at {paper_info_path}. All papers will be marked as 'not in dataset'.")


    # 2. Load citation edges
    if not os.path.exists(citation_edges_path):
        print(f"Error: citation_edges.csv not found at {citation_edges_path}. Cannot add flags.")
        return

    citation_df = pd.read_csv(citation_edges_path)
    print(f"Loaded {len(citation_df)} citation edges from {citation_edges_path}")

    # 3. Add boolean columns
    # Ensure IDs are treated as strings for consistent comparison
    citation_df['citing_paper_in_dataset'] = citation_df['citing_paper_id'].astype(str).isin(known_paper_ids)
    citation_df['cited_paper_in_dataset'] = citation_df['cited_paper_id'].astype(str).isin(known_paper_ids)

    # Save the updated DataFrame
    citation_df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Updated citation edges with existence flags saved to {output_path}")

# Example Usage (assuming you run this after S2_batch_query_papers.py)
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) # Adjust if your script is nested differently

    input_paper_info = os.path.join(project_root, "data", "paper_info.csv") # Your main list of papers
    input_citation_edges = os.path.join(project_root, "data", "citation_edges.csv") # Output from previous script
    output_citation_edges_flagged = os.path.join(project_root, "data", "citation_edges_flagged.csv")

    add_existence_flags(input_paper_info, input_citation_edges, output_citation_edges_flagged)