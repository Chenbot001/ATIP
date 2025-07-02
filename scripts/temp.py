import warnings
from acl_anthology import Anthology
import pandas as pd
import os
import sys
from acl_anthology.people import Name
from tqdm import tqdm # Import tqdm

# Suppress the SchemaMismatchWarning
warnings.filterwarnings("ignore", category=UserWarning, module="acl_anthology.anthology")

def get_acl_id_from_s2_id(s2_id):
    """
    Accepts an S2 ID (which is paper_id in authorships.csv) and returns the corresponding acl_id found in paper_info.csv.
    
    Args:
        s2_id (str): The S2 ID (corpus_id/paper_id) to look up.
        
    Returns:
        str: The corresponding acl_id if found, None otherwise.
    """
    paper_info_path = os.path.join('data', 'paper_info.csv')
    
    if not os.path.exists(paper_info_path):
        # Assuming 'data' directory is at the same level as the script, adjust if necessary
        paper_info_path = os.path.join(os.path.dirname(__file__), 'data', 'paper_info.csv')
        if not os.path.exists(paper_info_path):
            raise FileNotFoundError(f"paper_info.csv not found at {paper_info_path}")
    
    df = pd.read_csv(paper_info_path)
    
    matching_row = df[df['s2_id'].astype(str) == str(s2_id)]
    
    if matching_row.empty:
        return None
    
    return matching_row.iloc[0]['acl_id']

def count_abbreviated_first_names():
    """
    Determines and shows how many rows with abbreviated first names are in researcher_profiles.csv.
    An abbreviated first name is defined as a single capital letter followed by a period (e.g., "J.").
    """
    researcher_profiles_path = os.path.join('data', 'researcher_profiles.csv')

    if not os.path.exists(researcher_profiles_path):
        adjusted_path = os.path.join(os.path.dirname(__file__), 'data', 'researcher_profiles.csv')
        if not os.path.exists(adjusted_path):
            print(f"Error: researcher_profiles.csv not found at {researcher_profiles_path} or {adjusted_path}")
            return 0 # Return 0 if file not found
        else:
            researcher_profiles_path = adjusted_path

    try:
        researcher_profiles_df = pd.read_csv(researcher_profiles_path)
    except Exception as e:
        print(f"Error reading researcher_profiles.csv: {e}")
        return 0 # Return 0 if error reading

    # Filter for abbreviated names
    abbreviated_names_df = researcher_profiles_df[
        researcher_profiles_df['first_name'].apply(
            lambda x: isinstance(x, str) and len(x) == 2 and x[1] == '.' and x[0].isupper()
        )
    ]
    
    abbreviated_count = len(abbreviated_names_df)
    
    print(f"\nTotal rows with abbreviated first names in researcher_profiles.csv: {abbreviated_count}")
    return abbreviated_count # Return the count


def update_researcher_first_names():
    """
    Iterates through researcher_profiles.csv, identifies researchers with abbreviated first names (e.g., "J."),
    finds a corresponding paper, queries ACL Anthology for the full name, and updates the first name in the CSV.
    A tqdm progress bar is added for the processing of abbreviated names.
    Includes keyboard interrupt (Ctrl+C) handling to save progress.
    """
    researcher_profiles_path = os.path.join('data', 'researcher_profiles.csv')
    authorships_path = os.path.join('data', 'authorships.csv')

    # Ensure files exist
    for path in [researcher_profiles_path, authorships_path]:
        if not os.path.exists(path):
            # Adjust path if 'data' is a sibling directory to where the script is run
            adjusted_path = os.path.join(os.path.dirname(__file__), 'data', os.path.basename(path))
            if not os.path.exists(adjusted_path):
                raise FileNotFoundError(f"{os.path.basename(path)} not found at {path} or {adjusted_path}")
            else:
                if path == researcher_profiles_path:
                    researcher_profiles_path = adjusted_path
                elif path == authorships_path:
                    authorships_path = adjusted_path

    try:
        researcher_profiles_df = pd.read_csv(researcher_profiles_path)
        authorships_df = pd.read_csv(authorships_path)
    except Exception as e:
        print(f"Error reading CSV files: {e}")
        return

    anthology = Anthology.from_repo()

    updated_count = 0
    
    # Filter for rows with abbreviated first names for processing
    abbreviated_researchers_df = researcher_profiles_df[
        researcher_profiles_df['first_name'].apply(
            lambda x: isinstance(x, str) and len(x) == 2 and x[1] == '.' and x[0].isupper()
        )
    ].copy() # Use .copy() to avoid SettingWithCopyWarning
    
    if abbreviated_researchers_df.empty:
        print("\nNo abbreviated first names found to process.")
        return

    print(f"\nStarting to process {len(abbreviated_researchers_df)} abbreviated first names...")

    try:
        # Iterate through the filtered DataFrame with tqdm
        for original_index, row_data in tqdm(abbreviated_researchers_df.iterrows(), total=len(abbreviated_researchers_df), desc="Updating Names"):
            first_name = row_data['first_name']
            researcher_id = row_data['researcher_id']
            last_name = row_data['last_name']

            # Find the first available paper_id corresponding to the researcher_id
            author_papers = authorships_df[authorships_df['researcher_id'] == researcher_id]
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
                                    researcher_profiles_df.loc[original_index, 'first_name'] = author.name.first
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
        researcher_profiles_df.to_csv(researcher_profiles_path, index=False)
        print(f"\nUpdated {updated_count} researcher first names in {researcher_profiles_path}")
    except Exception as e:
        print(f"Error saving updated CSV: {e}")

if __name__ == "__main__":
    # Create a dummy 'data' directory and empty CSV files for demonstration if they don't exist
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)

    # Call the function to count abbreviated names
    count_abbreviated_first_names()
    
    # Then proceed with updating names, now with a progress bar and interrupt handling
    update_researcher_first_names()