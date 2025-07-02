import pandas as pd
import numpy as np
import requests
import time
import json
from tqdm import tqdm

def test_missing_values():
    """
    Test script to count rows with empty or None values in corpus_id, s2_id, or DOI columns
    """
    try:
        # Load the paper_info.csv file
        print("Loading paper_info_updated.csv...")
        df = pd.read_csv('./data/paper_info_updated.csv')
        
        print(f"Total rows in dataset: {len(df)}")
        print(f"Columns in dataset: {list(df.columns)}")
        
        # Check if the required columns exist
        required_columns = ['corpus_id', 's2_id']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Warning: Missing columns: {missing_columns}")
            return None, None
        
        # Count rows where any of the specified columns is empty or None
        # Consider empty strings, None, NaN, and whitespace-only strings as empty
        empty_mask = (
            df['corpus_id'].isna() | 
            (df['corpus_id'].astype(str).str.strip() == '') |
            (df['corpus_id'].astype(str).str.strip() == 'nan') |
            (df['corpus_id'] == 0) |
            df['s2_id'].isna() | 
            (df['s2_id'].astype(str).str.strip() == '') |
            (df['s2_id'].astype(str).str.strip() == 'nan')
        )
        
        rows_with_empty_values = empty_mask.sum()
        
        print(f"\nResults:")
        print(f"Rows with empty or None values in any of (corpus_id, s2_id, DOI): {rows_with_empty_values}")
        print(f"Percentage of rows with missing values: {(rows_with_empty_values / len(df)) * 100:.2f}%")
        
        # Show breakdown by column
        print(f"\nBreakdown by column:")
        for col in required_columns:
            if col == 'corpus_id':
                col_empty = (
                    df[col].isna() | 
                    (df[col].astype(str).str.strip() == '') |
                    (df[col].astype(str).str.strip() == 'nan') |
                    (df[col] == 0)
                ).sum()
            else:
                col_empty = (
                    df[col].isna() | 
                    (df[col].astype(str).str.strip() == '') |
                    (df[col].astype(str).str.strip() == 'nan')
                ).sum()
            print(f"  {col}: {col_empty} empty values ({col_empty/len(df)*100:.2f}%)")
        
        return df, empty_mask
        
    except FileNotFoundError:
        print("Error: paper_info.csv not found in ./data/ directory")
        return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def search_by_title(api_key, title):
    """
    Search for a paper by title using Semantic Scholar API
    
    Args:
        api_key (str): Semantic Scholar API key
        title (str): Paper title to search for
    
    Returns:
        dict: Paper information if found, None otherwise
    """
    try:
        r = requests.get(
            'https://api.semanticscholar.org/graph/v1/paper/search',
            headers={'x-api-key': api_key},
            params={
                'query': title,
                'limit': 1,
                'fields': 'paperId,corpusId,externalIds'
            },
            timeout=10
        )
        
        if r.status_code == 200:
            response = r.json()
            if response.get('data') and len(response['data']) > 0:
                paper = response['data'][0]
                return {
                    'paperId': paper.get('paperId'),
                    'corpusId': paper.get('corpusId'),
                    'externalIds': paper.get('externalIds', {})
                }
        return None
    except Exception as e:
        print(f"Error searching for title '{title[:50]}...': {e}")
        return None

