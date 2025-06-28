"""
Semantic Scholar Abstract Extractor for CSV Processing

This script reads a CSV file containing publication titles, searches for each publication
on Semantic Scholar to retrieve its abstract, and saves the enriched data to a new CSV file.

The script includes robust error handling, anti-blocking mechanisms, and incremental saving
for large datasets.

Required Libraries:
    - pandas
    - requests
    - json
    - time
    - tqdm
    - argparse
    - os
    - sys
    - typing
    - arxiv
    - thefuzz

Usage:
    python get_abstract.py --input "path/to/input.csv"
    python get_abstract.py --input "C:\Eric\Projects\AI_Researcher_Network\data\ACL25_ThemeData.csv"
"""

import pandas as pd
import requests
import json
import time
import argparse
import os
import sys
from typing import Optional, Dict, Any, Literal
from tqdm import tqdm
import arxiv
from thefuzz import fuzz

def search_paper_by_title(title: str, api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Search for a paper by title using the Semantic Scholar API.
    
    Args:
        title (str): The title of the paper to search for.
        api_key (str, optional): Semantic Scholar API key for higher rate limits.
        
    Returns:
        Optional[Dict[str, Any]]: Paper data if found, None otherwise.
    """
    # Semantic Scholar API endpoint for paper search
    base_url = "https://api.semanticscholar.org/graph/v1"
    search_url = f"{base_url}/paper/search"
    
    # Headers for the request
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'AI_Researcher_Network/1.0'
    }
    
    # Add API key if provided
    if api_key:
        headers['x-api-key'] = api_key
    
    # Parameters for the search
    params = {
        'query': title,
        'limit': 5,  # Limit results to top 5 matches
        'fields': 'paperId,title,abstract,url,year,authors.name,venue'
    }
    
    try:
        response = requests.get(search_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('data') and len(data['data']) > 0:
            # Return the first (most relevant) result
            return data['data'][0]
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error making API request for '{title}': {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response for '{title}': {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for '{title}': {e}")
        return None

def search_arxiv_by_title(title: str, min_similarity_score: int = 85) -> Optional[str]:
    """
    Search for a paper by title using the arXiv API with advanced search strategies.
    
    Args:
        title (str): The title of the paper to search for.
        min_similarity_score (int): Minimum similarity score for confident match (default: 85).
        
    Returns:
        Optional[str]: Abstract if found, None otherwise.
    """
    if not title or pd.isna(title) or title.strip() == "":
        return None
    
    clean_title = title.strip().replace('–', '-').replace('—', '-')
    
    # Strategy 1: Search with the colon removed (often problematic in search queries)
    title_no_colon = clean_title.replace(":", "")
    
    # Strategy 2: Search for just the unique part before the colon
    title_short = clean_title.split(":")[0] if ":" in clean_title else clean_title
    
    # List of search queries to try in order of preference
    search_queries = [
        clean_title,      # Try the original title first
        title_no_colon,   # Then try without the colon
        title_short       # Finally, try just the unique part
    ]
    
    for query in search_queries:
        try:
            search = arxiv.Search(query=query, max_results=5)
            results = list(search.results())
            
            if not results:
                continue
            
            for result in results:
                score = fuzz.ratio(clean_title.lower(), result.title.lower())
                
                if score >= min_similarity_score:
                    return result.summary.replace('\n', ' ')
                    
        except Exception as e:
            print(f"Error searching arXiv with query '{query}': {e}")
            continue
    
    return None

def get_abstract_by_title(title: str, api_key: Optional[str] = None, source: str = "semantic_scholar") -> Optional[str]:
    """
    Get the abstract of a paper by its title using the specified API source.
    
    Args:
        title (str): The title of the paper to search for.
        api_key (str, optional): API key for higher rate limits (Semantic Scholar only).
        api_source (str): API source to use ("semantic_scholar" or "arxiv").
        
    Returns:
        Optional[str]: The abstract if found, None otherwise.
    """
    if not title or pd.isna(title) or title.strip() == "":
        return None
        
    if source.lower() == "arxiv":
        return search_arxiv_by_title(title.strip())
    elif source.lower() == "semantic_scholar":
        paper_data = search_paper_by_title(title.strip(), api_key)
        
        if paper_data:
            abstract = paper_data.get('abstract')
            if abstract and abstract.strip():
                return abstract.strip()
            else:
                return None
        else:
            return None

def save_dataframe_incrementally(df: pd.DataFrame, output_file: str, mode: Literal['w', 'a'] = 'w'):
    """
    Save DataFrame to CSV file with proper encoding and error handling.
    
    Args:
        df (pd.DataFrame): DataFrame to save.
        output_file (str): Path to output CSV file.
        mode (Literal['w', 'a']): File mode ('w' for write, 'a' for append).
    """
    try:
        if mode == 'w':
            df.to_csv(output_file, index=False, encoding='utf-8')
        else:
            df.to_csv(output_file, mode=mode, header=False, 
                      index=False, encoding='utf-8')
    except Exception as e:
        print(f"Error saving to {output_file}: {e}")
        # Try saving with a backup filename
        backup_file = output_file.replace('.csv', f'_backup_{int(time.time())}.csv')
        try:
            df.to_csv(backup_file, index=False, encoding='utf-8')
            print(f"Data saved to backup file: {backup_file}")
        except Exception as backup_error:
            print(f"Failed to save backup file: {backup_error}")

def process_csv(input_file: str, api_key: Optional[str] = None, 
                               save_interval: int = 50, source: str = "semantic_scholar") -> None:
    """
    Process a CSV file to add abstracts for each publication title.
    
    Args:
        input_file (str): Path to input CSV file.
        api_key (str, optional): API key for higher rate limits (Semantic Scholar only).
        save_interval (int): Number of rows to process before saving incrementally.
        source (str): API source to use ("semantic_scholar" or "arxiv").
    """
    try:
        # Read the CSV file
        print(f"Reading CSV file: {input_file}")
        df = pd.read_csv(input_file, encoding='utf-8')
        
        # Create 'Abstract' column if not present
        if 'Abstract' not in df.columns:
            df['Abstract'] = None
        else:
            # Ensure the Abstract column is of object (string) dtype to avoid FutureWarning
            df['Abstract'] = df['Abstract'].astype('object')
        
        # Use the input file as the output file (overwrite)
        output_file = input_file
        
        print(f"Processing {len(df)} rows...")
        print(f"Results will be saved back to: {output_file}")
        
        # Process each row
        processed_count = 0
        success_count = 0
        error_count = 0
        
        # Create progress bar
        with tqdm(total=len(df), desc="Processing papers") as pbar:
            for index, row in df.iterrows():
                try:
                    title = row['Title']
                    
                    # Skip if abstract already exists and is not empty
                    existing_abstract = row['Abstract']
                    
                    if (pd.notna(existing_abstract) and 
                        str(existing_abstract).strip() != "" and 
                        str(existing_abstract).strip().lower() != "none" and
                        str(existing_abstract).strip().lower() != "nan"):
                        pbar.set_postfix({"Status": "Skipped (abstract exists)"})
                        pbar.update(1)
                        processed_count += 1
                        continue
                    
                    # Get abstract
                    abstract = get_abstract_by_title(title, api_key, source)
                    
                    
                    # If no abstract found, retry once after waiting (in case of rate limiting)
                    if not abstract:
                        pbar.set_postfix({"Status": "No abstract found, retrying..."})
                        time.sleep(1.5)  # Wait before retry
                        abstract = get_abstract_by_title(title, api_key, source)
                    
                    if abstract:
                        df.at[index, 'Abstract'] = abstract
                        success_count += 1
                        pbar.set_postfix({"Status": "Abstract found"})
                    else:
                        pbar.set_postfix({"Status": "No abstract found for title: " + title})
                        error_count += 1
                    
                    # Rate limiting
                    time.sleep(1.5)
                    
                    processed_count += 1
                    pbar.update(1)
                    
                    # Incremental saving
                    if processed_count % save_interval == 0:
                        print(f"\nSaving progress after {processed_count} rows...")
                        save_dataframe_incrementally(df, output_file)
                        
                except Exception as e:
                    print(f"\nError processing row {index} with title '{title}': {e}")
                    error_count += 1
                    processed_count += 1
                    pbar.update(1)
                    continue
        
        # Final save
        print(f"\nSaving final results...")
        save_dataframe_incrementally(df, output_file)
        
        # Print summary
        print(f"\n{'='*50}")
        print(f"PROCESSING COMPLETE")
        print(f"{'='*50}")
        print(f"Total rows processed: {processed_count}")
        print(f"Successful abstract retrievals: {success_count}")
        print(f"Failed/empty abstracts: {error_count}")
        print(f"Output file: {output_file}")
        
        # Calculate success rate
        if processed_count > 0:
            success_rate = (success_count / processed_count) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: The CSV file '{input_file}' is empty.")
    except pd.errors.ParserError as e:
        print(f"Error parsing CSV file '{input_file}': {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    """
    Main function to handle command-line arguments and execute the processing.
    """
    # Comment out argument parsing logic and hardcode the input file
    # parser = argparse.ArgumentParser(
    #     description="Extract abstracts from Semantic Scholar for papers in a CSV file"
    # )
    # parser.add_argument(
    #     '--input', 
    #     type=str, 
    #     required=True,
    #     help='Path to input CSV file containing paper titles'
    # )
    # parser.add_argument(
    #     '--api-key', 
    #     type=str, 
    #     default=None,
    #     help='Semantic Scholar API key for higher rate limits'
    # )
    # parser.add_argument(
    #     '--save-interval', 
    #     type=int, 
    #     default=50,
    #     help='Number of rows to process before saving incrementally (default: 50)'
    # )
    # 
    # args = parser.parse_args()
    
    # Hardcoded input file path
    input_file = "C:/Eric/Projects/AI_Researcher_Network/data/ACL25_ThemeData_abs.csv"
    api_key = "39B73CXWua7xhzGlxFrNJ5wY6uIjXCna9sLxWL2w"
    save_interval = 50
    # source = "semantic_scholar"
    source = "arxiv"
    
    # Validate input file
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    if not input_file.lower().endswith('.csv'):
        print(f"Error: Input file '{input_file}' is not a CSV file.")
        sys.exit(1)
    
    print("Semantic Scholar Abstract Extractor")
    print("=" * 40)
    print(f"Input file: {input_file}")
    print(f"API source: {source}")
    print(f"API key provided: {'Yes' if api_key else 'No'}")
    print(f"Save interval: {save_interval} rows")
    print("-" * 40)
    
    # Process the CSV file
    process_csv(input_file, api_key, save_interval, source)

if __name__ == "__main__":
    main()
