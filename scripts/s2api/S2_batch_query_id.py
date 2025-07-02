import pandas as pd
import os
import requests
import time

def extract_acl_ids_from_dataframe(df):
    """
    Extract acl_id values from a dataframe and format them for API requests.
    
    Args:
        df (DataFrame): Dataframe with acl_id column
        
    Returns:
        list: List of acl_id values as strings with 'ACL:' prefix
    """
    # Extract acl_id values, convert to strings, and add 'ACL:' prefix
    acl_ids = ['ACL:' + str(id_val) for id_val in df['acl_id']]
    return acl_ids

def extract_acl_ids(csv_filepath):
    """
    Read a CSV file and extract acl_id column values.
    
    Args:
        csv_filepath (str): Path to the CSV file
        
    Returns:
        tuple: (list of acl_id values as strings with 'ACL:' prefix, DataFrame)
    """
    try:
        # Check if file exists
        if not os.path.exists(csv_filepath):
            print(f"Error: File '{csv_filepath}' does not exist.")
            return [], None
        
        # Read the entire CSV file
        df = pd.read_csv(csv_filepath)
        
        # Check if acl_id column exists
        if 'acl_id' not in df.columns:
            print("Error: 'acl_id' column not found in the CSV file.")
            print(f"Available columns: {list(df.columns)}")
            return [], None
        
        # Extract acl_id values
        acl_ids = extract_acl_ids_from_dataframe(df)
        
        print(f"Successfully loaded {len(df)} rows from CSV file.")
        print(f"Total acl_id values to process: {len(acl_ids)}")
        
        return acl_ids, df
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return [], None

def batch_request(api_key, id_list, max_retries=3):
    """
    Make a batch request to Semantic Scholar API for multiple paper IDs with retry logic
    
    Args:
        api_key (str): Semantic Scholar API key
        id_list (list): List of paper IDs to fetch
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        dict: JSON response from the API
    """
    for attempt in range(max_retries + 1):
        try:
            r = requests.post(
                'https://api.semanticscholar.org/graph/v1/paper/batch',
                params={'fields': 'paperId,corpusId,externalIds'},
                headers={'x-api-key': api_key},
                json={"ids": id_list},
                timeout=30  # Add timeout to prevent hanging requests
            )
            r.raise_for_status()  # Raise exception for HTTP error status codes
            return r.json()
            
        except (requests.exceptions.ConnectionError, 
                requests.exceptions.Timeout, 
                requests.exceptions.RequestException) as e:
            
            if attempt < max_retries:
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                print(f"Request failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Request failed after {max_retries + 1} attempts: {e}")
                print("Returning empty response to continue processing...")
                return [None] * len(id_list)  # Return None for each ID to skip this batch

def populate_dataframe(df, api_response):
    """
    Populate the dataframe with data from the API response.
    
    Args:
        df (DataFrame): Original dataframe with acl_id column
        api_response (list): List of dictionaries from the API response
        
    Returns:
        DataFrame: Updated dataframe with new columns populated
    """
    # Add new columns if they don't exist
    if 'corpus_id' not in df.columns:
        df['corpus_id'] = pd.Series(dtype='Int64')  # Use nullable integer dtype
    if 's2_id' not in df.columns:
        df['s2_id'] = None
    if 'DOI' not in df.columns:
        df['DOI'] = None
    
    # Ensure corpus_id column is Int64 dtype
    if df['corpus_id'].dtype != 'Int64':
        df['corpus_id'] = df['corpus_id'].astype('Int64')
    
    # Create a mapping from ACL ID to row index for quick lookup
    acl_to_index = {}
    for idx, acl_id in enumerate(df['acl_id']):
        # Remove 'ACL:' prefix for comparison
        clean_acl_id = str(acl_id).replace('ACL:', '')
        acl_to_index[clean_acl_id] = idx
    
    # Iterate through API response and populate dataframe
    for paper_data in api_response:
        if paper_data is None:
            continue
            
        # Handle case where paper_data might be a string instead of dict
        if not isinstance(paper_data, dict):
            print(f"Warning: Skipping non-dict paper data: {type(paper_data)} - {paper_data}")
            continue
            
        # Extract ACL ID from externalIds
        external_ids = paper_data.get('externalIds', {})
        acl_id = external_ids.get('ACL')
        
        if acl_id and acl_id in acl_to_index:
            row_idx = acl_to_index[acl_id]
            
            # Get corpusId and convert to integer if it exists
            corpus_id = paper_data.get('corpusId')
            if corpus_id is not None:
                corpus_id = int(corpus_id)
            
            # Populate the row with API data
            df.at[row_idx, 'corpus_id'] = corpus_id
            df.at[row_idx, 's2_id'] = paper_data.get('paperId')
            df.at[row_idx, 'DOI'] = external_ids.get('DOI')
            
            print(f"Matched ACL ID {acl_id}: corpusId={corpus_id}, paperId={paper_data.get('paperId')}, DOI={external_ids.get('DOI')}")
        else:
            if acl_id:
                print(f"No match found for ACL ID: {acl_id}")
            else:
                print(f"No ACL ID found in paper data: {paper_data.get('paperId', 'Unknown')}")
    
    # Ensure corpus_id column maintains Int64 dtype after updates
    df['corpus_id'] = df['corpus_id'].astype('Int64')
    
    return df

