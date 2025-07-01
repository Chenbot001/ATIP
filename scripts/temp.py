import pandas as pd
import numpy as np

def compare_h_index_values():
    """
    Compare h_index values between researcher_profiles.csv and researcher_citation_metrics.csv
    """
    print("Loading data files...")
    
    # Load the data files
    profiles_df = pd.read_csv('data/researcher_profiles.csv')
    metrics_df = pd.read_csv('data/researcher_citation_metrics.csv')
    
    print(f"Loaded {len(profiles_df)} researcher profiles")
    print(f"Loaded {len(metrics_df)} researcher citation metrics")
    
    # Merge the dataframes on researcher_id
    merged_df = profiles_df.merge(metrics_df, on='researcher_id', how='inner', suffixes=('_profile', '_metrics'))
    
    print(f"Found {len(merged_df)} researchers with data in both files")
    
    # Compare h_index values
    comparison_results = []
    
    for _, row in merged_df.iterrows():
        researcher_id = row['researcher_id']
        profile_h_index = row['h_index']
        atip_h_index = row['atip_h_index']
        
        # Check if values match
        match = profile_h_index == atip_h_index
        
        comparison_results.append({
            'researcher_id': researcher_id,
            'researcher_name': row['researcher_name'],
            'profile_h_index': profile_h_index,
            'atip_h_index': atip_h_index,
            'match': match,
            'difference': profile_h_index - atip_h_index
        })
    
    # Convert to DataFrame for easier analysis
    results_df = pd.DataFrame(comparison_results)
    
    # Summary statistics
    print("\n=== SUMMARY STATISTICS ===")
    print(f"Total researchers compared: {len(results_df)}")
    print(f"Matching h_index values: {results_df['match'].sum()}")
    print(f"Non-matching h_index values: {len(results_df) - results_df['match'].sum()}")
    print(f"Match percentage: {(results_df['match'].sum() / len(results_df) * 100):.2f}%")   
    # Distribution of differences
    print(f"\n=== DIFFERENCE STATISTICS ===")
    print(f"Mean difference (profile - atip): {results_df['difference'].mean():.2f}")
    print(f"Median difference: {results_df['difference'].median():.2f}")
    print(f"Standard deviation: {results_df['difference'].std():.2f}")
    print(f"Min difference: {results_df['difference'].min()}")
    print(f"Max difference: {results_df['difference'].max()}")    
    
    # Save detailed results to CSV
    output_file = './data/h_index_comparison.csv'
    results_df.to_csv(output_file, index=False)
    print(f"\nDetailed results saved to: {output_file}")
    
    return results_df

if __name__ == "__main__":
    results = compare_h_index_values()