def fill_missing_values(df, empty_mask, api_key):
    """
    Fill missing values by searching Semantic Scholar API
    
    Args:
        df (pd.DataFrame): DataFrame with paper information
        empty_mask (pd.Series): Boolean mask of rows with missing values
        api_key (str): Semantic Scholar API key
    
    Returns:
        pd.DataFrame: Updated DataFrame with filled values
    """
    print(f"\nStarting to fill missing values for {empty_mask.sum()} rows...")
    
    # Create a copy to avoid modifying the original
    df_updated = df.copy()
    filled_count = 0
    error_count = 0
    
    # Get rows with missing values
    missing_rows = df_updated[empty_mask].copy()
    
    try:
        for idx, row in tqdm(missing_rows.iterrows(), total=len(missing_rows), desc="Filling missing values"):
            try:
                title = row['title']
                if pd.isna(title) or str(title).strip() == '':
                    print(f"Row {idx}: Skipping - no title available")
                    continue
                    
                print(f"Row {idx}: Searching for '{title[:60]}...'")
                
                # Search for the paper
                result = search_by_title(api_key, title)
                
                if result:
                    # Update missing values
                    updated = False
                    
                    # Fill corpus_id if missing or 0
                    if pd.isna(df_updated.at[idx, 'corpus_id']) or str(df_updated.at[idx, 'corpus_id']).strip() in ['', 'nan', '0']:
                        if result.get('corpusId'):
                            df_updated.at[idx, 'corpus_id'] = result['corpusId']
                            updated = True
                    
                    # Fill s2_id if missing
                    if pd.isna(df_updated.at[idx, 's2_id']) or str(df_updated.at[idx, 's2_id']).strip() in ['', 'nan']:
                        if result.get('paperId'):
                            df_updated.at[idx, 's2_id'] = result['paperId']
                            updated = True
                    
                    # Fill DOI if missing
                    if pd.isna(df_updated.at[idx, 'DOI']) or str(df_updated.at[idx, 'DOI']).strip() in ['', 'nan']:
                        external_ids = result.get('externalIds', {})
                        if external_ids.get('DOI'):
                            df_updated.at[idx, 'DOI'] = external_ids['DOI']
                            updated = True
                    
                    if updated:
                        filled_count += 1
                        print(f"Row {idx}: Successfully filled missing values")
                    else:
                        print(f"Row {idx}: Found paper but no missing values to fill")
                else:
                    print(f"Row {idx}: No paper found")
                
                time.sleep(1)
                
            except Exception as e:
                error_count += 1
                print(f"Row {idx}: Error processing - {e}")
                continue
                
    except KeyboardInterrupt:
        print(f"\n\nKeyboard interrupt detected! Saving current progress...")
        print(f"Processed {filled_count} rows successfully before interruption")
        print(f"Encountered {error_count} errors before interruption")
        
        # Save the current progress
        try:
            save_updated_dataframe(df_updated, 'paper_info_updated.csv')
            print("Current progress saved to 'paper_info_updated.csv'")
        except Exception as save_error:
            print(f"Error saving interrupted progress: {save_error}")
        
        return df_updated
    
    print(f"\nFilling complete!")
    print(f"Successfully filled: {filled_count} rows")
    print(f"Errors encountered: {error_count} rows")
    
    return df_updated

def save_updated_dataframe(df, filename='paper_info_updated.csv'):
    """
    Save the updated DataFrame to a new CSV file
    
    Args:
        df (pd.DataFrame): DataFrame to save
        filename (str): Output filename
    """
    try:
        output_path = f'./data/{filename}'
        df.to_csv(output_path, index=False)
        print(f"Updated data saved to: {output_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    API_KEY = "39B73CXWua7xhzGlxFrNJ5wY6uIjXCna9sLxWL2w"
    
    # First, analyze the current state
    result = test_missing_values()
    
    if result[0] is not None and result[1] is not None:
        df, empty_mask = result
        
        # Ask user if they want to proceed with filling missing values
        print(f"\nFound {empty_mask.sum()} rows with missing values.")
        response = input("Do you want to attempt to fill missing values using Semantic Scholar API? (y/n): ")
        
        if response.lower() in ['y', 'yes']:
            # Fill missing values
            df_updated = fill_missing_values(df, empty_mask, API_KEY)
            
            # Show updated statistics
            print("\n" + "="*50)
            print("UPDATED STATISTICS:")
            print("="*50)
            
            # Recalculate missing values
            empty_mask_updated = (
                df_updated['corpus_id'].isna() | 
                (df_updated['corpus_id'].astype(str).str.strip() == '') |
                (df_updated['corpus_id'].astype(str).str.strip() == 'nan') |
                (df_updated['corpus_id'] == 0) |
                df_updated['s2_id'].isna() | 
                (df_updated['s2_id'].astype(str).str.strip() == '') |
                (df_updated['s2_id'].astype(str).str.strip() == 'nan') |
                df_updated['DOI'].isna() | 
                (df_updated['DOI'].astype(str).str.strip() == '') |
                (df_updated['DOI'].astype(str).str.strip() == 'nan')
            )
            
            rows_with_empty_values_updated = empty_mask_updated.sum()
            print(f"Rows with empty or None values after update: {rows_with_empty_values_updated}")
            print(f"Percentage of rows with missing values: {(rows_with_empty_values_updated / len(df_updated)) * 100:.2f}%")
            
            # Show breakdown by column
            print(f"\nBreakdown by column:")
            for col in ['corpus_id', 's2_id', 'DOI']:
                col_empty = (
                    df_updated[col].isna() | 
                    (df_updated[col].astype(str).str.strip() == '') |
                    (df_updated[col].astype(str).str.strip() == 'nan') |
                    (df_updated[col] == 0)
                ).sum()
                print(f"  {col}: {col_empty} empty values ({col_empty/len(df_updated)*100:.2f}%)")
            
            # Save updated data
            save_updated_dataframe(df_updated)
        else:
            print("Skipping missing value filling.")
    else:
        print("Could not load data. Exiting.")
