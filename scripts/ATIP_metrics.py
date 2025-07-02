# ATIP_metrics.py
import pandas as pd
import numpy as np
import datetime
import json # To parse the 'citations_by_year' string
import ast # To safely parse Python dictionary strings

def get_author_id_from_name(full_name: str, df_author_profiles: pd.DataFrame) -> int | None:
    """
    Helper function to find author_id from full name using author_profiles.csv
    
    Args:
        full_name (str): The full name of the author (e.g., "John Doe")
        df_author_profiles (pd.DataFrame): DataFrame loaded from 'author_profiles.csv'
    
    Returns:
        int or None: The author_id if found, None otherwise
    """
    # Try exact match first
    author_row = df_author_profiles[
        (df_author_profiles['first_name'] + ' ' + df_author_profiles['last_name']) == full_name
    ]
    
    if not author_row.empty:
        return int(author_row['author_id'].item())
    
    # Try case-insensitive match
    author_row = df_author_profiles[
        (df_author_profiles['first_name'] + ' ' + df_author_profiles['last_name']).str.lower() == full_name.lower()
    ]
    
    if not author_row.empty:
        return int(author_row['author_id'].item())
    
    print(f"Author '{full_name}' not found in author profiles.")
    return None

def adjusted_citation_impact(author_id: int, df_author_citation_metrics: pd.DataFrame, df_authorships: pd.DataFrame, df_paper_info: pd.DataFrame):
    """
    Calculates the adjusted citation impact for a given author.

    The adjusted citation impact is defined as the author's total citation count
    divided by the square root of the integer years passed since the author's
    earliest publication available in the dataset.

    Args:
        author_id (int): The author_id of the author.
        df_author_citation_metrics (pd.DataFrame): DataFrame loaded from 'author_citation_metrics.csv'.
        df_authorships (pd.DataFrame): DataFrame loaded from 'authorships.csv'.
        df_paper_info (pd.DataFrame): DataFrame loaded from 'paper_info.csv'.

    Returns:
        tuple: A tuple containing (adjusted_impact, total_citation_count, first_publication_year).
               Returns (None, None, None) if the author or their first publication
               information cannot be found or calculation is not possible.
    """

    # 1. Get the author's total citation count (db_citation_count)
    citation_data = df_author_citation_metrics[df_author_citation_metrics['author_id'] == author_id]
    if citation_data.empty:
        print(f"No citation data found for author_id: {author_id}")
        return None, None, None
    total_citation_count = citation_data['db_citation_count'].values[0]

    # 2. Find the author's first publication year
    author_papers = df_authorships[df_authorships['author_id'] == author_id]
    if author_papers.empty:
        print(f"No papers found for author_id: {author_id}")
        return None, None, None

    # Correctly merge df_authorships with df_paper_info using 's2_id'
    merged_papers = pd.merge(author_papers, df_paper_info, left_on='paper_id', right_on='s2_id', how='inner')

    if merged_papers.empty:
        print(f"No matching paper information found for author_id: {author_id}")
        return None, None, None

    first_publication_year = merged_papers['year'].min()

    if hasattr(first_publication_year, 'item'):
        first_publication_year = first_publication_year.item()

    if first_publication_year is None or (isinstance(first_publication_year, (int, float)) and pd.isna(first_publication_year)):
        print(f"Could not determine first publication year for author_id: {author_id}")
        return None, None, None

    # 3. Calculate adjusted citation impact with the new formula
    # Using 2025 as the current year, as per the context provided.
    current_year = 2025

    years_passed = current_year - int(first_publication_year)

    if years_passed <= 0: # Handle cases where first publication year is current or future
        print(f"Years passed for author_id {author_id} is non-positive ({years_passed}), cannot calculate impact.")
        return None, None, None

    adjusted_impact = float(total_citation_count) / np.sqrt(years_passed)

    return adjusted_impact, total_citation_count, int(first_publication_year)

