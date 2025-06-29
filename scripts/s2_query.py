#!/usr/bin/env python3
"""
S2 API Data Gathering Script

This script enriches an existing database by fetching relational data from the Semantic Scholar API.
It processes ACL paper identifiers and generates CSV files for researcher profiles, citations, and authorships.

Phase 1: Fetches relational data (authors, citations, references) from paper IDs
Phase 2: Fetches researcher profile data from collected author IDs

Author: AI Assistant
Date: 2024
"""

import requests
import csv
import os
import time
import json
from typing import List, Dict, Set, Any, Optional
from tqdm import tqdm


def fetch_relational_data(input_csv_path: str, output_dir: str, api_key: Optional[str] = None) -> None:
    """
    Phase 1: Fetch relational data from Semantic Scholar API using paper IDs.
    
    Args:
        input_csv_path: Path to the input CSV file containing paper IDs
        output_dir: Directory to save output files
        api_key: Optional Semantic Scholar API key for higher rate limits
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read paper IDs from input CSV
    paper_ids = []
    try:
        with open(input_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'acl_id' in row and row['acl_id'].strip():
                    paper_ids.append(row['acl_id'].strip())
    except FileNotFoundError:
        print(f"Error: Input file {input_csv_path} not found.")
        return
    except Exception as e:
        print(f"Error reading input CSV: {e}")
        return
    
    print(f"Found {len(paper_ids)} paper IDs to process")
    
    # Split into minibatches of 500
    batch_size = 500
    minibatches = [paper_ids[i:i + batch_size] for i in range(0, len(paper_ids), batch_size)]
    
    # Initialize output files
    authorships_file = os.path.join(output_dir, 'authorships.csv')
    citations_file = os.path.join(output_dir, 'citations.csv')
    
    # Create CSV files with headers
    with open(authorships_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['researcher_id', 'paper_doi', 'is_first_author', 'is_last_author'])
    
    with open(citations_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['citing_paper_id', 'cited_paper_id', 'is_influential', 'context'])
    
    # Collect unique author IDs
    unique_author_ids: Set[str] = set()
    
    # Setup API headers
    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['x-api-key'] = api_key
    
    # Process each minibatch
    print("Processing paper batches...")
    for batch_idx, batch in enumerate(tqdm(minibatches, desc="Processing paper batches")):
        # Format IDs with ACL: prefix
        formatted_ids = [f"ACL:{paper_id}" for paper_id in batch]
        
        # Prepare API request
        payload = {
            "ids": formatted_ids,
            "fields": "externalIds,authors,citations"
        }
        
        # Make API call
        try:
            response = requests.post(
                'https://api.semanticscholar.org/graph/v1/paper/batch',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Warning: API returned status {response.status_code} for batch {batch_idx}")
                continue
            
            papers_data = response.json()
            
            # Process each paper in the batch
            for paper in papers_data:
                if not paper:  # Skip null papers
                    continue
                
                paper_id = paper.get('paperId')
                external_ids = paper.get('externalIds', {})
                doi = external_ids.get('DOI', '')
                
                # Process authors
                authors = paper.get('authors', [])
                for i, author in enumerate(authors):
                    if author and author.get('authorId'):
                        author_id = author['authorId']
                        unique_author_ids.add(author_id)
                        
                        # Determine author position
                        is_first = i == 0
                        is_last = i == len(authors) - 1
                        
                        # Write to authorships CSV
                        with open(authorships_file, 'a', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow([author_id, doi, is_first, is_last])
                
                # Process citations
                citations = paper.get('citations', [])
                for citation in citations:
                    if citation and citation.get('paperId'):
                        citing_paper_id = citation.get('paperId', '')
                        cited_paper_id = paper_id or ''
                        is_influential = citation.get('isInfluential', False)
                        context = citation.get('context', '')
                        
                        # Write to citations CSV
                        with open(citations_file, 'a', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow([citing_paper_id, cited_paper_id, is_influential, context])
        
        except requests.exceptions.RequestException as e:
            print(f"Error making API request for batch {batch_idx}: {e}")
            continue
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response for batch {batch_idx}: {e}")
            continue
        except Exception as e:
            print(f"Unexpected error processing batch {batch_idx}: {e}")
            continue
        
        # Rate limiting: wait 1 second between requests
        time.sleep(1)
    
    # Save unique author IDs to file
    author_ids_file = os.path.join(output_dir, 'author_ids_to_fetch.txt')
    with open(author_ids_file, 'w', encoding='utf-8') as f:
        for author_id in sorted(unique_author_ids):
            f.write(f"{author_id}\n")
    
    print(f"Phase 1 complete. Found {len(unique_author_ids)} unique authors.")
    print(f"Output files created in: {output_dir}")


def fetch_researcher_profiles(output_dir: str, api_key: Optional[str] = None) -> None:
    """
    Phase 2: Fetch researcher profile data from Semantic Scholar API using author IDs.
    
    Args:
        output_dir: Directory containing the author_ids_to_fetch.txt file
        api_key: Optional Semantic Scholar API key for higher rate limits
    """
    # Read author IDs from file
    author_ids_file = os.path.join(output_dir, 'author_ids_to_fetch.txt')
    try:
        with open(author_ids_file, 'r', encoding='utf-8') as f:
            author_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Author IDs file {author_ids_file} not found. Run Phase 1 first.")
        return
    except Exception as e:
        print(f"Error reading author IDs file: {e}")
        return
    
    print(f"Found {len(author_ids)} author IDs to process")
    
    # Split into minibatches of 500
    batch_size = 500
    minibatches = [author_ids[i:i + batch_size] for i in range(0, len(author_ids), batch_size)]
    
    # Initialize output file
    profiles_file = os.path.join(output_dir, 'researcher_profiles.csv')
    
    # Create CSV file with headers
    with open(profiles_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['researcher_id', 'first_name', 'last_name', 'h_index', 'total_citations', 'latest_affiliation'])
    
    # Setup API headers
    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['x-api-key'] = api_key
    
    # Process each minibatch
    print("Processing author batches...")
    for batch_idx, batch in enumerate(tqdm(minibatches, desc="Processing author batches")):
        # Prepare API request
        payload = {
            "ids": batch,
            "fields": "name,hIndex,citationCount,affiliations"
        }
        
        # Make API call
        try:
            response = requests.post(
                'https://api.semanticscholar.org/graph/v1/author/batch',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Warning: API returned status {response.status_code} for batch {batch_idx}")
                continue
            
            authors_data = response.json()
            
            # Process each author in the batch
            for author in authors_data:
                if not author:  # Skip null authors
                    continue
                
                author_id = author.get('authorId', '')
                name = author.get('name', '')
                h_index = author.get('hIndex', 0)
                citation_count = author.get('citationCount', 0)
                
                # Extract first and last name
                name_parts = name.split() if name else []
                first_name = name_parts[0] if len(name_parts) > 0 else ''
                last_name = name_parts[-1] if len(name_parts) > 1 else ''
                
                # Get latest affiliation
                affiliations = author.get('affiliations', [])
                latest_affiliation = ''
                if affiliations:
                    # Get the most recent affiliation (assuming they're ordered by date)
                    latest_affiliation = affiliations[0].get('name', '') if isinstance(affiliations[0], dict) else str(affiliations[0])
                
                # Write to profiles CSV
                with open(profiles_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([author_id, first_name, last_name, h_index, citation_count, latest_affiliation])
        
        except requests.exceptions.RequestException as e:
            print(f"Error making API request for batch {batch_idx}: {e}")
            continue
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response for batch {batch_idx}: {e}")
            continue
        except Exception as e:
            print(f"Unexpected error processing batch {batch_idx}: {e}")
            continue
        
        # Rate limiting: wait 1 second between requests
        time.sleep(1)
    
    print(f"Phase 2 complete. Researcher profiles saved to: {profiles_file}")


def main():
    """
    Main function to run both phases of the data gathering process.
    """
    # Configuration
    input_csv_path = "C:/Eric/Projects/AI_Researcher_Network/data/papers_data_classified.csv"
    output_dir = "C:/Eric/Projects/AI_Researcher_Network/data"
    api_key = "39B73CXWua7xhzGlxFrNJ5wY6uIjXCna9sLxWL2w"
    
    if not api_key:
        api_key = None
        print("No API key provided. Using public rate limits.")
    
    # Validate input file exists
    if not os.path.exists(input_csv_path):
        print(f"Error: Input file {input_csv_path} does not exist.")
        return
    
    print("\n" + "="*50)
    print("Starting S2 API Data Gathering Process")
    print("="*50)
    
    # Phase 1: Fetch relational data
    print("\nPhase 1: Fetching relational data...")
    fetch_relational_data(input_csv_path, output_dir, api_key)
    
    # Phase 2: Fetch researcher profiles
    print("\nPhase 2: Fetching researcher profiles...")
    fetch_researcher_profiles(output_dir, api_key)
    
    print("\n" + "="*50)
    print("Data gathering process complete!")
    print(f"All output files saved in: {output_dir}")
    print("="*50)


if __name__ == "__main__":
    main() 