import pandas as pd
import numpy as np

def get_author_id_from_name(full_name: str, df_author_profiles: pd.DataFrame) -> list:
    """
    Helper function to find author_id from full name using author_profiles.csv
    
    Args:
        full_name (str): The full name of the author (e.g., "John Doe")
        df_author_profiles (pd.DataFrame): DataFrame loaded from 'author_profiles.csv'
    
    Returns:
        list: List of author_ids if found, empty list otherwise
    """
    # Try exact match first
    author_row = df_author_profiles[
        (df_author_profiles['first_name'] + ' ' + df_author_profiles['last_name']) == full_name
    ]
    
    if not author_row.empty:
        author_ids = author_row['author_id'].tolist()
        if len(author_ids) > 1:
            print(f"Multiple authors found with name '{full_name}':")
            for author_id in author_ids:
                print(f"  Author ID: {author_id}")
        return author_ids
    
    # Try case-insensitive match
    author_row = df_author_profiles[
        (df_author_profiles['first_name'] + ' ' + df_author_profiles['last_name']).str.lower() == full_name.lower()
    ]
    
    if not author_row.empty:
        author_ids = author_row['author_id'].tolist()
        if len(author_ids) > 1:
            print(f"Multiple authors found with name '{full_name}' (case-insensitive):")
            for author_id in author_ids:
                print(f"  Author ID: {author_id}")
        return author_ids
    
    print(f"Author '{full_name}' not found in author profiles.")
    return []

def calculate_anci_frac(author_id: int,
                        paper_info_df: pd.DataFrame,
                        authorships_df: pd.DataFrame) -> tuple[float, int]:
    """
    Calculates the co-authorship fractionalized ANCI metric using the 'authorships' table.

    This metric is C_frac / (Y^0.5), where C_frac is the sum of fractionalized
    citations, and Y is the author's career length. It uses 's2_id' as the
    common paper identifier.

    Args:
        author_id: The unique identifier for the author.
        paper_info_df: DataFrame from 'paper_info.csv'. Must contain 's2_id',
                       'year', and 'citation_count' columns.
        authorships_df: DataFrame from 'authorships.csv'. Must contain 'author_id'
                        and 'paper_id' (representing s2_id) columns.

    Returns:
        The calculated ANCI_frac metric. Returns 0.0 if the author has no
        publications or a career of zero length.
    """
    # Note: The 'authorships.csv' file uses 'paper_id' which corresponds to 's2_id'.
    # For clarity, we will rename it to 's2_id'.
    authorships_df = authorships_df.rename(columns={'paper_id': 's2_id'})

    # Find all s2_ids for the given author_id
    author_s2_ids = authorships_df[authorships_df['author_id'] == author_id]['s2_id'].unique()

    if len(author_s2_ids) == 0:
        return 0.0

    # Filter paper_info to only the author's papers using the list of s2_ids
    papers_details = paper_info_df[paper_info_df['s2_id'].isin(author_s2_ids)].copy()
    paper_count = len(papers_details)
    print(f"Publications by target author found: {paper_count}")

    if papers_details.empty:
        return 0.0

    # --- 1. Calculate Career Length (Y) ---
    first_pub_year = papers_details['year'].min()
    current_year = 2025 # Based on context
    career_length = current_year - first_pub_year + 1

    if career_length <= 0:
        return 0.0

    # --- 2. Calculate Fractionalized Citation Sum (C_frac) ---

    # Pre-calculate the number of authors for each paper using the s2_id
    author_counts = authorships_df.groupby('s2_id')['author_id'].nunique()
    
    # Map the author counts to the details of the author's papers
    papers_details['num_authors'] = papers_details['s2_id'].map(author_counts)

    # Clean up data - drop papers without author counts and where author count is zero
    papers_details.dropna(subset=['num_authors'], inplace=True)
    papers_details = papers_details[papers_details['num_authors'] > 0]

    # Calculate fractionalized citation for each paper (c_i / a_i)
    papers_details['frac_citation'] = papers_details['citation_count'] / papers_details['num_authors']
    
    c_frac = papers_details['frac_citation'].sum()

    # --- 3. Calculate Final ANCI_frac Metric ---
    anci_frac = c_frac / np.sqrt(career_length)

    return anci_frac, career_length, paper_count

# --- Example Usage ---
if __name__ == '__main__':
    paper_info_df = pd.read_csv('data/paper_info.csv')
    authorships_df = pd.read_csv('data/authorships.csv')
    author_profiles_df = pd.read_csv('data/author_profiles.csv')

    target_author = "Eric Xing"
    target_author_ids = get_author_id_from_name(target_author, author_profiles_df)
    
    if not target_author_ids:
        print(f"No authors found with name '{target_author}'")
        exit()
    
    print(f"Authors {target_author} found with IDs: {target_author_ids}")
    
    # If multiple authors found, calculate ANCI for each
    if len(target_author_ids) > 1:
        print(f"\nCalculating ANCI metrics for all {len(target_author_ids)} authors:")
        for i, author_id in enumerate(target_author_ids, 1):
            anci_metric, career_length, paper_count = calculate_anci_frac(author_id, paper_info_df, authorships_df)
            print(f"{i}. Author ID {author_id}: ANCI_frac = {anci_metric:.4f}, Paper Count = {paper_count}, Career Length = {career_length} years")

            print()
    else:
        # Single author found
        anci_metric, career_length, paper_count = calculate_anci_frac(target_author_ids[0], paper_info_df, authorships_df)
        print(f"Career Length = {career_length} years")
        print(f"Paper Count = {paper_count}")
        print(f"The ANCI_frac for author {target_author} is: {anci_metric:.4f}")
        print()
