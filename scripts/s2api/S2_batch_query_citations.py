import requests
import csv
import os
import time
import json
import pandas as pd
from tqdm import tqdm
from typing import List, Set, Dict, Any

# API Configuration
S2_API_KEY = "39B73CXWua7xhzGlxFrNJ5wY6uIjXCna9sLxWL2w"  # Replace with your actual API key

def fetch_citation_counts(input_csv_path: str, output_csv_path: str) -> None:
    """
    Fetch citation counts for papers from Semantic Scholar API and update the dataframe.
    
    Args:
        input_csv_path: Path to the input CSV file containing paper IDs
        output_csv_path: Path to save the updated CSV file
    """
    # Load the CSV file into a dataframe
    print(f"Loading data from {input_csv_path}...")
    df = pd.read_csv(input_csv_path)
    
    # Add citation_count column if it doesn't exist
    if 'citation_count' not in df.columns:
        df['citation_count'] = None
    
    # Filter papers that have s2_id
    papers_with_s2_id = df[df['s2_id'].notna() & (df['s2_id'] != '')].copy()
    
    if papers_with_s2_id.empty:
        print("No papers with s2_id found in the dataset.")
        return
    
    print(f"Found {len(papers_with_s2_id)} papers with s2_id to process")
    
    # Get list of s2_ids
    paper_ids = papers_with_s2_id['s2_id'].tolist()
    
    # Split into minibatches of 500
    batch_size = 500
    minibatches = [paper_ids[i:i + batch_size] 
                   for i in range(0, len(paper_ids), batch_size)]
    
    # Testing: only process first minibatch
    # minibatches = minibatches[:1]  # Comment this line to process all batches
    
    # Dictionary to store citation counts
    citation_counts = {}
    
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
                    params={'fields': 'paperId,citationCount'},
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
                        logs_dir = os.path.join(os.path.dirname(os.path.dirname(input_csv_path)), "logs")
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
                    citation_count = paper.get('citationCount', 0)
                    
                    # Ensure citation_count is an integer
                    try:
                        citation_count = int(citation_count) if citation_count is not None else 0
                    except (ValueError, TypeError):
                        citation_count = 0
                    
                    if paper_id:
                        citation_counts[paper_id] = citation_count
                
                # Successfully processed the batch, break out of retry loop
                break
                
            except Exception as e:
                print(f"Error processing batch {batch_idx}: {str(e)}")
                break  # Exit retry loop for exceptions

        # Rate limiting
        time.sleep(1)
    
    # Update the dataframe with citation counts
    print(f"Updating dataframe with citation counts for {len(citation_counts)} papers...")
    
    # Create a mapping from s2_id to citation_count
    df['citation_count'] = df['s2_id'].map(citation_counts)
    
    # Fill NaN values with 0 for papers that don't have citation data
    df['citation_count'] = df['citation_count'].fillna(0)
    
    # Ensure citation_count column is integer type
    df['citation_count'] = df['citation_count'].astype(int)
    
    # Save the updated dataframe
    print(f"Saving updated dataframe to {output_csv_path}...")
    df.to_csv(output_csv_path, index=False)
    
    print(f"Successfully updated {len(citation_counts)} papers with citation counts")
    print(f"Updated dataframe saved to: {output_csv_path}")


def main():
    """
    Main function to fetch citation counts and update the dataframe.
    """
    # Configuration - use absolute paths based on script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    input_csv_path = os.path.join(project_root, "data", "paper_info.csv")
    output_csv_path = os.path.join(project_root, "data", "paper_info_with_citations.csv")
    
    print("Starting Semantic Scholar citation count fetching process...")
    print(f"Input file: {input_csv_path}")
    print(f"Output file: {output_csv_path}")
    print()
    
    # Check if input file exists
    if not os.path.exists(input_csv_path):
        print(f"Error: Input file not found: {input_csv_path}")
        return
    
    # Fetch citation counts and update dataframe
    fetch_citation_counts(input_csv_path, output_csv_path)
    print()
    
    print("Citation count fetching process complete!")

if __name__ == "__main__":
    main()
