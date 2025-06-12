"""
ACL Anthology Paper Information Extractor

This script extracts paper information from the ACL Anthology and saves it to a CSV file.
It processes papers from a specific collection, extracts metadata for each paper,
and also accumulates statistics about authors and papers.

The script uses the ACL Anthology API to access paper data and pandas for efficient
data manipulation and storage.

Usage:
    python paper_table.py

Requirements:
    - acl_anthology library
    - pandas
    - Python 3.6+
"""

from acl_anthology import Anthology
import pandas as pd
import os
import sys

def save_papers_to_csv(papers_df, csv_file='papers_data.csv'):
    """
    Save a DataFrame of paper information to a CSV file.
    
    Args:
        papers_df (pd.DataFrame): DataFrame containing paper information.
        csv_file (str, optional): Path to the output CSV file. Defaults to 'papers_data.csv'.
        
    Returns:
        None
    """
    # Always overwrite the file to ensure outdated data is replaced
    papers_df.to_csv(csv_file, mode='w', header=True, index=False, encoding='utf-8')
    print(f"Data saved to {csv_file}")

def search_collection(anthology, collection_id=""):
    """
    Search through a collection in the ACL Anthology and extract paper information.
    
    Args:
        anthology (Anthology): Anthology instance to use for searching.
        collection_id (str, optional): ID of the collection to search. Defaults to "2024.acl".
        
    Returns:
        tuple: A tuple containing (papers_df, total_papers, all_unique_authors)
               where papers_df is a DataFrame of paper information,
               total_papers is the count of papers processed,
               and all_unique_authors is a set of unique author names.
    """
    # Get the collection
    collection = anthology.get(collection_id)
    total_papers = 0
    
    # Create a list to store all paper data
    papers_data = []
    
    for volume in collection.volumes():
        volume_papers = 0
        for paper in volume.papers():
            # Extract paper information
            paper_id = paper.full_id
                
            # Count statistics
            volume_papers += 1
            total_papers += 1
            
            paper_doi = paper.doi
            if paper_doi is None:
                continue  # Skip papers without DOI

            title = paper.title
            abstract = paper.abstract
            venue = anthology.venues[paper.venue_ids[0]].acronym if paper.venue_ids else ''
            year = paper.year
            tracks = None  # This will be filled with data using a different script
            
            papers_data.append({
                'paper_id': paper_id,
                'paper_doi': paper_doi,
                'title': title,
                'abstract': abstract,
                'venue': venue,
                'year': year,
                'tracks': tracks
            })
        
        # print(f"Volume: {volume.title}")
        # print(f"  Number of papers: {volume_papers}")
    

    papers_df = pd.DataFrame(papers_data)
    # print(f"Total {total_papers} papers across all volumes in collection {collection.id}:")

    return papers_df

def main():
    """
    Main function to initialize the Anthology and run the paper extraction process.
    
    Returns:
        None
    """
    try:
        # Try to initialize anthology from local repo first
        anthology = Anthology.from_repo()
        print("Using local anthology repository.")
    except Exception as e:
        print(f"Error initializing anthology: {e}")
        print("Could not initialize anthology. Make sure the data is available.")
        sys.exit(1)

    # Read all collection IDs from acl_collections.txt
    with open("c:\\Users\\ssr\\EJC\\AI_Researcher_Network\\data\\acl_collections.txt", "r") as file:
        collection_ids = [line.strip() for line in file]

    # Initialize an empty DataFrame to accumulate all paper data
    all_papers_df = pd.DataFrame()

    # Initialize counters for collections and papers
    total_collections = 0
    total_papers = 0

    for collection_id in collection_ids:
        print(f"Processing collection: {collection_id}")
        papers_df = search_collection(anthology, collection_id=collection_id)
        all_papers_df = pd.concat([all_papers_df, papers_df], ignore_index=True)
        total_collections += 1
        total_papers += len(papers_df)

    # Save the accumulated data to CSV
    if not all_papers_df.empty:
        save_papers_to_csv(all_papers_df, csv_file='../data/papers_data.csv')

    # Display total counts
    print(f"\nTotal collections processed: {total_collections}")
    print(f"Total papers collected: {total_papers}")

    print("Script completed successfully.")

if __name__ == "__main__":
    main()



