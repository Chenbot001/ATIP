import pandas as pd
import numpy as np
import utils.csv_utils as csv_utils
from ATIP_metrics_v2 import *
from tqdm import tqdm


def calculate_anci_batch(author_profiles_df, authorships_df, paper_info_df):
    """
    Optimized batch calculation of ANCI metrics for all authors.
    Pre-computes data structures to avoid repeated calculations.
    """
    print("Pre-computing data structures...")
    
    # Pre-compute author counts per paper (this was being done 56k times!)
    print("  - Computing author counts per paper...")
    author_counts_per_paper = authorships_df.groupby('paper_id')['author_id'].nunique()
    
    # Pre-compute career lengths for all authors
    print("  - Computing career lengths for all authors...")
    career_lengths = {}
    for author_id in tqdm(author_profiles_df['author_id'], desc="Computing career lengths"):
        author_paper_ids = authorships_df[authorships_df['author_id'] == author_id]['paper_id'].unique()
        if len(author_paper_ids) == 0:
            career_lengths[author_id] = 0
            continue
            
        papers_details = paper_info_df[paper_info_df['corpus_id'].isin(author_paper_ids)]
        if papers_details.empty:
            career_lengths[author_id] = 0
            continue
            
        first_pub_year = papers_details['year'].min()
        career_length = 2025 - first_pub_year + 1
        career_lengths[author_id] = int(max(0, career_length))
    
    # Create a mapping from paper_id to paper details for faster lookups
    print("  - Creating paper details mapping...")
    paper_details_dict = {}
    for _, row in paper_info_df.iterrows():
        paper_details_dict[row['corpus_id']] = {
            'citation_count': row['citation_count'],
            'year': row['year']
        }
    
    print("Calculating ANCI metrics for all authors...")
    anci_results = []
    
    for author_id in tqdm(author_profiles_df['author_id'], desc="Processing authors"):
        career_length = career_lengths[author_id]
        
        if career_length <= 0:
            anci_results.append({
                'author_id': author_id,
                'anci_p_frac': 0.0,
                'career_length': 0,
                'paper_count': 0
            })
            continue
        
        # Get author's papers
        author_papers = authorships_df[authorships_df['author_id'] == author_id]['paper_id'].unique()
        
        if len(author_papers) == 0:
            anci_results.append({
                'author_id': author_id,
                'anci_p_frac': 0.0,
                'career_length': career_length,
                'paper_count': 0
            })
            continue
        
        # Calculate fractional citations using pre-computed data
        total_frac_citations = 0.0
        valid_papers = 0
        
        for paper_id in author_papers:
            if paper_id in paper_details_dict:
                paper_info = paper_details_dict[paper_id]
                num_authors = author_counts_per_paper.get(paper_id, 1)
                
                if num_authors > 0:
                    frac_citation = paper_info['citation_count'] / num_authors
                    total_frac_citations += frac_citation
                    valid_papers += 1
        
        if valid_papers > 0:
            anci_p_frac = total_frac_citations / (valid_papers * np.sqrt(career_length))
        else:
            anci_p_frac = 0.0
        
        anci_results.append({
            'author_id': author_id,
            'anci_p_frac': anci_p_frac,
            'career_length': career_length,
            'paper_count': valid_papers
        })
    
    return anci_results


