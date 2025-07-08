import pandas as pd
import numpy as np

def get_author_papers(author_id: int, 
                      authorships_df: pd.DataFrame, 
                      paper_info_df: pd.DataFrame) -> pd.DataFrame:
    """
    Retrieves a DataFrame of all papers published by a given author.

    Args:
        author_id (int): The unique identifier for the author.
        authorships_df (pd.DataFrame): Data from authorships.csv.
        paper_info_df (pd.DataFrame): Data from paper_info.csv.

    Returns:
        pd.DataFrame: A DataFrame containing the details of the author's papers.
    """
    # Ensure paper_id columns are named consistently for merging
    if 'paper_id' in authorships_df.columns:
        authorships_df = authorships_df.rename(columns={'paper_id': 's2_id'})
    
    author_s2_ids = authorships_df[authorships_df['author_id'] == author_id]['s2_id'].unique()
    if len(author_s2_ids) == 0:
        return pd.DataFrame() # Return empty DataFrame if no papers
    
    return paper_info_df[paper_info_df['s2_id'].isin(author_s2_ids)].copy()

def calculate_rq_venue(author_papers_df: pd.DataFrame) -> float:
    """
    Calculates the Venue-Weighted Score (RQ_venue). 

    This score is the sum of tier-based scores for each paper. [cite: 57]
    Tier scores: A=4, B=3, C=2, D=1. [cite: 58]

    Args:
        author_papers_df (pd.DataFrame): A DataFrame of an author's papers.

    Returns:
        float: The author's RQ_venue score.
    """
    if author_papers_df.empty:
        return 0.0

    # Define tier scores
    TIER_SCORES = {'A': 4, 'B': 3, 'C': 2, 'D': 1}
    
    def get_tier(row):
        track = row.get('track', '')
        # Handle NaN values and convert to string
        if pd.isna(track) or track == '':
            return 'D'  # Default to tier D for unknown tracks
        track = str(track).lower()
        
        # Tier A for long papers at main conferences
        if 'long papers' in track:
            return 'A'
        # Tier B for short papers or findings
        if 'short papers' in track or 'findings' in track:
            return 'B'
        # Tier C for demos and student workshops
        if 'demonstrations' in track or 'student research workshop' in track or 'industry' in track:
            return 'C'
        # Tier D for workshops as a default
        if 'workshop' in track:
            return 'D'
        return 'D'  # Default to tier D if no category matches

    # Apply the tiering logic and then map to scores
    author_papers_df['tier'] = author_papers_df.apply(get_tier, axis=1)
    author_papers_df['venue_score'] = author_papers_df['tier'].map(TIER_SCORES).fillna(0)
    
    # The RQ_venue is the sum of all individual paper scores [cite: 57]
    return author_papers_df['venue_score'].sum()

def calculate_rq_age_cit(author_papers_df: pd.DataFrame) -> float:
    """
    Calculates the Age-Adjusted Citation Score (RQ_ageCit). 

    Formula: sum(ln(Ci + 1) / (1 + t - Yi)) for all papers. 

    Args:
        author_papers_df (pd.DataFrame): A DataFrame of an author's papers.

    Returns:
        float: The author's RQ_ageCit score.
    """
    if author_papers_df.empty:
        return 0.0
    
    t = 2025 # Current year for age calculation 
    
    # Apply the formula to each paper (row)
    # Ci = citation_count, Yi = year 
    author_papers_df['age_cit_score'] = np.log(author_papers_df['citation_count'] + 1) / \
                                        (1 + t - author_papers_df['year'])
    
    # The final score is the sum of all individual paper scores 
    return author_papers_df['age_cit_score'].sum()

# --- Example Usage ---
if __name__ == '__main__':
    try:
        # Load necessary data tables
        authorships = pd.read_csv('data/authorships.csv')
        paper_info = pd.read_csv('data/paper_info.csv')
    except FileNotFoundError as e:
        print(f"Error loading data file: {e}. Make sure files are in a 'data/' directory.")
        exit()

    # --- CHOOSE YOUR TARGET AUTHOR ID ---
    target_author_id = 143977260 # Eric Xing

    print(f"--- Calculating Research Quality for Author ID: {target_author_id} ---")

    # 1. Get all papers for the author
    author_papers = get_author_papers(target_author_id, authorships, paper_info)

    if not author_papers.empty:
        # 2. Calculate the Venue-Weighted Score
        rq_venue_score = calculate_rq_venue(author_papers)
        
        # 3. Calculate the Age-Adjusted Citation Score
        rq_age_cit_score = calculate_rq_age_cit(author_papers)

        print(f"\nTotal Papers Found: {len(author_papers)}")
        print(f"Venue-Weighted Score (RQ_venue): {rq_venue_score:.2f}")
        print(f"Age-Adjusted Citation Score (RQ_ageCit): {rq_age_cit_score:.4f}")
    else:
        print("No papers found for this author.")