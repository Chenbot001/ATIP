import pandas as pd
import numpy as np
import ast

def get_author_id_from_name(full_name: str, df_author_profiles: pd.DataFrame) -> list:
    """Helper function to find author_id from full name."""
    author_row = df_author_profiles[
        (df_author_profiles['first_name'] + ' ' + df_author_profiles['last_name']) == full_name
    ]
    if not author_row.empty:
        return author_row['author_id'].tolist()
    return []

# --- NEW: Dedicated Career Length Function ---
def get_career_length(author_id: int, 
                      authorships_df: pd.DataFrame, 
                      paper_info_df: pd.DataFrame) -> int:
    """
    Calculates the career length for a single author.

    Args:
        author_id (int): The unique identifier for the author.
        authorships_df (pd.DataFrame): DataFrame linking authors to papers.
        paper_info_df (pd.DataFrame): DataFrame with paper publication years.

    Returns:
        int: The author's career length in years. Returns 0 if no papers are found.
    """
    author_s2_ids = authorships_df[authorships_df['author_id'] == author_id]['s2_id'].unique()
    if len(author_s2_ids) == 0:
        return 0
    
    papers_details = paper_info_df[paper_info_df['s2_id'].isin(author_s2_ids)]
    if papers_details.empty:
        return 0
        
    first_pub_year = papers_details['year'].min()
    career_length = 2025 - first_pub_year + 1
    
    return int(max(0, career_length))

# --- REFACTORED: Metric Functions ---
def calculate_anci_frac(author_id: int,
                        career_length: int,
                        paper_info_df: pd.DataFrame,
                        authorships_df: pd.DataFrame) -> tuple:
    """
    Calculates the co-authorship fractionalized ANCI metric using a pre-calculated career length.
    """
    author_s2_ids = authorships_df[authorships_df['author_id'] == author_id]['s2_id'].unique()
    papers_details = paper_info_df[paper_info_df['s2_id'].isin(author_s2_ids)].copy()
    
    if career_length <= 0 or papers_details.empty:
        return 0.0, 0
    
    author_counts = authorships_df.groupby('s2_id')['author_id'].nunique()
    papers_details['num_authors'] = papers_details['s2_id'].map(author_counts)
    papers_details.dropna(subset=['num_authors'], inplace=True)
    papers_details = papers_details[papers_details['num_authors'] > 0]
    papers_details['frac_citation'] = papers_details['citation_count'] / papers_details['num_authors']
    
    c_frac = papers_details['frac_citation'].sum()
    anci_frac = c_frac / np.sqrt(career_length)
    
    return anci_frac, len(papers_details)

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
                                    citations_by_year_df: pd.DataFrame) -> tuple:
    """
    Calculates citation acceleration using a pre-calculated career length.
    """
    # The function signature was already correct, so no major changes are needed here.
    author_data = citations_by_year_df[citations_by_year_df['author_id'] == author_id]
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


# --- REFACTORED: Example Usage ---
if __name__ == '__main__':
    # --- CHOOSE YOUR INPUT ---
    # Option 1: Provide a name (string)
    # target_author = "Eric Xing" 
    # Option 2: Provide an ID (integer)
    target_author = 143977260 

    # Load all necessary datasets
    paper_info_df = pd.read_csv('data/paper_info.csv')
    authorships_df = pd.read_csv('data/authorships.csv')
    authorships_df.rename(columns={'paper_id': 's2_id'}, inplace=True)
    author_profiles_df = pd.read_csv('data/author_profiles.csv')
    author_citation_metrics_df = pd.read_csv('data/author_citation_metrics.csv')

    target_author_ids = []
    display_name = ""

    # Dynamically determine if input is a name (str) or an ID (int)
    if isinstance(target_author, str):
        display_name = target_author
        target_author_ids = get_author_id_from_name(display_name, author_profiles_df)
    elif isinstance(target_author, int):
        target_author_ids = [target_author]
        # Look up the name for display purposes
        author_profile = author_profiles_df[author_profiles_df['author_id'] == target_author]
        if not author_profile.empty:
            display_name = f"{author_profile.iloc[0]['first_name']} {author_profile.iloc[0]['last_name']}"
        else:
            display_name = f"ID: {target_author}"
    else:
        print("Invalid target_author type. Please provide a string (name) or integer (ID).")
        exit()
    
    # Proceed with calculation loop
    if not target_author_ids:
        print(f"No authors found for input: '{display_name}'")
        exit()
    
    print(f"Input: '{display_name}' | Found matching ID(s): {target_author_ids}\n")
    
    for author_id in target_author_ids:
        print(f"--- Calculating metrics for Author ID: {author_id} ---")
        
        career_len = get_career_length(author_id, authorships_df, paper_info_df)
        
        if career_len > 0:
            anci_metric, paper_count = calculate_anci_frac(author_id, career_len, paper_info_df, authorships_df)
            cagr, linear_trend = calculate_citation_acceleration(author_id, career_len, author_citation_metrics_df)
            
            print(f"  Author Name: {display_name}")
            print(f"  Career Length: {career_len} years")
            print(f"  Paper Count: {paper_count}")
            print(f"\n  ANCI_frac: {anci_metric:.4f}")
            print(f"\n  Hybrid Acceleration Metrics:")
            print(f"    - CAGR (n <= 3): {cagr:.4f}")
            print(f"    - Linear Trend: {linear_trend:.4f}")
            if career_len < 6:
                print("      (Trend set to 0.0 as career is less than 6 years)")
        else:
            print("  Could not calculate metrics due to zero career length or no publications.")
        print("-" * 50)