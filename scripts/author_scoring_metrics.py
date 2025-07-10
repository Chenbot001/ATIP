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
    print("Pre-computing data structures for ANCI...")
    
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
            
        papers_details = paper_info_df[paper_info_df['paper_id'].isin(author_paper_ids)]
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
        paper_details_dict[row['paper_id']] = {
            'citation_count': row['citation_count'],
            'year': row['year']
        }
    
    print("Calculating ANCI metrics for all authors...")
    anci_results = []
    
    for author_id in tqdm(author_profiles_df['author_id'], desc="Processing authors for ANCI"):
        career_length = career_lengths[author_id]
        
        if career_length <= 0:
            anci_results.append({
                'author_id': author_id,
                'anci_score': 0.0,
                'career_length': 0,
                'paper_count': 0
            })
            continue
        
        # Get author's papers
        author_papers = authorships_df[authorships_df['author_id'] == author_id]['paper_id'].unique()
        
        if len(author_papers) == 0:
            anci_results.append({
                'author_id': author_id,
                'anci_score': 0.0,
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
            anci_score = total_frac_citations / (valid_papers * np.sqrt(career_length))
        else:
            anci_score = 0.0
        
        anci_results.append({
            'author_id': author_id,
            'anci_score': anci_score,
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
    
    for author_id in tqdm(author_profiles_df['author_id'], desc="Processing authors for acceleration"):
        # Get career length for this author
        author_paper_ids = authorships_df[authorships_df['author_id'] == author_id]['paper_id'].unique()
        if len(author_paper_ids) == 0:
            career_length = 0
        else:
            papers_details = paper_info_df[paper_info_df['paper_id'].isin(author_paper_ids)]
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
            'accel_score': acceleration_score,
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
    
    for author_id in tqdm(author_profiles_df['author_id'], desc="Processing authors for PQI"):
        # Get career length for this author
        author_paper_ids = authorships_df[authorships_df['author_id'] == author_id]['paper_id'].unique()
        if len(author_paper_ids) == 0:
            career_length = 0
        else:
            papers_details = paper_info_df[paper_info_df['paper_id'].isin(author_paper_ids)]
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


def create_comprehensive_author_profiles():
    """
    Create a comprehensive author profiles table with all metrics.
    """
    print("Loading data...")
    
    # Load data
    paper_info_df = pd.read_csv('data/paper_info.csv')
    authorships_df = pd.read_csv('data/authorships.csv')
    author_profiles_df = pd.read_csv('data/author_profiles.csv')
    author_citation_metrics_df = pd.read_csv('data/author_citation_metrics.csv')
    paper_awards_df = pd.read_csv('data/paper_awards.csv')
    venue_tier_df = pd.read_csv('data/venue_tiers.csv')

    print(f"Loaded {len(author_profiles_df)} author profiles")

    # Calculate all metrics in batch
    print("\n=== Calculating ANCI scores ===")
    anci_results = calculate_anci_batch(author_profiles_df, authorships_df, paper_info_df)
    
    print("\n=== Calculating acceleration scores ===")
    acceleration_results = calculate_acceleration_batch(author_profiles_df, authorships_df, paper_info_df, author_citation_metrics_df)
    
    print("\n=== Calculating PQI scores ===")
    pqi_results = calculate_pqi_batch(author_profiles_df, authorships_df, paper_info_df, venue_tier_df, paper_awards_df)

    # Convert results to DataFrames
    anci_df = pd.DataFrame(anci_results)
    acceleration_df = pd.DataFrame(acceleration_results)
    pqi_df = pd.DataFrame(pqi_results)

    print("\n=== Creating comprehensive author profiles ===")
    
    # Start with author profiles as the base
    comprehensive_df = author_profiles_df.copy()
    
    # Create author_name by combining first_name and last_name
    comprehensive_df['author_name'] = comprehensive_df['first_name'] + ' ' + comprehensive_df['last_name']
    
    # Rename columns for consistency
    comprehensive_df = comprehensive_df.rename(columns={
        'latest_affiliation': 'affiliation',
        'total_citations': 'citations'
    })
    
    # Merge with metric results
    comprehensive_df = comprehensive_df.merge(anci_df[['author_id', 'anci_score']], on='author_id', how='left')
    comprehensive_df = comprehensive_df.merge(acceleration_df[['author_id', 'accel_score']], on='author_id', how='left')
    comprehensive_df = comprehensive_df.merge(pqi_df[['author_id', 'pqi_score']], on='author_id', how='left')
    
    # Fill NaN values with 0 for metric scores
    comprehensive_df['anci_score'] = comprehensive_df['anci_score'].fillna(0.0)
    comprehensive_df['accel_score'] = comprehensive_df['accel_score'].fillna(0.0)
    comprehensive_df['pqi_score'] = comprehensive_df['pqi_score'].fillna(0.0)
    
    # Select and reorder columns as requested
    final_columns = [
        'author_id', 
        'author_name', 
        'affiliation', 
        'pqi_score', 
        'anci_score', 
        'accel_score', 
        'h_index', 
        'citations'
    ]
    
    web_profiles_df = comprehensive_df[final_columns].copy()
    
    # Fill any remaining NaN values
    web_profiles_df = web_profiles_df.fillna({
        'author_name': 'Unknown',
        'affiliation': 'Unknown',
        'h_index': 0,
        'citations': 0
    })
    
    print(f"\nFinal table shape: {web_profiles_df.shape}")
    print(f"Columns: {web_profiles_df.columns.tolist()}")
    
    # Display sample of results
    print("\nSample of comprehensive author profiles:")
    print(web_profiles_df.head(10))
    
    # Save results
    output_file = 'data/web_profiles.csv'
    web_profiles_df.to_csv(output_file, index=False)
    print(f"\nComprehensive author profiles saved to '{output_file}'")
    
    # Print summary statistics
    print("\n=== Summary Statistics ===")
    print(f"Total authors: {len(web_profiles_df)}")
    print(f"Authors with PQI > 0: {len(web_profiles_df[web_profiles_df['pqi_score'] > 0])}")
    print(f"Authors with ANCI > 0: {len(web_profiles_df[web_profiles_df['anci_score'] > 0])}")
    print(f"Authors with acceleration > 0: {len(web_profiles_df[web_profiles_df['accel_score'] > 0])}")
    print(f"Average h-index: {web_profiles_df['h_index'].mean():.2f}")
    print(f"Average citations: {web_profiles_df['citations'].mean():.2f}")
    
    return web_profiles_df


if __name__ == "__main__":
    # Create comprehensive author profiles
    web_profiles_df = create_comprehensive_author_profiles()