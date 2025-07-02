# ATIP_metrics.py
import pandas as pd
import numpy as np
import datetime
import json # To parse the 'citations_by_year' string

def adjusted_citation_impact(author_identifier, df_researcher_citation_metrics, df_authorships, df_paper_info):
    """
    Calculates the adjusted citation impact for a given author.

    The adjusted citation impact is defined as the author's total citation count
    divided by the square root of the integer years passed since the author's
    earliest publication available in the dataset.

    Args:
        author_identifier (str or int): The full name (str) or researcher_id (int) of the author.
        df_researcher_citation_metrics (pd.DataFrame): DataFrame loaded from 'researcher_citation_metrics.csv'.
        df_authorships (pd.DataFrame): DataFrame loaded from 'authorships.csv'.
        df_paper_info (pd.DataFrame): DataFrame loaded from 'paper_info.csv'.

    Returns:
        tuple: A tuple containing (adjusted_impact, total_citation_count, first_publication_year).
               Returns (None, None, None) if the author or their first publication
               information cannot be found or calculation is not possible.
    """

    # 1. Get the researcher_id if a full name is provided
    researcher_id = None
    if isinstance(author_identifier, str):
        author_row = df_researcher_citation_metrics[df_researcher_citation_metrics['researcher_name'] == author_identifier]
        if not author_row.empty:
            researcher_id = author_row['researcher_id'].iloc[0]
    elif isinstance(author_identifier, int):
        researcher_id = author_identifier
    else:
        print("Invalid author_identifier type. Must be a string (full name) or an integer (researcher_id).")
        return None, None, None

    if researcher_id is None:
        print(f"Author '{author_identifier}' not found in researcher citation metrics.")
        return None, None, None

    # 2. Get the author's total citation count (db_citation_count)
    citation_data = df_researcher_citation_metrics[df_researcher_citation_metrics['researcher_id'] == researcher_id]
    if citation_data.empty:
        print(f"No citation data found for researcher_id: {researcher_id}")
        return None, None, None
    total_citation_count = citation_data['db_citation_count'].iloc[0]

    # 3. Find the author's first publication year
    author_papers = df_authorships[df_authorships['researcher_id'] == researcher_id]
    if author_papers.empty:
        print(f"No papers found for researcher_id: {researcher_id}")
        return None, None, None

    # Correctly merge df_authorships with df_paper_info using 's2_id' [cite: 1, 3, 5]
    merged_papers = pd.merge(author_papers, df_paper_info, left_on='paper_id', right_on='s2_id', how='inner')

    if merged_papers.empty:
        print(f"No matching paper information found for researcher_id: {researcher_id}")
        return None, None, None

    first_publication_year = merged_papers['year'].min()

    if hasattr(first_publication_year, 'item'):
        first_publication_year = first_publication_year.item()

    if first_publication_year is None or (isinstance(first_publication_year, (int, float)) and pd.isna(first_publication_year)):
        print(f"Could not determine first publication year for researcher_id: {researcher_id}")
        return None, None, None

    # 4. Calculate adjusted citation impact with the new formula
    # Using 2025 as the current year, as per the context provided.
    current_year = 2025

    years_passed = current_year - int(first_publication_year)

    if years_passed <= 0: # Handle cases where first publication year is current or future
        print(f"Years passed for researcher_id {researcher_id} is non-positive ({years_passed}), cannot calculate impact.")
        return None, None, None

    adjusted_impact = float(total_citation_count) / np.sqrt(years_passed)

    return adjusted_impact, total_citation_count, int(first_publication_year)


def citation_accel(researcher_id, df_researcher_citation_metrics):
    """
    Gauges an author's citation acceleration across their years of publication.
    Formula: Citations(Last 2yr) / Citations(Previous 2yr)

    Args:
        researcher_id (int): The researcher_id of the author.
        df_researcher_citation_metrics (pd.DataFrame): DataFrame loaded from 'researcher_citation_metrics.csv'.

    Returns:
        float or str: The citation acceleration score, np.inf for infinite acceleration,
                      or a string message if calculation is not possible.
    """
    author_row = df_researcher_citation_metrics[df_researcher_citation_metrics['researcher_id'] == researcher_id]
    if author_row.empty:
        return "Author not found in researcher citation metrics."

    citations_by_year_str = author_row['citations_by_year'].iloc[0]

    # Parse the string representation of dictionary into an actual dictionary
    # Handle potential issues with single quotes vs double quotes if needed, though json.loads is usually strict.
    try:
        # Replace single quotes with double quotes for valid JSON, if necessary
        citations_by_year_dict = json.loads(citations_by_year_str.replace("'", "\""))
    except json.JSONDecodeError:
        print(f"Error parsing citations_by_year for researcher_id {researcher_id}: {citations_by_year_str}")
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


if __name__ == "__main__":
    
    # Load dataframes (assuming the files are in the same directory as the script)
    researcher_citation_metrics_df = pd.read_csv('./data/researcher_citation_metrics.csv')
    authorships_df = pd.read_csv('./data/authorships.csv')
    paper_info_df = pd.read_csv('./data/paper_info.csv')


    # Example Usage for citation_accel
    author_id_accel = 100516590 # Use the same or a different researcher_id
    accel_score = citation_accel(author_id_accel, researcher_citation_metrics_df)
    
    # Get the author's full name for Citation Acceleration
    author_name_row_accel = researcher_citation_metrics_df[researcher_citation_metrics_df['researcher_id'] == author_id_accel]
    author_full_name_accel = author_name_row_accel['researcher_name'].iloc[0] if not author_name_row_accel.empty else "Unknown Author"

    print(f"\n--- Citation Acceleration ---")
    print(f"Citation Acceleration for {author_full_name_accel} (ID {author_id_accel}): {accel_score}")
    print("-" * 30)