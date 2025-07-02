import warnings
from acl_anthology import Anthology
import pandas as pd
import os
import sys
from acl_anthology.people import Name

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
    
    df = pd.read_csv(paper_info_path) # [cite: 5]
    
    matching_row = df[df['s2_id'].astype(str) == str(s2_id)] # [cite: 5]
    
    if matching_row.empty:
        return None
    
    return matching_row.iloc[0]['acl_id'] # [cite: 5]

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
            return
        else:
            researcher_profiles_path = adjusted_path

    try:
        researcher_profiles_df = pd.read_csv(researcher_profiles_path) # 
    except Exception as e:
        print(f"Error reading researcher_profiles.csv: {e}")
        return

    abbreviated_count = 0
    for index, row in researcher_profiles_df.iterrows():
        first_name = row['first_name'] # 
        # Check for abbreviated first name (one capital letter followed by '.')
        if isinstance(first_name, str) and len(first_name) == 2 and first_name[1] == '.' and first_name[0].isupper():
            abbreviated_count += 1
    
    print(f"\nTotal rows with abbreviated first names in researcher_profiles.csv: {abbreviated_count}")


def update_researcher_first_names():
    """
    Iterates through researcher_profiles.csv, identifies researchers with abbreviated first names (e.g., "J."),
    finds a corresponding paper, queries ACL Anthology for the full name, and updates the first name in the CSV.
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
        researcher_profiles_df = pd.read_csv(researcher_profiles_path) # 
        authorships_df = pd.read_csv(authorships_path) # [cite: 3]
    except Exception as e:
        print(f"Error reading CSV files: {e}")
        return

    anthology = Anthology.from_repo()

    updated_count = 0
    
    # Iterate through researcher_profiles.csv
    for index, row in researcher_profiles_df.iterrows():
        first_name = row['first_name'] # 
        researcher_id = row['researcher_id'] # 
        last_name = row['last_name'] # 

        # Check for abbreviated first name (one capital letter followed by '.')
        if isinstance(first_name, str) and len(first_name) == 2 and first_name[1] == '.' and first_name[0].isupper():
            print(f"Processing abbreviated name: {first_name} {last_name} (ID: {researcher_id})")

            # Find the first available paper_id corresponding to the researcher_id
            author_papers = authorships_df[authorships_df['researcher_id'] == researcher_id] # [cite: 3]
            if author_papers.empty:
                print(f"  No papers found for researcher ID {researcher_id}. Skipping.")
                continue

            # Get the first paper_id (which is s2_id)
            s2_id = author_papers.iloc[0]['paper_id'] # [cite: 3]
            
            # Use paper_info.csv to find the acl_id using this paper_id (s2_id)
            acl_id = get_acl_id_from_s2_id(s2_id)

            if acl_id:
                try:
                    paper = anthology.get(acl_id)
                    if paper and hasattr(paper, 'authors') and paper.authors:
                        full_name_found = False
                        for author in paper.authors:
                            if hasattr(author, 'name') and hasattr(author.name, 'last') and hasattr(author.name, 'first'):
                                if author.name.last == last_name and len(author.name.first) > 1 and author.name.first[0].isupper():
                                    # Match by last name and ensure the first name is not abbreviated itself
                                    print(f"  Found full name for {first_name} {last_name}: {author.name.first} {author.name.last}")
                                    researcher_profiles_df.at[index, 'first_name'] = author.name.first # 
                                    full_name_found = True
                                    updated_count += 1
                                    break
                        if not full_name_found:
                            print(f"  Could not find a matching full first name in ACL Anthology for {first_name} {last_name} (Paper ID: {s2_id}).")
                    else:
                        print(f"  Paper {acl_id} not found in ACL Anthology or has no authors.")
                except Exception as e:
                    print(f"  Error accessing ACL Anthology for ACL ID {acl_id}: {e}")
            else:
                print(f"  ACL ID not found for S2 ID {s2_id}.")
        elif not isinstance(first_name, str):
            print(f"Skipping non-string first name: {first_name} (ID: {researcher_id})")

    # Save the updated DataFrame back to CSV
    try:
        researcher_profiles_df.to_csv(researcher_profiles_path, index=False)
        print(f"\nUpdated {updated_count} researcher first names in {researcher_profiles_path}")
    except Exception as e:
        print(f"Error saving updated CSV: {e}")

if __name__ == "__main__":
    # Create a dummy 'data' directory and empty CSV files for demonstration if they don't exist
    # In a real scenario, you would have your actual data here.
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)

    # Call the new function to count abbreviated names
    count_abbreviated_first_names()
    
    # Then proceed with updating names
    update_researcher_first_names()