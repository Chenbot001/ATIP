import warnings
from acl_anthology import Anthology
import pandas as pd
import os
import sys
from acl_anthology.people import Name
from tqdm import tqdm # Import tqdm

# Suppress the SchemaMismatchWarning
warnings.filterwarnings("ignore", category=UserWarning, module="acl_anthology.anthology")

# Configuration section - centralized file paths
CONFIG = {
    'data_dir': 'data',
    'paper_info_file': 'paper_info.csv',
    'author_profiles_file': 'author_data.csv',
    'authorships_file': 'authorships.csv'
}

def get_data_file_path(filename):
    """
    Helper function to get the full path to a data file.
    Tries the current directory first, then adjusts for script location.
    
    Args:
        filename (str): The name of the file in the data directory
        
    Returns:
        str: Full path to the file
        
    Raises:
        FileNotFoundError: If the file cannot be found
    """
    # Try current directory first
    file_path = os.path.join(CONFIG['data_dir'], filename)
    if os.path.exists(file_path):
        return file_path
    
    # Try relative to script location
    script_dir = os.path.dirname(__file__)
    adjusted_path = os.path.join(script_dir, CONFIG['data_dir'], filename)
    if os.path.exists(adjusted_path):
        return adjusted_path
    
    raise FileNotFoundError(f"{filename} not found at {file_path} or {adjusted_path}")

def get_acl_id_from_s2_id(s2_id):
    """
    Accepts an S2 ID (which is paper_id in authorships.csv) and returns the corresponding acl_id found in paper_info.csv.
    
    Args:
        s2_id (str): The S2 ID (corpus_id/paper_id) to look up.
        
    Returns:
        str: The corresponding acl_id if found, None otherwise.
    """
    try:
        paper_info_path = get_data_file_path(CONFIG['paper_info_file'])
        df = pd.read_csv(paper_info_path)
        
        matching_row = df[df['s2_id'].astype(str) == str(s2_id)]
        
        if matching_row.empty:
            return None
        
        return matching_row.iloc[0]['acl_id']
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None

def count_abbreviated_first_names():
    """
    Determines and shows the percentage of rows with abbreviated first names in researcher_profiles.csv.
    An abbreviated first name is defined as a single capital letter followed by a period (e.g., "J.").
    """
    try:
        authors_df_path = get_data_file_path(CONFIG['author_profiles_file'])
        authors_df = pd.read_csv(authors_df_path)
    except (FileNotFoundError, Exception) as e:
        print(f"Error reading {CONFIG['author_profiles_file']}: {e}")
        return 0

    total_authors = len(authors_df)
    
    # Filter for abbreviated names
    abbreviated_names_df = authors_df[
        authors_df['first_name'].apply(
            lambda x: isinstance(x, str) and len(x) == 2 and x[1] == '.' and x[0].isupper()
        )
    ]
    
    abbreviated_count = len(abbreviated_names_df)
    abbreviated_percentage = (abbreviated_count / total_authors) * 100 if total_authors > 0 else 0
    
    print(f"\nTotal authors in {CONFIG['author_profiles_file']}: {total_authors}")
    print(f"Authors with abbreviated first names: {abbreviated_count}")
    print(f"Percentage of abbreviated first names: {abbreviated_percentage:.2f}%")
    return abbreviated_percentage

def analyze_abbreviated_names_by_last_name():
    """
    Finds rows with abbreviated first names and identifies how many have the same last name.
    An abbreviated first name is defined as a single capital letter followed by a period (e.g., "J.").
    """
    try:
        authors_df_path = get_data_file_path(CONFIG['author_profiles_file'])
        authors_df = pd.read_csv(authors_df_path)
    except (FileNotFoundError, Exception) as e:
        print(f"Error reading {CONFIG['author_profiles_file']}: {e}")
        return

    # Filter for abbreviated names
    abbreviated_names_df = authors_df[
        authors_df['first_name'].apply(
            lambda x: isinstance(x, str) and len(x) == 2 and x[1] == '.' and x[0].isupper()
        )
    ].copy()
    
    if abbreviated_names_df.empty:
        print("\nNo abbreviated first names found.")
        return
    
    # Group by last name and count occurrences
    last_name_counts = abbreviated_names_df['last_name'].value_counts()
    
    print(f"\nAnalysis of abbreviated first names by last name:")
    print(f"Total authors with abbreviated first names: {len(abbreviated_names_df)}")
    print(f"Unique last names with abbreviated first names: {len(last_name_counts)}")
    
    # Show last names with multiple abbreviated entries
    multiple_abbrev = last_name_counts[last_name_counts > 1]
    if not multiple_abbrev.empty:
        print(f"\nLast names with multiple abbreviated first names:")
        for last_name in multiple_abbrev.index:
            print(f"\n{last_name}:")
            # Get all authors with this last name and abbreviated first names
            authors_with_last_name = abbreviated_names_df[abbreviated_names_df['last_name'] == last_name]
            for _, author_row in authors_with_last_name.iterrows():
                print(f"  {author_row['first_name']} {author_row['last_name']} (ID: {author_row['author_id']})")
        
        print(f"\nSummary:")
        print(f"  Last names with 1 abbreviated author: {len(last_name_counts[last_name_counts == 1])}")
        print(f"  Last names with 2+ abbreviated authors: {len(multiple_abbrev)}")
        print(f"  Total authors in last names with 2+ abbreviated authors: {multiple_abbrev.sum()}")
    else:
        print(f"\nAll abbreviated first names have unique last names.")
    
    return last_name_counts