def process_in_batches(df, acl_ids, api_key, batch_size=500, delay=2):
    """
    Process the dataframe in batches, making API requests for each batch.
    
    Args:
        df (DataFrame): Dataframe to populate
        acl_ids (list): List of all ACL IDs
        api_key (str): Semantic Scholar API key
        batch_size (int): Number of papers to process per batch
        delay (int): Delay in seconds between requests
        
    Returns:
        DataFrame: Updated dataframe
    """
    total_papers = len(acl_ids)
    total_batches = (total_papers + batch_size - 1) // batch_size  # Ceiling division
    save_interval = 5  # Save every 5 batches
    
    print(f"\nProcessing {total_papers} papers in {total_batches} batches of {batch_size}")
    print(f"Will save progress every {save_interval} batches")
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, total_papers)
        
        batch_ids = acl_ids[start_idx:end_idx]
        
        print(f"\n--- Batch {batch_num + 1}/{total_batches} ---")
        print(f"Processing papers {start_idx + 1} to {end_idx} ({len(batch_ids)} papers)")
        
        # Make API request for this batch
        response = batch_request(api_key, batch_ids)
        if response is not None:
            print(f"API Response received with {len(response)} papers")
        else:
            print("API Response was None - skipping this batch")
            continue
        
        # Populate dataframe with this batch's data
        df = populate_dataframe(df, response)
        
        # Save incrementally every 5 batches (or on the last batch)
        if (batch_num + 1) % save_interval == 0 or batch_num == total_batches - 1:
            temp_output_filepath = "data/paper_info_temp.csv"
            df.to_csv(temp_output_filepath, index=False)
            print(f"✓ Progress saved to {temp_output_filepath} (Batch {batch_num + 1}/{total_batches})")
        
        # Add delay between requests (except for the last batch)
        if batch_num < total_batches - 1:
            print(f"Waiting {delay} second before next batch...")
            time.sleep(delay)
    
    return df

def main():
    """Main function to run the script."""
    # Hardcoded filepath
    csv_filepath = "data/paper_info.csv"
    S2_API_KEY = "39B73CXWua7xhzGlxFrNJ5wY6uIjXCna9sLxWL2w"

    print(f"Reading from: {csv_filepath}")
    acl_ids, paper_info = extract_acl_ids(csv_filepath)
    
    if not acl_ids or paper_info is None:
        print("Failed to extract ACL IDs or load dataframe. Exiting.")
        return
    
    # Process the entire dataframe in batches
    updated_df = process_in_batches(paper_info, acl_ids, S2_API_KEY, batch_size=500, delay=1)
    
    # Show summary of populated data
    print("\n" + "="*80)
    print("FINAL SUMMARY:")
    print("="*80)
    print(f"Total rows: {len(updated_df)}")
    print(f"Rows with corpus_id: {updated_df['corpus_id'].notna().sum()}")
    print(f"Rows with s2_id: {updated_df['s2_id'].notna().sum()}")
    print(f"Rows with DOI: {updated_df['DOI'].notna().sum()}")
    
    # Save the updated dataframe to a new CSV file
    output_filepath = "data/paper_info_full.csv"
    updated_df.to_csv(output_filepath, index=False)
    print(f"\nDataframe saved to: {output_filepath}")

if __name__ == "__main__":
    main()
