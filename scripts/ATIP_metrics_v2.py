import pandas as pd
import numpy as np
import ast
import re
import math
from typing import Optional, Dict

# --- Helper Functions ---
def get_author_id_from_name(full_name: str, author_profiles_df: pd.DataFrame) -> list:
    """Helper function to find author_id from full name."""
    author_row = author_profiles_df[
        (author_profiles_df['first_name'] + ' ' + author_profiles_df['last_name']) == full_name
    ]
    if not author_row.empty:
        return author_row['author_id'].tolist()
    return []

# --- Low-level Metrics ---
def get_career_length(author_id: int, 
                      authorships_df: pd.DataFrame, 
                      paper_info_df: pd.DataFrame) -> int:
    """
    Calculates the career length (Y) for a single author.

    Args:
        author_id (int): The unique identifier for the author.
        authorships_df (pd.DataFrame): DataFrame linking authors to papers.
        paper_info_df (pd.DataFrame): DataFrame with paper publication years.

    Returns:
        int: The author's career length in years. Returns 0 if no papers are found.
    """
    author_paper_ids = authorships_df[authorships_df['author_id'] == author_id]['paper_id'].unique()
    if len(author_paper_ids) == 0:
        return 0
    
    papers_details = paper_info_df[paper_info_df['paper_id'].isin(author_paper_ids)]
    if papers_details.empty:
        return 0
        
    first_pub_year = papers_details['year'].min()
    career_length = 2025 - first_pub_year + 1
    
    return int(max(0, career_length))

# --- Adjusted Citation Impact (ANCI)---
def calculate_anci(author_id: int,
                        career_length: int,
                        paper_info_df: pd.DataFrame,
                        authorships_df: pd.DataFrame) -> tuple:
    """
    Calculates the co-authorship fractionalized ANCI metric using a pre-calculated career length.
    """
    author_paper_ids = authorships_df[authorships_df['author_id'] == author_id]['paper_id'].unique()
    papers_details = paper_info_df[paper_info_df['paper_id'].isin(author_paper_ids)].copy()
    
    if career_length <= 0 or papers_details.empty:
        return 0.0, 0
    
    author_counts = authorships_df.groupby('paper_id')['author_id'].nunique()
    papers_details['num_authors'] = papers_details['paper_id'].map(author_counts)
    papers_details.dropna(subset=['num_authors'], inplace=True)
    papers_details = papers_details[papers_details['num_authors'] > 0]
    papers_details['frac_citation'] = papers_details['citation_count'] / papers_details['num_authors']
    
    c_frac = papers_details['frac_citation'].sum()
    anci_p_frac = c_frac / (len(papers_details) * np.sqrt(career_length))
    
    return anci_p_frac, len(papers_details)

# --- Citation Acceleration (CAGR + Linear Trend) ---
def _calculate_slope(citations_in_window: dict) -> float:
    """Helper to calculate the slope of a linear regression."""
    years = np.array(list(citations_in_window.keys()))
    citations = np.array(list(citations_in_window.values()))
    if len(years) < 2: return 0.0
    mean_y, mean_c = np.mean(years), np.mean(citations)
    numerator = np.sum((years - mean_y) * (citations - mean_c))
    denominator = np.sum((years - mean_y)**2)
    return float(numerator / denominator if denominator != 0 else 0.0)

