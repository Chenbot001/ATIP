import pandas as pd

def adjusted_citation_impact(author_identifier, df_researcher_citation_metrics, df_authorships, df_paper_info):
    """
    Calculates the adjusted citation impact for a given author.

    The adjusted citation impact is defined as the author's total citation count
    divided by the integer year of their first publication available in the dataset.

    Args:
        author_identifier (str or int): The full name (str) or researcher_id (int) of the author.
        df_researcher_citation_metrics (pd.DataFrame): DataFrame loaded from 'researcher_citation_metrics.csv'.
        df_authorships (pd.DataFrame): DataFrame loaded from 'authorships.csv'.
        df_paper_info (pd.DataFrame): DataFrame loaded from 'paper_info.csv'.

    Returns:
        float: The adjusted citation impact, or None if the author or their first publication
               information cannot be found.
    """

    # 1. Get the researcher_id if a full name is provided
    researcher_id = None
    if isinstance(author_identifier, str):
        # Assuming researcher_name in researcher_citation_metrics is 'full_name' for lookup
        author_row = df_researcher_citation_metrics[df_researcher_citation_metrics['researcher_name'] == author_identifier]
        if not author_row.empty:
            researcher_id = author_row['researcher_id'].iloc[0]
    elif isinstance(author_identifier, int):
        researcher_id = author_identifier
    else:
        print("Invalid author_identifier type. Must be a string (full name) or an integer (researcher_id).")
        return None

    if researcher_id is None:
        print(f"Author '{author_identifier}' not found in researcher citation metrics.")
        return None

    # 2. Get the author's total citation count (db_citation_count)
    citation_data = df_researcher_citation_metrics[df_researcher_citation_metrics['researcher_id'] == researcher_id]
    if citation_data.empty:
        print(f"No citation data found for researcher_id: {researcher_id}")
        return None
    total_citation_count = citation_data['db_citation_count'].iloc[0] [cite: 5]

    # 3. Find the author's first publication year
    # Get all paper_ids for the researcher
    author_papers = df_authorships[df_authorships['researcher_id'] == researcher_id] [cite: 1]
    if author_papers.empty:
        print(f"No papers found for researcher_id: {researcher_id}")
        return None

    # Get the paper_id from authorships to link with paper_info
    # Note: paper_id in authorships.csv is paper_id, in paper_info.csv it's corpus_id or acl_id,
    # assuming 'paper_id' from 'authorships.csv' maps to 'corpus_id' or 'acl_id' in 'paper_info.csv'
    # For now, let's assume 'paper_id' from authorships directly matches 'corpus_id' in paper_info.
    # If not, a mapping or join key clarification would be needed.
    
    # We will need to merge df_authorships with df_paper_info on a common paper identifier.
    # The 'authorships.csv' has 'paper_id'  and 'paper_info.csv' has 'corpus_id' and 'acl_id'.
    # Assuming 'paper_id' from 'authorships.csv' refers to 'corpus_id' from 'paper_info.csv' for joining.
    
    merged_papers = pd.merge(author_papers, df_paper_info, left_on='paper_id', right_on='corpus_id', how='inner') [cite: 1, 4]

    if merged_papers.empty:
        print(f"No matching paper information found for researcher_id: {researcher_id}")
        return None

    # Find the minimum year
    first_publication_year = merged_papers['year'].min() [cite: 4]

    if pd.isna(first_publication_year):
        print(f"Could not determine first publication year for researcher_id: {researcher_id}")
        return None

    # 4. Calculate adjusted citation impact
    if first_publication_year == 0: # Avoid division by zero if year is somehow 0
        print(f"First publication year for researcher_id {researcher_id} is 0, cannot calculate impact.")
        return None

    adjusted_impact = float(total_citation_count) / int(first_publication_year)

    return adjusted_impact