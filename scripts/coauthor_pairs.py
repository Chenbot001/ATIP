import pandas as pd
from itertools import combinations
import os

# --- Configuration ---
INPUT_FILE = './data/authorships.csv'
OUTPUT_FILE = './data/author_collabs.csv'

# --- Main Script ---
def create_adjacency_list():
    """
    Reads author-paper data and creates a co-author adjacency list.
    """
    # Verify the input file exists
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: Input file '{INPUT_FILE}' not found.")
        print("Please make sure the script is in the same directory as your CSV files.")
        return

    print(f"▶️ Loading data from '{INPUT_FILE}'...")
    # The file 'authorships.csv' has columns 'paper_id (s2_id)' and 'author_name' 
    # We only need these two columns for this task.
    df = pd.read_csv(INPUT_FILE, usecols=['paper_id', 'author_name'])

    print("🔄 Grouping authors by paper...")
    # Group by the paper ID and create a list of authors for each paper.
    paper_authors = df.groupby('paper_id')['author_name'].agg(list)

    print("🤝 Generating co-author pairs...")
    all_pairs = []
    # Iterate through the list of authors for each paper
    for authors in paper_authors:
        # We only need to generate pairs if there is more than one author
        if len(authors) > 1:
            # itertools.combinations creates unique pairs (e.g., (A,B), (A,C), (B,C))
            pairs = combinations(sorted(authors), 2)
            all_pairs.extend(pairs)

    print("📝 Creating the final adjacency list DataFrame...")
    # Create a DataFrame from the list of pairs
    edge_list = pd.DataFrame(all_pairs, columns=['Author1', 'Author2'])

    # To make it a true adjacency list for easy lookups, we add reciprocal pairs.
    # e.g., if we have (AuthorA, AuthorB), we also add (AuthorB, AuthorA).
    reciprocal_list = edge_list.rename(columns={'Author1': 'Author2', 'Author2': 'Author1'})
    full_adjacency_list = pd.concat([edge_list, reciprocal_list], ignore_index=True)
    full_adjacency_list.rename(columns={'Author1': 'Author', 'Author2': 'Co-Author'}, inplace=True)
    
    # Remove any potential duplicates and sort for consistency
    full_adjacency_list.drop_duplicates(inplace=True)
    full_adjacency_list.sort_values(by=['Author', 'Co-Author'], inplace=True)


    print(f"💾 Saving data to '{OUTPUT_FILE}'...")
    # Save the final DataFrame to your target CSV file without the pandas index.
    full_adjacency_list.to_csv(OUTPUT_FILE, index=False)

    print(f"✅ Done! Co-author list created at '{OUTPUT_FILE}'.")

if __name__ == '__main__':
    create_adjacency_list()