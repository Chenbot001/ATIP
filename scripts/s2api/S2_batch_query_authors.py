import requests
import csv
import os
import time
import json
from tqdm import tqdm
from typing import List, Set, Dict, Any

# API Configuration
S2_API_KEY = "39B73CXWua7xhzGlxFrNJ5wY6uIjXCna9sLxWL2w"  # Replace with your actual API key

def fetch_author_profiles(output_dir: str) -> None:
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
        writer.writerow(['author_id', 'first_name', 'last_name', 'h_index', 'total_citations', 'latest_affiliation', 'homepage'])   
    
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
    output_dir = "./data"
    # Phase 2: Fetch researcher profiles
    print("=== Phase 2: Fetching Author Profiles ===")
    fetch_author_profiles(output_dir)
    print()
    
    print("Data gathering process complete!")


if __name__ == "__main__":
    main()
