import requests
import csv
import os
import time
from tqdm import tqdm
from typing import List, Dict, Tuple, Optional

# API Configuration
S2_API_KEY = "39B73CXWua7xhzGlxFrNJ5wY6uIjXCna9sLxWL2w"
S2_BATCH_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper/batch"

def fetch_relational_data(input_csv_path: str, output_dir: str) -> None:
    """
    Fetch relational data from Semantic Scholar API and update paper information.
    
    Args:
        input_csv_path: Path to the input CSV file containing acl_id and title
        output_dir: Directory to save output files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs("./logs", exist_ok=True)
    
    # Read input CSV and extract acl_id and title
    papers_data = read_input_csv(input_csv_path)
    print(f"Loaded {len(papers_data)} papers from {input_csv_path}")
    
    # Split into minibatches of 500
    minibatches = create_minibatches(papers_data, batch_size=500)
    print(f"Created {len(minibatches)} minibatches")
    
    # Process each minibatch
    all_paper_updates = []
    invalid_papers = []
    
    for i, minibatch in enumerate(tqdm(minibatches, desc="Processing minibatches")):
        print(f"\nProcessing minibatch {i+1}/{len(minibatches)}")
        
        # Format IDs for API call
        formatted_ids = [f"ACL:{paper['acl_id']}" for paper in minibatch]
        
        # Make API call
        response = make_batch_api_call(formatted_ids)
        
        if response is None:
            # If API call failed, mark all papers in this batch as invalid
            invalid_papers.extend([paper['title'] for paper in minibatch])
            continue
        
        # Process response and update paper data
        batch_updates, batch_invalid = process_api_response(minibatch, response)
        all_paper_updates.extend(batch_updates)
        invalid_papers.extend(batch_invalid)
        
        # Rate limiting
        time.sleep(1)
    
    # Update paper_info.csv with new data
    update_paper_info_csv(all_paper_updates, output_dir)
    
    # Save invalid papers to log file
    save_invalid_papers(invalid_papers)
    
    print(f"\nProcessing complete!")
    print(f"Updated {len(all_paper_updates)} papers")
    print(f"Found {len(invalid_papers)} invalid papers")

def read_input_csv(csv_path: str) -> List[Dict[str, str]]:
    """Read input CSV and extract acl_id and title."""
    papers_data = []
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            papers_data.append({
                'acl_id': row['acl_id'],
                'title': row['title']
            })
    
    return papers_data

def create_minibatches(data: List[Dict], batch_size: int) -> List[List[Dict]]:
    """Split data into minibatches of specified size."""
    minibatches = []
    for i in range(0, len(data), batch_size):
        minibatches.append(data[i:i + batch_size])
    return minibatches

def make_batch_api_call(paper_ids: List[str]) -> Optional[List[Dict]]:
    """Make batch API call to Semantic Scholar."""
    headers = {
        'Content-Type': 'application/json'
    }
    
    if S2_API_KEY != "YOUR_KEY_HERE":
        headers['x-api-key'] = S2_API_KEY
    
    payload = {
        "ids": paper_ids,
        "fields": "paperId,corpusId,externalIds"
    }
    
    try:
        response = requests.post(S2_BATCH_ENDPOINT, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return None

def process_api_response(minibatch: List[Dict], api_response: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """Process API response and extract paper updates and invalid papers."""
    updates = []
    invalid_papers = []
    
    # Create a mapping from ACL ID to API response
    response_map = {}
    for item in api_response:
        if item and 'externalIds' in item and 'ACL' in item['externalIds']:
            acl_id = item['externalIds']['ACL']
            response_map[acl_id] = item
    
    # Process each paper in the minibatch
    for paper in minibatch:
        acl_id = paper['acl_id']
        title = paper['title']
        
        if acl_id in response_map:
            # Valid response found
            api_data = response_map[acl_id]
            update = {
                'acl_id': acl_id,
                'title': title,
                'corpus_id': api_data.get('corpusId'),
                's2_id': api_data.get('paperId'),
                'doi': api_data.get('externalIds', {}).get('DOI')
            }
            updates.append(update)
        else:
            # No valid response found
            invalid_papers.append(title)
    
    return updates, invalid_papers

def update_paper_info_csv(paper_updates: List[Dict], output_dir: str) -> None:
    """Update paper_info.csv with new data and save as paper_info_full.csv."""
    # Read existing paper_info.csv
    input_paper_info_path = "data/paper_info.csv"
    output_paper_info_path = os.path.join(output_dir, "paper_info_full.csv")
    
    if not os.path.exists(input_paper_info_path):
        print(f"Warning: {input_paper_info_path} not found. Creating new file with updates only.")
        # Create new file with just the updates
        with open(output_paper_info_path, 'w', newline='', encoding='utf-8') as file:
            if paper_updates:
                fieldnames = paper_updates[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(paper_updates)
        return
    
    # Read existing data
    existing_papers = {}
    with open(input_paper_info_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            existing_papers[row['acl_id']] = row
    
    # Update with new data
    for update in paper_updates:
        acl_id = update['acl_id']
        if acl_id in existing_papers:
            # Update existing record
            existing_papers[acl_id].update(update)
        else:
            # Add new record
            existing_papers[acl_id] = update
    
    # Write updated data
    with open(output_paper_info_path, 'w', newline='', encoding='utf-8') as file:
        if existing_papers:
            fieldnames = list(existing_papers.values())[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_papers.values())
    
    print(f"Updated paper info saved to {output_paper_info_path}")

def save_invalid_papers(invalid_papers: List[str]) -> None:
    """Save invalid paper titles to logs/invalid_papers.txt."""
    log_path = "./logs/invalid_papers.txt"
    
    with open(log_path, 'w', encoding='utf-8') as file:
        for title in invalid_papers:
            file.write(f"{title}\n")
    
    print(f"Invalid papers saved to {log_path}")

if __name__ == "__main__":
    # Configuration
    input_csv_path = "data/paper_info.csv"  # Adjust path as needed
    output_dir = "data"
    
    # Run the main function
    fetch_relational_data(input_csv_path, output_dir)
