import requests
import csv
import os
import time
import json
from tqdm import tqdm
from typing import List, Set, Dict, Any

# API Configuration
S2_API_KEY = "39B73CXWua7xhzGlxFrNJ5wY6uIjXCna9sLxWL2w"  # Replace with your actual API key

def fetch_relational_data(input_csv_path: str, output_dir: str) -> None:
    """
    Phase 1: Fetch relational data (authors & citations) from Semantic Scholar API.
    
    Args:
        input_csv_path: Path to the input CSV file containing paper IDs
        output_dir: Directory to save output files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read paper IDs from input CSV
    paper_ids = []
    with open(input_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'acl_id' in row and row['acl_id']:
                paper_ids.append(row['acl_id'])
    
    print(f"Found {len(paper_ids)} paper IDs to process")
    
    # Format paper IDs with ACL: prefix
    formatted_paper_ids = [f"ACL:{paper_id}" for paper_id in paper_ids]
    
    # Split into minibatches of 500
    batch_size = 500
    minibatches = [formatted_paper_ids[i:i + batch_size] 
                   for i in range(0, len(formatted_paper_ids), batch_size)]
    
    # Testing: only process first minibatch
    # minibatches = minibatches[:1]  # Comment this line to process all batches

    
    # Initialize output files
    authorships_file = os.path.join(output_dir, 'authorships.csv')
    citations_file = os.path.join(output_dir, 'citation_edges.csv')
    
    # Write headers for output files
    with open(authorships_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['researcher_id', 'paper_id', 'is_first_author', 'is_last_author'])
    
    with open(citations_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['citing_paper_id', 'cited_paper_id', 'is_influential', 'context'])
    
    # Collect unique author IDs
    unique_author_ids: Set[str] = set()
    
    # Process each minibatch
    headers = {'x-api-key': S2_API_KEY} if S2_API_KEY != "YOUR_KEY_HERE" else {}
    
    for batch_idx, minibatch in enumerate(tqdm(minibatches, desc="Processing paper batches")):
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Make API request
                response = requests.post(
                    'https://api.semanticscholar.org/graph/v1/paper/batch',
                    params={'fields': 'externalIds,authors,citations,references'},
                    json={"ids": minibatch},
                    headers=headers
                )
                
                if response.status_code == 429:
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"Rate limited (429) in batch {batch_idx}. Retrying in 2 seconds... (attempt {retry_count}/{max_retries})")
                        time.sleep(2)
                        continue
                    else:
                        print(f"Rate limited (429) in batch {batch_idx}. Max retries reached. Skipping batch.")
                        break
                
                if response.status_code != 200:
                    print(f"Error in batch {batch_idx}: Status {response.status_code}")
                    print(f"Response: {response.text}")
                    
                    # Log invalid paper IDs if it's a 400 error with "No valid paper ids given"
                    if response.status_code == 400 and "No valid paper ids given" in response.text:
                        # Create logs directory if it doesn't exist
                        logs_dir = os.path.join(os.path.dirname(output_dir), "logs")
                        os.makedirs(logs_dir, exist_ok=True)
                        
                        # Log the invalid paper IDs from this batch
                        invalid_ids_file = os.path.join(logs_dir, "invalid_paper_ids.txt")
                        with open(invalid_ids_file, 'a', encoding='utf-8') as f:
                            f.write(f"Batch {batch_idx} - Invalid paper IDs:\n")
                            for paper_id in minibatch:
                                f.write(f"  {paper_id}\n")
                            f.write("\n")
                        
                        print(f"Invalid paper IDs from batch {batch_idx} logged to: {invalid_ids_file}")
                    
                    break  # Exit retry loop for non-429 errors
                
                # If we get here, the request was successful
                papers_data = response.json()
                
                # Check if papers_data is a list before processing
                if not isinstance(papers_data, list):
                    print(f"Error in batch {batch_idx}: API did not return a list. Response: {papers_data}")
                    break
                
                # Process each paper in the batch
                for paper in papers_data:
                    if not paper:  # Skip null/empty responses
                        continue
                    
                    # Additional check to ensure paper is a dictionary
                    if not isinstance(paper, dict):
                        print(f"Skipping invalid paper entry in batch {batch_idx}: {paper}")
                        continue
                    
                    paper_id = paper.get('paperId')
                    external_ids = paper.get('externalIds', {})
                    doi = external_ids.get('DOI', '')
                    authors = paper.get('authors', [])
                    citations = paper.get('citations', [])
                    references = paper.get('references', [])
                    
                    # Ensure authors, citations, and references are lists
                    if not isinstance(authors, list):
                        authors = []
                    if not isinstance(citations, list):
                        citations = []
                    if not isinstance(references, list):
                        references = []
                    
                    # Process authorships
                    for i, author in enumerate(authors):
                        if author and author.get('authorId'):
                            author_id = author['authorId']
                            unique_author_ids.add(author_id)
                            
                            is_first = i == 0
                            is_last = i == len(authors) - 1
                            
                            with open(authorships_file, 'a', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                writer.writerow([author_id, doi, is_first, is_last])
                    
                    # Process citations (references)
                    for ref in references:
                        if ref and ref.get('paperId'):
                            with open(citations_file, 'a', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                writer.writerow([
                                    paper_id,  # citing_paper_id
                                    ref['paperId'],  # cited_paper_id
                                    '',  # is_influential leave blank
                                    ''  # context leave blank
                                ])
                    
                    # Process citations (citations)
                    for cit in citations:
                        if cit and cit.get('paperId'):
                            with open(citations_file, 'a', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                writer.writerow([
                                    cit['paperId'],  # citing_paper_id
                                    paper_id,  # cited_paper_id
                                    '',  # is_influential leave blank
                                    ''  # context leave blank
                                ])
                
                # Successfully processed the batch, break out of retry loop
                break
                
            except Exception as e:
                print(f"Error processing batch {batch_idx}: {str(e)}")
                break  # Exit retry loop for exceptions

        # Rate limiting
        time.sleep(1)
    
    # Save unique author IDs
    author_ids_file = os.path.join(output_dir, 'author_ids_to_fetch.txt')
    with open(author_ids_file, 'w', encoding='utf-8') as f:
        for author_id in sorted(unique_author_ids):
            f.write(f"{author_id}\n")
    
    print(f"Phase 1 complete. Found {len(unique_author_ids)} unique authors.")
    print(f"Output files saved to: {output_dir}")

def fetch_researcher_profiles(output_dir: str) -> None:
    """
    Phase 2: Fetch researcher profile data from Semantic Scholar API.
    
    Args:
        output_dir: Directory containing author_ids_to_fetch.txt and where to save researcher_profiles.csv
    """
    # Read author IDs
    author_ids_file = os.path.join(output_dir, 'author_ids_to_fetch.txt')
    if not os.path.exists(author_ids_file):
        print(f"Error: {author_ids_file} not found. Run Phase 1 first.")
        return
    
    author_ids = []
    with open(author_ids_file, 'r', encoding='utf-8') as f:
        # This line correctly filters out any blank lines
        author_ids = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(author_ids)} author IDs to process")
    
    # Split into minibatches
    batch_size = 500
    minibatches = [author_ids[i:i + batch_size] for i in range(0, len(author_ids), batch_size)]

    # Initialize output file
    profiles_file = os.path.join(output_dir, 'researcher_profiles.csv')
    
    # Write header
    with open(profiles_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['researcher_id', 'first_name', 'last_name', 'h_index', 'total_citations', 'latest_affiliation', 'homepage'])   
    
    # Process each minibatch
    headers = {'x-api-key': S2_API_KEY} if S2_API_KEY != "YOUR_KEY_HERE" else {}
    
    for batch_idx, minibatch in enumerate(tqdm(minibatches, desc="Processing author batches")):
        try:
            # Make API request - MODIFICATION 2: Added 'homepage' to the fields
            response = requests.post(
                'https://api.semanticscholar.org/graph/v1/author/batch',
                params={'fields': 'name,hIndex,citationCount,affiliations,homepage'},
                json={"ids": minibatch},
                headers=headers
            )
            
            # This check is good, but won't catch cases where the server returns 200 OK with an error message in the body
            if response.status_code != 200:
                print(f"Error in batch {batch_idx}: Status {response.status_code}")
                print(f"Response: {response.text}")
                continue
            
            authors_data = response.json()
            
            # ensure authors_data is a list before looping
            if not isinstance(authors_data, list):
                print(f"Error in batch {batch_idx}: API did not return a list. Response: {authors_data}")
                continue

            # Process each author in the batch
            for author in authors_data:
                # This robustly handles both `null` responses from the API and any unexpected non-dict items
                if not isinstance(author, dict):
                    print(f"Skipping invalid author entry in batch {batch_idx}: {author}")
                    continue
                
                # The rest of your code is correct, now that it's protected from bad data
                author_id = author.get('authorId')
                name = author.get('name', '')
                h_index = author.get('hIndex', 0)
                citation_count = author.get('citationCount', 0)
                affiliations = author.get('affiliations', [])
                homepage = author.get('homepage', '')
                
                name_parts = name.split() if name else ['', '']
                first_name = name_parts[0] if len(name_parts) > 0 else ''
                last_name = name_parts[-1] if len(name_parts) > 1 else ''
                
                latest_affiliation = ''
                if affiliations and isinstance(affiliations, list):
                    # Filter out any non-string items in the affiliations list
                    valid_affiliations = [aff for aff in affiliations if isinstance(aff, str)]
                    if valid_affiliations:
                        # Take the last affiliation as the most recent one
                        latest_affiliation = valid_affiliations[-1]
                elif isinstance(affiliations, str):
                    # If affiliations is a string, use it directly
                    latest_affiliation = affiliations
                
                with open(profiles_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([author_id, first_name, last_name, h_index, citation_count, latest_affiliation, homepage])
            
            time.sleep(1)
            
        except json.JSONDecodeError:
            print(f"Error decoding JSON in batch {batch_idx}. Response was not valid JSON.")
            print(f"Response Text: {response.text}")
            continue
        except Exception as e:
            print(f"An unexpected error occurred in batch {batch_idx}: {str(e)}")
            continue
    
    print(f"Phase 2 complete. Researcher profiles saved to: {profiles_file}")

def main():
    """
    Main function to run both phases of the data gathering process.
    """
    # Configuration - use absolute paths based on script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    input_csv_path = os.path.join(project_root, "data", "papers_data_classified.csv")
    output_dir = os.path.join(project_root, "data")
    
    print("Starting Semantic Scholar data gathering process...")
    print(f"Input file: {input_csv_path}")
    print(f"Output directory: {output_dir}")
    print()
    
    # Check if input file exists
    if not os.path.exists(input_csv_path):
        print(f"Error: Input file not found: {input_csv_path}")
        return
    
    # Phase 1: Fetch relational data
    print("=== Phase 1: Fetching Relational Data ===")
    fetch_relational_data(input_csv_path, output_dir)
    print()
    
    # Phase 2: Fetch researcher profiles
    print("=== Phase 2: Fetching Researcher Profiles ===")
    fetch_researcher_profiles(output_dir)
    print()
    
    print("Data gathering process complete!")


if __name__ == "__main__":
    main()