def calculate_citation_acceleration(author_id: int,
                                    career_length: int,
                                    author_citation_metrics_df: pd.DataFrame) -> tuple:
    """
    Calculates citation acceleration using a pre-calculated career length.
    """
    # The function signature was already correct, so no major changes are needed here.
    author_data = author_citation_metrics_df[author_citation_metrics_df['author_id'] == author_id]
    if author_data.empty: return (np.nan, np.nan)
    citations_str = author_data['citations_by_year'].iloc[0]
    try:
        citations_by_year = {int(k): v for k, v in ast.literal_eval(citations_str).items()}
    except (ValueError, SyntaxError):
        return (np.nan, np.nan)
    if not citations_by_year: return (np.nan, np.nan)

    # CAGR Calculation
    cagr_score = np.nan
    n_cagr = min(3, career_length - 1)
    if n_cagr >= 1:
        k, t = 1, 2024
        c_t = citations_by_year.get(t, 0) + k
        c_t_n = citations_by_year.get(t - n_cagr, 0) + k
        cagr_score = (c_t / c_t_n)**(1/n_cagr) - 1

    # Linear-Trend Second Derivative
    linear_trend_score = 0.0
    if career_length >= 6:
        w, t = 2, 2024
        current_window = {y: c for y, c in citations_by_year.items() if t - w < y <= t}
        previous_window = {y: c for y, c in citations_by_year.items() if t - 2*w < y <= t - w}
        if len(current_window) >= 2 and len(previous_window) >= 2:
            beta_current = _calculate_slope(current_window)
            beta_previous = _calculate_slope(previous_window)
            linear_trend_score = (beta_current - beta_previous) / w

    return (cagr_score, linear_trend_score)

# --- Publication Quality Index (PQI)---
# Step 1: Base score for each venue tier
BASE_TIER_SCORES: Dict[str, float] = {
    'A': 4.0,
    'B': 3.0,
    'C': 2.0,
    'D': 1.0
}

# Step 2: Weight for each publication track
TRACK_WEIGHTS: Dict[str, float] = {
    'main': 1.0,
    'long': 1.0,
    'short': 0.8,
    'findings': 0.7,
    'industry': 0.6,
    'srw': 0.5,
    'demo': 0.4,
    'tutorials': 0.2
}

AWARD_WEIGHTS = {
    "Best Overall Paper": 5.0,
    "Test-of-Time Award": 5.0,
    "Best Paper Runner-Up": 4.0,
    "Outstanding Paper": 4.0,
    "Area Chair/SAC Award": 3.0,
    "Best Short Paper": 3.0,
    "Best Thematic/Resource/Impact Paper": 3.0,
    "Honorable Mention": 2.0,
    "Reproduction Award": 2.0,
    "SRW Best Paper Award": 2.0,
    "Best Demo Paper": 1.0,
    "Specific Contribution Award": 1.0,
}

MAX_AWARD_POINTS = 5.0

# Weights for the final PQI formula
PQI_WEIGHTS = {'venue': 0.40, 'citation': 0.30, 'award': 0.20, 'recency': 0.10}

def _find_paper_track(paper_info_df: pd.DataFrame, paper_id: int) -> str:
    """
    Determines the track of a paper using its acl_id from the paper_info DataFrame.

    It first tries to match track keywords (e.g., 'findings', 'demo') in the acl_id.
    If that fails, it looks for a hyphen followed by a 4-digit code to determine the track.
    If no specific track can be determined, it defaults to 'main'.

    Args:
        paper_info_df: DataFrame containing paper info, including 'paper_id' and 'acl_id'.
        paper_id: The paper_id of the paper to find the track for.

    Returns:
        The determined track as a string.
    """
    try:
        # Find the acl_id for the given paper_id
        acl_id = paper_info_df.loc[paper_info_df['paper_id'] == paper_id, 'acl_id'].iloc[0]
        if pd.isna(acl_id):
            return 'main'
    except IndexError:
        return 'main'

    # --- Method 1: Direct string matching ---
    keyword_tracks = ['findings', 'short', 'srw', 'demo', 'tutorials', 'industry', 'main']
    for track in keyword_tracks:
        if track in acl_id:
            return track

    # --- Method 2: Generalized digit code interpretation ---
    # Look for any hyphen followed by 4 digits (e.g., "X-1234", "ABC-4567")
    match = re.search(r'-(\d{4})', acl_id)
    if match:
        digit_code = match.group(1)
        first_digit = digit_code[0]
        
        digit_map = {
            '1': 'long',
            '2': 'short',
            '3': 'srw',
            '4': 'demo',
            '5': 'tutorials'
        }
        if first_digit in digit_map:
            return digit_map[first_digit]

    # --- Default Case ---
    return 'main'

