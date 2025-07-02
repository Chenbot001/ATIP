"""
ACL Anthology Researcher-Paper Mapping Extractor

This script extracts detailed researcher-paper relationships from the ACL Anthology.
For each author in each paper, it records the author's information along with the paper's ACL ID,
DOI, and title, creating a comprehensive mapping that can be used for matching with external 
databases like Semantic Scholar.

The script preserves all author-paper relationships without deduplication, meaning
the same author will appear multiple times if they have multiple papers.

Usage:
    python researcher_paper_mapping.py [--collection COLLECTION_ID] [--all-collections]

Requirements:
    - acl_anthology library
    - pandas
    - Python 3.6+
"""

import os
import sys
import uuid
import time
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from acl_anthology import Anthology
from acl_anthology.people.name import Name


def generate_unique_researcher_id(first_name, last_name):
    """
    Generate a unique researcher ID using UUID v5.
    
    Args:
        first_name (str): Researcher's first name
        last_name (str): Researcher's last name
        
    Returns:
        str: A unique researcher ID based on UUID v5
        
    Note:
        This function uses UUID v5 with a namespace to ensure that the same name
        always generates the same UUID. It uses the combination of first and last name
        as the input for UUID generation.
    """
    # Standardize names to avoid case and space issues
    first_name = first_name.strip().lower() if first_name else ""
    last_name = last_name.strip().lower() if last_name else ""
    
    if not first_name and not last_name:
        return None
    
    # Create an identifier string
    identifier = f"{first_name}_{last_name}"
    
    # Create a UUID namespace (using a constant UUID to ensure consistency)
    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # UUID namespace for URLs
    
    # Generate a UUID v5 (name-based) using the namespace and identifier
    researcher_uuid = uuid.uuid5(namespace, identifier)
    
    # Format the UUID for use as a researcher ID
    researcher_id = f"r_{str(researcher_uuid)}"
    
    return researcher_id


def extract_paper_info(paper):
    """
    Extract paper information including ACL ID, DOI, and title from a paper object.
    
    Args:
        paper: Paper object from ACL Anthology
        
    Returns:
        tuple: (acl_id, paper_doi, paper_title) or (None, None, None) if not available
    """
    try:
        # Extract ACL ID (like 2024.acl-long.123)
        acl_id = None
        if hasattr(paper, 'full_id') and paper.full_id:
            acl_id = paper.full_id
        elif hasattr(paper, 'id') and paper.id:
            acl_id = paper.id
        
        # Extract DOI
        paper_doi = None
        if hasattr(paper, 'doi') and paper.doi:
            paper_doi = paper.doi
        
        # Extract paper title
        paper_title = None
        if hasattr(paper, 'title') and paper.title:
            paper_title = str(paper.title).strip()
        
        return acl_id, paper_doi, paper_title
        
    except Exception as e:
        print(f"Error extracting paper info: {str(e)}")
        return None, None, None


def process_paper_authors(paper):
    """
    Process all authors from a single paper and extract their information.
    
    Args:
        paper: A paper object from ACL Anthology
        
    Returns:
        list: List of dictionaries containing author-paper relationships
    """
    try:
        acl_id, paper_doi, paper_title = extract_paper_info(paper)
        if not acl_id:
            print(f"Warning: No ACL ID found for paper {paper}")
            return []
        
        author_paper_data = []
        
        # Process each author in the paper
        for author in paper.authors:
            try:
                # Parse author name
                name = Name.from_(author.name)
                first_name = name.first if name.first else ''
                last_name = name.last if name.last else ''
                
                # Generate researcher ID
                researcher_id = generate_unique_researcher_id(first_name, last_name)
                
                # Extract affiliation if available
                affiliation = None
                if hasattr(author, 'affiliation') and author.affiliation:
                    affiliation = author.affiliation
                
                # Create record for this author-paper relationship
                author_record = {
                    'researcher_id': researcher_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'acl_id': acl_id,
                    'paper_doi': paper_doi,
                    'paper_title': paper_title,
                    'affiliation': affiliation
                }
                
                author_paper_data.append(author_record)
                
            except Exception as e:
                print(f"Error processing author {author.name} in paper {acl_id}: {str(e)}")
                continue
        
        return author_paper_data
        
    except Exception as e:
        print(f"Error processing paper: {str(e)}")
        return []


def search_collection(anthology, collection_id):
    """
    Extract researcher-paper relationships from a specific collection.
    
    Args:
        anthology (Anthology): Anthology instance to use for searching
        collection_id (str): ID of the collection to search
        
    Returns:
        pd.DataFrame: DataFrame containing researcher-paper relationships
    """
    try:
        collection = anthology.get(collection_id)
        all_author_paper_data = []
        
        print(f"Analyzing collection: {collection_id}")
        
        # Collect all papers from the collection
        all_papers = []
        for volume in collection.volumes():
            for paper in volume.papers():
                all_papers.append(paper)
        
        print(f"Found {len(all_papers)} papers in collection {collection_id}")
        
        # Process papers in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(process_paper_authors, all_papers))
        
        # Flatten the results
        for paper_results in results:
            all_author_paper_data.extend(paper_results)
        
        # Create DataFrame from author-paper data
        researchers_df = pd.DataFrame(all_author_paper_data)
        
        print(f"Extracted {len(researchers_df)} author-paper relationships from collection {collection_id}")
        
        return researchers_df
        
    except Exception as e:
        print(f"Error processing collection {collection_id}: {str(e)}")
        return pd.DataFrame()


