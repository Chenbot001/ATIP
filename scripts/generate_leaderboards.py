import pandas as pd
import numpy as np
import ast
import re
import math
from typing import Optional, Dict, Tuple
import time
from tqdm import tqdm

# Import the functions from ATIP_metrics_v2.py
from ATIP_metrics_v2 import (
    get_career_length,
    calculate_anci_frac,
    calculate_citation_acceleration,
    calculate_author_pqi,
    _calculate_slope
)

def calculate_all_metrics_for_author(author_id: int, 
                                    authorships_df: pd.DataFrame,
                                    paper_info_df: pd.DataFrame,
                                    author_citation_metrics_df: pd.DataFrame,
                                    venue_tier_df: pd.DataFrame,
                                    paper_awards_df: pd.DataFrame) -> Tuple[float, float, float, float]:
    """
    Calculate all three key metrics for a single author.
    
    Returns:
        Tuple of (anci_score, cagr_score, linear_trend_score, pqi_score)
    """
    # Create a mapping from paper_id to s2_id for the functions that expect s2_id
    paper_id_to_s2_id = dict(zip(paper_info_df['corpus_id'], paper_info_df['s2_id']))
    
    # Create a modified authorships_df with s2_id column for compatibility
    authorships_with_s2 = authorships_df.copy()
    authorships_with_s2['s2_id'] = authorships_with_s2['paper_id'].map(paper_id_to_s2_id)
    
    # Filter out rows where s2_id mapping failed
    authorships_with_s2 = authorships_with_s2.dropna(subset=['s2_id'])
    
    if authorships_with_s2.empty:
        return 0.0, np.nan, 0.0, 0.0
    
    # Calculate career length first
    career_len = get_career_length(author_id, authorships_with_s2, paper_info_df)
    
    if career_len <= 0:
        return 0.0, np.nan, 0.0, 0.0
    
    # Calculate ANCI
    anci_score, _ = calculate_anci_frac(author_id, career_len, paper_info_df, authorships_with_s2)
    
    # Calculate citation acceleration (CAGR and linear trend)
    cagr_score, linear_trend_score = calculate_citation_acceleration(author_id, career_len, author_citation_metrics_df)
    
    # Calculate PQI
    pqi_score = calculate_author_pqi(author_id, authorships_df, paper_info_df, venue_tier_df, paper_awards_df)
    
    return anci_score, cagr_score, linear_trend_score, pqi_score

def generate_leaderboards():
    """Generate top 100 leaderboards for all three metrics."""
    
    print("Loading datasets...")
    # Load all necessary datasets
    paper_info_df = pd.read_csv('data/paper_info.csv')
    authorships_df = pd.read_csv('data/authorships.csv')
    author_profiles_df = pd.read_csv('data/author_profiles.csv')
    author_citation_metrics_df = pd.read_csv('data/author_citation_metrics.csv')
    paper_awards_df = pd.read_csv('data/paper_awards.csv')
    venue_tier_df = pd.read_csv('data/venue_tiers.csv')
    
    print(f"Processing {len(author_profiles_df)} authors...")
    
    # Initialize results storage
    results = []
    
    # Process each author with progress bar
    for idx, author_row in tqdm(author_profiles_df.iterrows(), total=len(author_profiles_df), desc="Calculating metrics"):
        author_id = author_row['author_id']
        author_name = f"{author_row['first_name']} {author_row['last_name']}"
        
        try:
            # Calculate all metrics
            anci_score, cagr_score, linear_trend_score, pqi_score = calculate_all_metrics_for_author(
                author_id, authorships_df, paper_info_df, author_citation_metrics_df, 
                venue_tier_df, paper_awards_df
            )
            
            results.append({
                'author_id': author_id,
                'author_name': author_name,
                'anci_score': anci_score,
                'cagr_score': cagr_score,
                'linear_trend_score': linear_trend_score,
                'pqi_score': pqi_score
            })
            
        except Exception as e:
            print(f"Error processing author {author_id} ({author_name}): {e}")
            # Add with default values
            results.append({
                'author_id': author_id,
                'author_name': author_name,
                'anci_score': 0.0,
                'cagr_score': np.nan,
                'linear_trend_score': 0.0,
                'pqi_score': 0.0
            })
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    print("Generating leaderboards...")
    
    # Generate ANCI leaderboard
    anci_leaderboard = results_df[results_df['anci_score'] > 0].copy()
    anci_leaderboard = anci_leaderboard.sort_values('anci_score', ascending=False).head(100)
    anci_leaderboard['rank'] = range(1, len(anci_leaderboard) + 1)
    anci_leaderboard = anci_leaderboard[['rank', 'author_id', 'author_name', 'anci_score']]
    anci_leaderboard.to_csv('../data/anci_leaderboard_top100.csv', index=False)
    print(f"ANCI leaderboard saved: {len(anci_leaderboard)} authors")
    
    # Generate CAGR leaderboard
    cagr_leaderboard = results_df[results_df['cagr_score'].notna()].copy()
    cagr_leaderboard = cagr_leaderboard.sort_values('cagr_score', ascending=False).head(100)
    cagr_leaderboard['rank'] = range(1, len(cagr_leaderboard) + 1)
    cagr_leaderboard = cagr_leaderboard[['rank', 'author_id', 'author_name', 'cagr_score']]
    cagr_leaderboard.to_csv('../data/cagr_leaderboard_top100.csv', index=False)
    print(f"CAGR leaderboard saved: {len(cagr_leaderboard)} authors")
    
    # Generate PQI leaderboard
    pqi_leaderboard = results_df[results_df['pqi_score'] > 0].copy()
    pqi_leaderboard = pqi_leaderboard.sort_values('pqi_score', ascending=False).head(100)
    pqi_leaderboard['rank'] = range(1, len(pqi_leaderboard) + 1)
    pqi_leaderboard = pqi_leaderboard[['rank', 'author_id', 'author_name', 'pqi_score']]
    pqi_leaderboard.to_csv('../data/pqi_leaderboard_top100.csv', index=False)
    print(f"PQI leaderboard saved: {len(pqi_leaderboard)} authors")
    
    # Also save the complete results for reference
    results_df.to_csv('../data/all_authors_metrics.csv', index=False)
    print(f"Complete results saved: {len(results_df)} authors")
    
    # Print some statistics
    print("\n=== Statistics ===")
    print(f"Total authors processed: {len(results_df)}")
    print(f"Authors with ANCI > 0: {len(results_df[results_df['anci_score'] > 0])}")
    print(f"Authors with valid CAGR: {len(results_df[results_df['cagr_score'].notna()])}")
    print(f"Authors with PQI > 0: {len(results_df[results_df['pqi_score'] > 0])}")
    
    # Print top 5 for each metric
    print("\n=== Top 5 ANCI ===")
    print(anci_leaderboard.head().to_string(index=False))
    
    print("\n=== Top 5 CAGR ===")
    print(cagr_leaderboard.head().to_string(index=False))
    
    print("\n=== Top 5 PQI ===")
    print(pqi_leaderboard.head().to_string(index=False))

if __name__ == '__main__':
    start_time = time.time()
    generate_leaderboards()
    end_time = time.time()
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds") 