def calculate_acceleration_batch(author_profiles_df, authorships_df, paper_info_df, author_citation_metrics_df):
    """
    Batch calculation of citation acceleration metrics for all authors.
    """
    print("Calculating citation acceleration metrics for all authors...")
    acceleration_results = []
    
    for author_id in tqdm(author_profiles_df['author_id'], desc="Processing authors"):
        # Get career length for this author
        author_paper_ids = authorships_df[authorships_df['author_id'] == author_id]['paper_id'].unique()
        if len(author_paper_ids) == 0:
            career_length = 0
        else:
            papers_details = paper_info_df[paper_info_df['corpus_id'].isin(author_paper_ids)]
            if papers_details.empty:
                career_length = 0
            else:
                first_pub_year = papers_details['year'].min()
                career_length = 2025 - first_pub_year + 1
                career_length = int(max(0, career_length))
        
        # Calculate citation acceleration
        cagr_score, linear_trend_score = calculate_citation_acceleration(
            author_id, career_length, author_citation_metrics_df
        )
        
        # Use CAGR as primary acceleration metric, fallback to linear trend if CAGR is NaN
        acceleration_score = cagr_score if not np.isnan(cagr_score) else linear_trend_score
        if np.isnan(acceleration_score):
            acceleration_score = 0.0
        
        acceleration_results.append({
            'author_id': author_id,
            'acceleration_score': acceleration_score,
            'cagr_score': cagr_score if not np.isnan(cagr_score) else 0.0,
            'linear_trend_score': linear_trend_score,
            'career_length': career_length,
            'paper_count': len(author_paper_ids)
        })
    
    return acceleration_results


def calculate_pqi_batch(author_profiles_df, authorships_df, paper_info_df, venue_tier_df, paper_awards_df):
    """
    Batch calculation of PQI metrics for all authors.
    """
    print("Calculating PQI metrics for all authors...")
    pqi_results = []
    
    for author_id in tqdm(author_profiles_df['author_id'], desc="Processing authors"):
        # Get career length for this author
        author_paper_ids = authorships_df[authorships_df['author_id'] == author_id]['paper_id'].unique()
        if len(author_paper_ids) == 0:
            career_length = 0
        else:
            papers_details = paper_info_df[paper_info_df['corpus_id'].isin(author_paper_ids)]
            if papers_details.empty:
                career_length = 0
            else:
                first_pub_year = papers_details['year'].min()
                career_length = 2025 - first_pub_year + 1
                career_length = int(max(0, career_length))
        
        # Calculate PQI
        pqi_score = calculate_author_pqi(
            author_id, authorships_df, paper_info_df, venue_tier_df, paper_awards_df
        )
        
        pqi_results.append({
            'author_id': author_id,
            'pqi_score': pqi_score,
            'career_length': career_length,
            'paper_count': len(author_paper_ids)
        })
    
    return pqi_results


