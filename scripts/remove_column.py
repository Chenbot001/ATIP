import pandas as pd
import os

# Configuration - Modify these values as needed
INPUT_CSV_FILEPATH = "data/authorships.csv"  # Path to your CSV file
COLUMN_TO_REMOVE = "citation_count"  # Name of the column to remove

def remove_column_from_csv(input_filepath, column_name):
    """
    Remove a specified column from a CSV file.
    
    Args:
        input_filepath (str): Path to the input CSV file
        column_name (str): Name of the column to remove
    """
    try:
        # Read the CSV file
        print(f"Reading CSV file: {input_filepath}")
        df = pd.read_csv(input_filepath)
        
        # Check if the column exists
        if column_name not in df.columns:
            print(f"Warning: '{column_name}' column not found in the CSV file.")
            print(f"Available columns: {list(df.columns)}")
            return
        
        # Remove the specified column
        print(f"Removing '{column_name}' column...")
        df = df.drop(columns=[column_name])
        
        # Save the modified dataframe back to the same file
        df.to_csv(input_filepath, index=False)
        print(f"Successfully removed '{column_name}' column from {input_filepath}")
        print(f"Remaining columns: {list(df.columns)}")
        
    except FileNotFoundError:
        print(f"Error: File '{input_filepath}' not found.")
    except Exception as e:
        print(f"Error processing file: {str(e)}")

def main():
    """Main function with hardcoded parameters."""
    # Validate file exists
    if not os.path.exists(INPUT_CSV_FILEPATH):
        print(f"Error: File '{INPUT_CSV_FILEPATH}' does not exist.")
        return
    
    # Validate it's a CSV file
    if not INPUT_CSV_FILEPATH.lower().endswith('.csv'):
        print(f"Error: File '{INPUT_CSV_FILEPATH}' is not a CSV file.")
        return
    
    # Remove the specified column
    remove_column_from_csv(INPUT_CSV_FILEPATH, COLUMN_TO_REMOVE)

if __name__ == "__main__":
    main()