def process_collections(anthology, collection_ids, output_file):
    """
    Process multiple collections and extract researcher-paper relationships.
    
    Args:
        anthology (Anthology): Anthology instance to use for searching
        collection_ids (list): List of collection IDs to process
        output_file (str): Path to the output CSV file
        
    Returns:
        pd.DataFrame: DataFrame containing all researcher-paper relationships
    """
    # Initialize an empty DataFrame to store all data
    all_data_df = pd.DataFrame()
    
    # Process each collection
    for i, collection_id in enumerate(collection_ids):
        print(f"\nProcessing collection [{i+1}/{len(collection_ids)}]: {collection_id}")
        
        try:
            # Extract researcher-paper data from the current collection
            collection_df = search_collection(anthology, collection_id)
            
            # Append to all_data_df
            if all_data_df.empty:
                all_data_df = collection_df
            else:
                all_data_df = pd.concat([all_data_df, collection_df], ignore_index=True)
            
            # Save intermediate results periodically
            if (i + 1) % 5 == 0 or (i + 1) == len(collection_ids):
                save_data_to_csv(all_data_df, output_file)
                print(f"Saved intermediate results, processed {i+1}/{len(collection_ids)} collections")
                print(f"Total records so far: {len(all_data_df)}")
                
        except Exception as e:
            print(f"Error processing collection {collection_id}: {str(e)}")
            continue
    
    return all_data_df


def save_data_to_csv(data_df, csv_file):
    """
    Save a DataFrame of researcher-paper relationships to a CSV file.
    
    Args:
        data_df (pd.DataFrame): DataFrame containing researcher-paper relationships
        csv_file (str): Path to the output CSV file
        
    Returns:
        None
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(csv_file), exist_ok=True)
        
        # Save the DataFrame to CSV with UTF-8 encoding
        data_df.to_csv(csv_file, mode='w', header=True, index=False, encoding='utf-8')
        print(f"Data saved to {csv_file}")
        
    except Exception as e:
        print(f"Error saving data to CSV: {str(e)}")


def main():
    """
    Main function to run the researcher-paper mapping extraction process.
    """
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Extract researcher-paper mapping data from ACL Anthology')
    parser.add_argument('--collection', type=str, default="2024.acl", 
                        help='ACL collection ID to process (default: 2024.acl)')
    parser.add_argument('--output', type=str, default="data/researchers_data_with_paper.csv",
                        help='Output CSV file path (default: data/researchers_data_with_paper.csv)')
    parser.add_argument('--collections-file', type=str, default="data/acl_collections.txt",
                        help='File containing multiple collection IDs')
    args = parser.parse_args()
    
    # Start timing
    start_time = time.time()
    print(f"Starting researcher-paper mapping extraction at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize anthology
        try:
            anthology = Anthology.from_repo()
            print("Using local anthology repository")
        except Exception as e:
            print(f"Error initializing local anthology: {e}")
            print("Trying online repository...")
            try:
                anthology = Anthology.from_url()
                print("Using online anthology repository")
            except Exception as e2:
                print(f"Cannot initialize anthology: {e2}")
                sys.exit(1)
        
        # Process all collections from the collections file by default
        try:
            with open(args.collections_file, 'r') as f:
                collection_ids = [line.strip() for line in f if line.strip()]
            print(f"Read {len(collection_ids)} collections from {args.collections_file}")
        except Exception as e:
            print(f"Error reading collections file: {str(e)}")
            print(f"Falling back to single collection: {args.collection}")
            collection_ids = [args.collection]
        
        # Process all collections
        result_df = process_collections(anthology, collection_ids, args.output)
        
        # Print final statistics
        print(f"\n=== Final Statistics ===")
        print(f"Total author-paper relationships: {len(result_df)}")
        
        if not result_df.empty:
            # Count unique researchers
            unique_researchers = result_df['researcher_id'].nunique()
            print(f"Unique researchers: {unique_researchers}")
            
            # Count unique papers
            unique_papers = result_df['acl_id'].nunique()
            print(f"Unique papers: {unique_papers}")
            
            # Show sample of data
            print(f"\nSample data (first 5 rows):")
            print(result_df.head().to_string(index=False))
        
        # Calculate total time
        end_time = time.time()
        total_time = end_time - start_time
        print(f"\nTotal processing time: {total_time:.2f} seconds")
        print(f"Script completed successfully!")
        print(f"Results saved to: {args.output}")
        
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