def update_researcher_first_names():
    """
    Iterates through researcher_profiles.csv, identifies researchers with abbreviated first names (e.g., "J."),
    finds a corresponding paper, queries ACL Anthology for the full name, and updates the first name in the CSV.
    A tqdm progress bar is added for the processing of abbreviated names.
    Includes keyboard interrupt (Ctrl+C) handling to save progress.
    """
    try:
        authors_df_path = get_data_file_path(CONFIG['author_profiles_file'])
        authorships_path = get_data_file_path(CONFIG['authorships_file'])
        
        authors_df = pd.read_csv(authors_df_path)
        authorships_df = pd.read_csv(authorships_path)
    except (FileNotFoundError, Exception) as e:
        print(f"Error reading CSV files: {e}")
        return

    anthology = Anthology.from_repo()

    updated_count = 0
    
    # Filter for rows with abbreviated first names for processing
    abbrev_authors_df = authors_df[
        authors_df['first_name'].apply(
            lambda x: isinstance(x, str) and len(x) == 2 and x[1] == '.' and x[0].isupper()
        )
    ].copy() # Use .copy() to avoid SettingWithCopyWarning
    
    if abbrev_authors_df.empty:
        print("\nNo abbreviated first names found to process.")
        return

    print(f"\nStarting to process {len(abbrev_authors_df)} abbreviated first names...")

    try:
        # Iterate through the filtered DataFrame with tqdm
        for original_index, row_data in tqdm(abbrev_authors_df.iterrows(), total=len(abbrev_authors_df), desc="Updating Names"):
            first_name = row_data['first_name']
            author_id = row_data['author_id']
            last_name = row_data['last_name']

            # Find the first available paper_id corresponding to the author_id
            author_papers = authorships_df[authorships_df['author_id'] == author_id]
            if author_papers.empty:
                continue

            s2_id = author_papers.iloc[0]['paper_id']
            acl_id = get_acl_id_from_s2_id(s2_id)

            if acl_id:
                try:
                    paper = anthology.get(acl_id)
                    if paper and hasattr(paper, 'authors') and paper.authors:
                        full_name_found = False
                        for author in paper.authors:
                            if hasattr(author, 'name') and hasattr(author.name, 'last') and hasattr(author.name, 'first'):
                                if author.name.last == last_name and len(author.name.first) > 1 and author.name.first[0].isupper():
                                    # Update the original DataFrame directly using .loc with the original index
                                    authors_df.loc[original_index, 'first_name'] = author.name.first
                                    full_name_found = True
                                    updated_count += 1
                                    break
                except Exception as e:
                    # Suppress detailed print in loop to keep progress bar clean
                    pass # Continue processing
    except KeyboardInterrupt:
        print("\nProcess interrupted by user (Ctrl+C). Saving current progress...")
    
    # This block will execute whether the loop completes or is interrupted
    try:
        authors_df.to_csv(authors_df_path, index=False)
        print(f"\nUpdated {updated_count} author first names in {authors_df_path}")
    except Exception as e:
        print(f"Error saving updated CSV: {e}")

if __name__ == "__main__":
    # Create a dummy 'data' directory and empty CSV files for demonstration if they don't exist
    data_dir = CONFIG['data_dir']
    os.makedirs(data_dir, exist_ok=True)

    # Call the function to count abbreviated names
    count_abbreviated_first_names()
    
    # Call the function to analyze abbreviated names by last name
    analyze_abbreviated_names_by_last_name()
    
    # Then proceed with updating names, now with a progress bar and interrupt handling
    # update_researcher_first_names()