def citation_accel(author_id: int, df_author_citation_metrics: pd.DataFrame):
    """
    Gauges an author's citation acceleration across their years of publication.
    Formula: Citations(Last 2yr) / Citations(Previous 2yr)

    Args:
        author_id (int): The author_id of the author.
        df_author_citation_metrics (pd.DataFrame): DataFrame loaded from 'author_citation_metrics.csv'.

    Returns:
        float or str: The citation acceleration score, np.inf for infinite acceleration,
                      or a string message if calculation is not possible.
    """
    author_row = df_author_citation_metrics[df_author_citation_metrics['author_id'] == author_id]
    if author_row.empty:
        return "Author not found in author citation metrics."

    citations_by_year_str = author_row['citations_by_year'].values[0]

    # Parse the string representation of dictionary into an actual dictionary
    # Use ast.literal_eval for safer parsing of Python dictionary strings
    try:
        citations_by_year_dict = ast.literal_eval(citations_by_year_str)
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing citations_by_year for author_id {author_id}: {citations_by_year_str}")
        print(f"Parse error: {e}")
        return "Error parsing citation data."

    # Convert keys from string to int (years) and ensure values are integers
    citations_by_year_dict = {int(k): int(v) for k, v in citations_by_year_dict.items()}

    # Determine relevant years based on current year (2025)
    current_year = 2025
    
    # Define the periods
    last_2_years_period = [current_year - 1, current_year - 2] # [2024, 2023]
    previous_2_years_period = [current_year - 3, current_year - 4] # [2022, 2021]

    # Find the earliest and latest year of actual citations for the author
    if not citations_by_year_dict:
        return "insufficient publication history to calculate citation acceleration."
    
    # Get all years for which the author has citations, sorted
    available_years = sorted(citations_by_year_dict.keys())
    
    if len(available_years) < 2:
        return "insufficient publication history to calculate citation acceleration."

    # Determine the span of the author's publication history.
    # We need at least 4 years of history to define distinct 'Last 2yr' and 'Previous 2yr' periods.
    # The 'Previous 2yr' period (2021-2022) must be covered.
    # Check if the earliest available year is at or before the start of the 'previous_2_years_period' (i.e., 2021)
    if min(available_years) > min(previous_2_years_period):
        return "insufficient publication history to calculate citation acceleration."
        
    # Sum citations for each period
    citations_last_2yr = sum(citations_by_year_dict.get(year, 0) for year in last_2_years_period)
    citations_previous_2yr = sum(citations_by_year_dict.get(year, 0) for year in previous_2_years_period)

    # Handle edge cases for calculation
    if citations_previous_2yr == 0:
        if citations_last_2yr > 0:
            return np.inf  # Infinite acceleration if previous period had no citations but recent does
        else:
            return 0.0 # No acceleration if both periods have no citations (no meaningful change)
    
    return float(citations_last_2yr) / citations_previous_2yr

def first_author_dominance(author_id: int, df_author_citation_metrics: pd.DataFrame, df_authorships: pd.DataFrame, df_paper_info: pd.DataFrame) -> float | None:
    """
    Calculates the first author dominance for a given author.

    First author dominance is defined as the cumulative citation count from papers
    where the author is flagged as the first author, divided by the author's
    total citation count (db_citation_count).

    Args:
        author_id (int): The author_id of the author.
        df_author_citation_metrics (pd.DataFrame): DataFrame loaded from 'author_citation_metrics.csv'.
        df_authorships (pd.DataFrame): DataFrame loaded from 'authorships.csv'.
        df_paper_info (pd.DataFrame): DataFrame loaded from 'paper_info.csv'.

    Returns:
        float or None: The first author dominance score, or None if calculation is not possible.
    """
    # 1. Get the author's total citation count from author_citation_metrics.csv
    total_citation_data = df_author_citation_metrics[df_author_citation_metrics['author_id'] == author_id]
    if total_citation_data.empty:
        print(f"No citation data found for author_id: {author_id} in author_citation_metrics.csv")
        return None
    total_citation_count = total_citation_data['db_citation_count'].values[0]

    if total_citation_count == 0:
        return 0.0 # If total citations are 0, dominance is 0

    # 2. Get papers where the author is the first author from authorships.csv
    first_author_papers = df_authorships[
        (df_authorships['author_id'] == author_id) & (df_authorships['is_first_author'] == True)
    ]

    if first_author_papers.empty:
        return 0.0 # If no papers where they are first author, dominance is 0

    # 3. Get citation counts for these papers from paper_info.csv
    # Merge first_author_papers with paper_info to get citation counts
    # Use 'paper_id' from authorships and 's2_id' from paper_info for merging
    merged_first_author_paper_info = pd.merge(
        first_author_papers,
        df_paper_info[['s2_id', 'citation_count']],
        left_on='paper_id',
        right_on='s2_id',
        how='inner'
    )

    if merged_first_author_paper_info.empty:
        print(f"No matching paper info found for first-authored papers by author_id: {author_id}")
        return 0.0 # No citation data for first-authored papers found

    cumulative_first_author_citations = merged_first_author_paper_info['citation_count'].sum()

    # 4. Calculate first author dominance
    dominance_score = float(cumulative_first_author_citations) / total_citation_count

    return dominance_score

if __name__ == "__main__":
    
    # Load dataframes (assuming the files are in the same directory as the script)
    author_citation_metrics_df = pd.read_csv('./data/author_citation_metrics.csv')
    authorships_df = pd.read_csv('./data/authorships.csv')
    paper_info_df = pd.read_csv('./data/paper_info.csv')
    author_profiles_df = pd.read_csv('./data/author_profiles.csv')

    # Example Usage for citation_accel
    author_id = 100466830 # Use the same or a different author_id
    aci_score, citation_count, first_publication_year = adjusted_citation_impact(author_id, author_citation_metrics_df, authorships_df, paper_info_df)
    accel_score = citation_accel(author_id, author_citation_metrics_df)
    first_author_dom_score = first_author_dominance(author_id, author_citation_metrics_df, authorships_df, paper_info_df)

    print(f"\n--- Adjusted Citation Impact ---")
    print(f"Adjusted Citation Impact Score for ID {author_id}: {aci_score}")
    print(f"Total Citation Count for ID {author_id}: {citation_count}")
    print(f"First Publication Year for ID {author_id}: {first_publication_year}")
    print(f"\n--- Citation Acceleration ---")
    print(f"Citation Acceleration for ID {author_id}: {accel_score}")
    print(f"\n--- First Author Dominance ---")
    print(f"First Author Dominance for ID {author_id}: {first_author_dom_score}")
    print("-" * 30)
