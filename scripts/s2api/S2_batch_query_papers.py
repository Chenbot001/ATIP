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
            if 's2_id' in row and row['s2_id']:
                paper_ids.append(row['s2_id'])
    
    print(f"Found {len(paper_ids)} paper IDs to process")
    
    
    # Split into minibatches of 500
    batch_size = 500
    minibatches = [paper_ids[i:i + batch_size] 
                   for i in range(0, len(paper_ids), batch_size)]
    
    # Testing: only process first minibatch
    # minibatches = minibatches[:1]  # Comment this line to process all batches

    
    # Initialize output files
    authorships_file = os.path.join(output_dir, 'authorships.csv')
    citations_file = os.path.join(output_dir, 'citation_edges.csv')
    
    # Write headers for output files
    with open(authorships_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['researcher_id', 'paper_id', 'author_name', 'is_first_author', 'is_last_author','paper_title'])
    
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
                    params={'fields': 'paperId,externalIds,authors,citations,references,title'},
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
                            for id in minibatch:
                                f.write(f"  {id}\n")
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
                    
                    paper_id = paper.get('paperId', '')
                    authors = paper.get('authors', [])
                    citations = paper.get('citations', [])
                    references = paper.get('references', [])
                    paper_title = paper.get('title', '')
                    
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
                            author_name = author['name']
                            unique_author_ids.add(author_id)
                            
                            is_first = i == 0
                            is_last = i == len(authors) - 1
                            
                            with open(authorships_file, 'a', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                writer.writerow([author_id, paper_id, author_name, is_first, is_last, paper_title])
                    
                    # Process citations (references)
                    for ref in references:
                        if ref and ref.get('paperId'):
                            with open(citations_file, 'a', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                writer.writerow([
                                    paper_id,  # citing_paper_id (using corpus_id)
                                    ref['paperId'],  # cited_paper_id (using corpus_id)
                                    '',  # is_influential leave blank
                                    ''  # context leave blank
                                ])
                    
                    # Process citations (citations)
                    for cit in citations:
                        if cit and cit.get('paperId'):
                            with open(citations_file, 'a', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                writer.writerow([
                                    cit['paperId'],  # citing_paper_id (using corpus_id)
                                    paper_id,  # cited_paper_id (using corpus_id)
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


def main():
    """
    Main function to run both phases of the data gathering process.
    """
    # Configuration - use absolute paths based on script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    input_csv_path = os.path.join(project_root, "data", "paper_info.csv")
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
    
    print("Data gathering process complete!")

if __name__ == "__main__":
    main()
