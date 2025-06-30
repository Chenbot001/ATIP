import pandas as pd
import sys
import argparse

def get_unique_venues(file_path):
    """
    Read a CSV file and return all unique values in the 'venue' column.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        list: List of unique venue values
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Check if 'venue' column exists
        if 'venue' not in df.columns:
            print(f"Error: 'venue' column not found in {file_path}")
            print(f"Available columns: {list(df.columns)}")
            return []
        
        # Get unique values from the venue column
        unique_venues = df['venue'].dropna().unique().tolist()
        
        return unique_venues
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def clean_venues_data(file_path):
    """
    Filter the CSV file to keep only rows with valid venues and save back to the file.
    
    Args:
        file_path (str): Path to the CSV file
    """
    # Define valid venues
    valid_venues = ['ACL', 'EMNLP', 'NAACL', 'Findings']
    
    try:
        # Read the CSV file
        print(f"Reading data from: {file_path}")
        df = pd.read_csv(file_path)
        
        # Check if 'venue' column exists
        if 'venue' not in df.columns:
            print(f"Error: 'venue' column not found in {file_path}")
            print(f"Available columns: {list(df.columns)}")
            return
        
        # Get initial count
        initial_count = len(df)
        print(f"Initial number of rows: {initial_count}")
        
        # Filter to keep only rows with valid venues
        df_cleaned = df[df['venue'].isin(valid_venues)]
        
        # Get final count
        final_count = len(df_cleaned)
        removed_count = initial_count - final_count
        
        print(f"Valid venues: {valid_venues}")
        print(f"Rows removed: {removed_count}")
        print(f"Rows remaining: {final_count}")
        
        # Save the cleaned data back to the same file
        df_cleaned.to_csv(file_path, index=False)
        print(f"Cleaned data saved back to: {file_path}")
        
        # Show unique venues in cleaned data
        venues_series = df_cleaned['venue']
        unique_venues_cleaned = sorted(venues_series.unique().tolist())  # type: ignore
        print(f"\nUnique venues in cleaned data: {unique_venues_cleaned}")
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error processing file: {e}")

def main():
    # Hardcoded file path - change this to your desired CSV file
    file_path = "C:/Users/ssr/EJC/ATIP/data/paper_info.csv"  # Example path, modify as needed
    
    # Clean the data by removing invalid venues
    clean_venues_data(file_path)

if __name__ == "__main__":
    main()