if __name__ == "__main__":
    # Define target metric and validate
    target_metric = 'quality'  # Change this to 'impact', 'acceleration', or 'quality'
    
    valid_ranking_metrics = ['impact', 'acceleration', 'quality']
    
    if target_metric not in valid_ranking_metrics:
        print(f"Error: Invalid target metric '{target_metric}'. Valid options are: {valid_ranking_metrics}")
        exit(1)
    
    print(f"Generating leaderboard for metric: {target_metric}")
    
    # Load data
    paper_info_df = pd.read_csv('data/paper_info.csv')
    authorships_df = pd.read_csv('data/authorships.csv')
    author_profiles_df = pd.read_csv('data/author_profiles.csv')
    author_citation_metrics_df = pd.read_csv('data/author_citation_metrics.csv')
    paper_awards_df = pd.read_csv('data/paper_awards.csv')
    venue_tier_df = pd.read_csv('data/venue_tiers.csv')

    TOP_N = 100

    # Generate leaderboard based on target metric
    if target_metric == 'impact':
        # Calculate ANCI metrics
        anci_results = calculate_anci_batch(author_profiles_df, authorships_df, paper_info_df)
        
        # Convert results to DataFrame
        metric_df = pd.DataFrame(anci_results)
        
        # Sort by ANCI score in descending order
        metric_df_sorted = metric_df.sort_values('anci_p_frac', ascending=False)
        
        # Join with author_profiles_df to get author names
        metric_df_with_names = metric_df_sorted.merge(
            author_profiles_df[['author_id', 'first_name', 'last_name']], 
            on='author_id', 
            how='left'
        )
        
        # Create author_name column by combining first_name and last_name
        metric_df_with_names['author_name'] = metric_df_with_names['first_name'] + ' ' + metric_df_with_names['last_name']
        
        # Add ranking column
        metric_df_with_names['ranking'] = range(1, len(metric_df_with_names) + 1)
        
        # Select and reorder columns
        final_leaderboard = metric_df_with_names[['ranking', 'author_id', 'author_name', 'anci_p_frac', 'paper_count', 'career_length']]
        
        # Display top N results
        final_leaderboard = final_leaderboard.head(TOP_N)
        print(f"\nTop {TOP_N} authors by ANCI score:")
        print(final_leaderboard)
        
        # Save results
        final_leaderboard.to_csv(f'data/top{TOP_N}_anci.csv', index=False)
        print(f"\nFull leaderboard saved to 'data/top{TOP_N}_anci.csv'")
        
    elif target_metric == 'acceleration':
        # Calculate citation acceleration metrics
        acceleration_results = calculate_acceleration_batch(author_profiles_df, authorships_df, paper_info_df, author_citation_metrics_df)
        
        # Convert results to DataFrame
        metric_df = pd.DataFrame(acceleration_results)
        
        # Sort by acceleration score in descending order
        metric_df_sorted = metric_df.sort_values('acceleration_score', ascending=False)
        
        # Join with author_profiles_df to get author names
        metric_df_with_names = metric_df_sorted.merge(
            author_profiles_df[['author_id', 'first_name', 'last_name']], 
            on='author_id', 
            how='left'
        )
        
        # Create author_name column by combining first_name and last_name
        metric_df_with_names['author_name'] = metric_df_with_names['first_name'] + ' ' + metric_df_with_names['last_name']
        
        # Add ranking column
        metric_df_with_names['ranking'] = range(1, len(metric_df_with_names) + 1)
        
        # Select and reorder columns
        final_leaderboard = metric_df_with_names[['ranking', 'author_id', 'author_name', 'acceleration_score', 'paper_count', 'career_length']]
        
        # Display top N results
        final_leaderboard = final_leaderboard.head(TOP_N)
        print(f"\nTop {TOP_N} authors by citation acceleration:")
        print(final_leaderboard)
        
        # Save results
        final_leaderboard.to_csv(f'data/top{TOP_N}_accel.csv', index=False)
        print(f"\nFull leaderboard saved to 'data/top{TOP_N}_accel.csv'")
        
    elif target_metric == 'quality':
        # Calculate PQI metrics
        pqi_results = calculate_pqi_batch(author_profiles_df, authorships_df, paper_info_df, venue_tier_df, paper_awards_df)
        
        # Convert results to DataFrame
        metric_df = pd.DataFrame(pqi_results)
        
        # Sort by PQI score in descending order
        metric_df_sorted = metric_df.sort_values('pqi_score', ascending=False)
        
        # Join with author_profiles_df to get author names
        metric_df_with_names = metric_df_sorted.merge(
            author_profiles_df[['author_id', 'first_name', 'last_name']], 
            on='author_id', 
            how='left'
        )
        
        # Create author_name column by combining first_name and last_name
        metric_df_with_names['author_name'] = metric_df_with_names['first_name'] + ' ' + metric_df_with_names['last_name']
        
        # Add ranking column
        metric_df_with_names['ranking'] = range(1, len(metric_df_with_names) + 1)
        
        # Select and reorder columns
        final_leaderboard = metric_df_with_names[['ranking', 'author_id', 'author_name', 'pqi_score', 'paper_count', 'career_length']]
        
        # Display top N results
        final_leaderboard = final_leaderboard.head(TOP_N)
        print(f"\nTop {TOP_N} authors by PQI score:")
        print(final_leaderboard)
        
        # Save results
        final_leaderboard.to_csv(f'data/top{TOP_N}_pqi.csv', index=False)
        print(f"\nFull leaderboard saved to 'data/top{TOP_N}_pqi.csv'")