def _calculate_venue_score(paper_info_df: pd.DataFrame,
                           venue_tier_df: pd.DataFrame,
                           paper_id: int) -> float:
    """
    Calculates a composite venue score based on a paper's venue tier and track.

    Args:
        paper_info_df: DataFrame with paper information (paper_id, venue, acl_id).
        venue_tier_df: DataFrame mapping venues to tiers ('A', 'B', 'C', 'D').
        paper_id: The paper_id of the paper to score.

    Returns:
        The calculated floating point venue score.
    """
    try:
        # Get the paper's venue string
        venue = paper_info_df.loc[paper_info_df['paper_id'] == paper_id, 'venue'].iloc[0]
    except IndexError:
        return 0.0 # Paper not found

    # Determine Base Tier Score
    try:
        matching_rows = venue_tier_df[venue_tier_df['venue'] == venue]
        tier = matching_rows['tier'].iloc[0] if not matching_rows.empty else 'D'
    except (IndexError, KeyError):
        tier = 'D' # Default to lowest tier if venue is unranked
    base_score = BASE_TIER_SCORES.get(tier, 1.0)

    # Determine Track Weight by calling the helper function
    track = _find_paper_track(paper_info_df, paper_id)
    track_weight = TRACK_WEIGHTS.get(track, 0.0) # Default to 0 if track is unknown

    return base_score * track_weight

def _calculate_award_impact_score(paper_awards_df: pd.DataFrame, 
                                  paper_id: int) -> float:
    """
    Calculates a normalized award score for a specific paper ID from a DataFrame.

    Args:
        paper_awards_df: DataFrame containing paper awards data.
        paper_id: The integer ID of the paper to look up.

    Returns:
        A normalized score between 0.0 and 1.0. Returns 0.0 if the paper has no awards.
    """
    # Filter the DataFrame to find all awards for the given paper_id
    paper_awards = paper_awards_df[paper_awards_df['paper_id'] == paper_id]

    if paper_awards.empty:
        return 0.0

    # Get the list of award names from the specified column
    awards_list = paper_awards['award'].tolist()

    # Find the maximum point value among the paper's awards
    max_points = 0.0
    for award in awards_list:
        points = AWARD_WEIGHTS.get(award, 0.0)
        if points > max_points:
            max_points = points
            
    # Normalize the score
    return max_points / MAX_AWARD_POINTS
    
def _calculate_recency_score(publication_year: int) -> float:
    """
    Calculates the recency score for a paper based on its publication year.

    This score rewards recent work while down-weighting older papers.
    The formula is 1 / (1 + t - Yi), where 't' is the current year 
    and 'Yi' is the publication year of the paper.

    Args:
        publication_year: The year the paper was published.

    Returns:
        The calculated recency score.
    """
    current_year = 2025 # Career length is calculated as mid-2025 minus the first paper's year.
    
    # The age is the difference between the current year and the publication year.
    # We add 1 to the age in the denominator to avoid division by zero for papers
    # published in the current year.
    age = current_year - publication_year
    
    # Handle potential future-dated papers, though unlikely.
    if age < 0:
        return 0.0
        
    return 1 / (1 + age)

def _calculate_paper_pqi(paper_id: int,
                         paper_info_df: pd.DataFrame,
                         venue_tier_df: pd.DataFrame,
                         paper_awards_df: pd.DataFrame) -> float:
    """Calculates the full PQI score for a single paper."""
    # 1. Venue Score
    venue_score = _calculate_venue_score(paper_info_df, venue_tier_df, paper_id)

    # 2. Citation Score
    try:
        cite_count = paper_info_df.loc[paper_info_df['paper_id'] == paper_id, 'citation_count'].iloc[0]
        citation_score = math.log(cite_count + 1)
    except IndexError:
        citation_score = 0.0

    # 3. Award Score
    award_score = _calculate_award_impact_score(paper_awards_df, paper_id=paper_id)
    
    # 4. Recency Score
    try:
        year = paper_info_df.loc[paper_info_df['paper_id'] == paper_id, 'year'].iloc[0]
        recency_score = _calculate_recency_score(year)
    except IndexError:
        recency_score = 0.0
        
    # Final weighted calculation
    pqi = (
        PQI_WEIGHTS['venue'] * venue_score +
        PQI_WEIGHTS['citation'] * citation_score +
        PQI_WEIGHTS['award'] * award_score +
        PQI_WEIGHTS['recency'] * recency_score
    )
    return pqi

def calculate_author_pqi(author_id: int,
                         authorships_df: pd.DataFrame,
                         paper_info_df: pd.DataFrame,
                         venue_tier_df: pd.DataFrame,
                         paper_awards_df: pd.DataFrame
) -> float:
    """Calculates the mean Publication Quality Index (PQI) for a single author."""
    author_papers = authorships_df[authorships_df['author_id'] == author_id]
    if author_papers.empty:
        return 0.0
    
    pqi_scores = [
        _calculate_paper_pqi(pid, paper_info_df, venue_tier_df, paper_awards_df)
        for pid in author_papers['paper_id']
    ]
    
    # Return the mean of the PQI scores for all of the author's papers
    return sum(pqi_scores) / len(pqi_scores) if pqi_scores else 0.0

# --- Main Function ---
if __name__ == '__main__':
    # --- CHOOSE YOUR INPUT ---
    # Option 1: Provide a name (string)
    # target_author = "Eric Xing" 
    # Option 2: Provide an ID (integer)
    target_author = 143977260 

    # Load all necessary datasets
    paper_info_df = pd.read_csv('data/paper_info.csv')
    authorships_df = pd.read_csv('data/authorships.csv')
    author_profiles_df = pd.read_csv('data/author_profiles.csv')
    author_citation_metrics_df = pd.read_csv('data/author_citation_metrics.csv')
    paper_awards_df = pd.read_csv('data/paper_awards.csv')
    venue_tier_df = pd.read_csv('data/venue_tiers.csv')

    author_1_pqi = calculate_author_pqi(target_author, authorships_df, paper_info_df, venue_tier_df, paper_awards_df)
    print(f"Mean PQI for Author 1: {author_1_pqi:.4f}")

    # target_author_ids = []
    # display_name = ""

    # # Dynamically determine if input is a name (str) or an ID (int)
    # if isinstance(target_author, str):
    #     display_name = target_author
    #     target_author_ids = get_author_id_from_name(display_name, author_profiles_df)
    # elif isinstance(target_author, int):
    #     target_author_ids = [target_author]
    #     # Look up the name for display purposes
    #     author_profile = author_profiles_df[author_profiles_df['author_id'] == target_author]
    #     if not author_profile.empty:
    #         display_name = f"{author_profile.iloc[0]['first_name']} {author_profile.iloc[0]['last_name']}"
    #     else:
    #         display_name = f"ID: {target_author}"
    # else:
    #     print("Invalid target_author type. Please provide a string (name) or integer (ID).")
    #     exit()
    
    # # Proceed with calculation loop
    # if not target_author_ids:
    #     print(f"No authors found for input: '{display_name}'")
    #     exit()
    
    # print(f"Input: '{display_name}' | Found matching ID(s): {target_author_ids}\n")
    
    # for author_id in target_author_ids:
    #     print(f"--- Calculating metrics for: {display_name} ---")
        
    #     career_len = get_career_length(author_id, authorships_df, paper_info_df)
        
    #     if career_len > 0:
    #         anci_metric, paper_count = calculate_anci(author_id, career_len, paper_info_df, authorships_df)
    #         cagr, linear_trend = calculate_citation_acceleration(author_id, career_len, author_citation_metrics_df)
            
    #         print(f"  Career Length: {career_len} years")
    #         print(f"  Paper Count: {paper_count}")
    #         print(f"\n  ANCI_frac: {anci_metric:.4f}")
    #         print(f"\n  Hybrid Acceleration Metrics:")
    #         print(f"    - CAGR (n <= 3): {cagr:.4f}")
    #         print(f"    - Linear Trend: {linear_trend:.4f}")
    #         if career_len < 6:
    #             print("      (Trend set to 0.0 as career is less than 6 years)")
    #     else:
    #         print("  Could not calculate metrics due to zero career length or no publications.")
    #     print("-" * 50)