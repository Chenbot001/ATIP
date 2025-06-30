#!/usr/bin/env python3
"""
Track Distribution Calculator

This script calculates the distribution of tracks across:
1. All papers (with titles)
2. Papers with available abstracts

Input CSV should have columns: 'Track Theme', 'Title', 'Abstract'
"""

import pandas as pd
import argparse
import sys
from pathlib import Path


def calculate_track_distribution(csv_path):
    """
    Calculate track distribution from CSV file.
    
    Args:
        csv_path (str): Path to the CSV file
        
    Returns:
        dict: Dictionary containing distribution statistics
    """
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Check if required columns exist
        required_columns = ['Track Theme', 'Title', 'Abstract']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Clean the data
        df = df.dropna(subset=['Title'])  # Remove rows without titles
        df['Track Theme'] = df['Track Theme'].fillna('Unknown')  # Fill missing track themes
        
        # Calculate distributions
        total_papers = len(df)
        papers_with_abstracts = df['Abstract'].notna().sum()
        
        # Track distribution for all papers
        all_tracks_dist = df['Track Theme'].value_counts()
        
        # Track distribution for papers with abstracts
        papers_with_abstracts_df = df[df['Abstract'].notna()]
        abstracts_tracks_dist = papers_with_abstracts_df['Track Theme'].value_counts()
        
        # Calculate percentages
        all_tracks_percentage = (all_tracks_dist / total_papers * 100).round(2)
        abstracts_tracks_percentage = (abstracts_tracks_dist / papers_with_abstracts * 100).round(2)
        
        return {
            'total_papers': total_papers,
            'papers_with_abstracts': papers_with_abstracts,
            'all_tracks_distribution': all_tracks_dist,
            'abstracts_tracks_distribution': abstracts_tracks_dist,
            'all_tracks_percentage': all_tracks_percentage,
            'abstracts_tracks_percentage': abstracts_tracks_percentage
        }
        
    except FileNotFoundError:
        print(f"Error: File '{csv_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)


def print_distribution_results(results):
    """
    Print the distribution results in a formatted way.
    
    Args:
        results (dict): Results from calculate_track_distribution
    """
    print("=" * 80)
    print("TRACK DISTRIBUTION ANALYSIS")
    print("=" * 80)
    
    print(f"\n📊 OVERVIEW:")
    print(f"   Total papers: {results['total_papers']:,}")
    print(f"   Papers with abstracts: {results['papers_with_abstracts']:,}")
    print(f"   Papers without abstracts: {results['total_papers'] - results['papers_with_abstracts']:,}")
    
    print(f"\n📈 TRACK DISTRIBUTION - ALL PAPERS:")
    print("-" * 50)
    print(f"{'Track Theme':<40} {'Count':<10} {'Percentage':<10}")
    print("-" * 50)
    
    for track, count in results['all_tracks_distribution'].items():
        percentage = results['all_tracks_percentage'][track]
        print(f"{track:<40} {count:<10} {percentage:<10.2f}%")
    
    print(f"\n📈 TRACK DISTRIBUTION - PAPERS WITH ABSTRACTS:")
    print("-" * 50)
    print(f"{'Track Theme':<40} {'Count':<10} {'Percentage':<10}")
    print("-" * 50)
    
    for track, count in results['abstracts_tracks_distribution'].items():
        percentage = results['abstracts_tracks_percentage'][track]
        print(f"{track:<40} {count:<10} {percentage:<10.2f}%")
    
    print("\n" + "=" * 80)


def save_results_to_csv(results, output_path):
    """
    Save the distribution results to CSV files.
    
    Args:
        results (dict): Results from calculate_track_distribution
        output_path (str): Base path for output files
    """
    # Create output directory if it doesn't exist
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save all papers distribution
    all_papers_df = pd.DataFrame({
        'Track_Theme': results['all_tracks_distribution'].index,
        'Count': results['all_tracks_distribution'].values,
        'Percentage': results['all_tracks_percentage'].values
    })
    all_papers_path = f"{output_path}_all_papers.csv"
    all_papers_df.to_csv(all_papers_path, index=False)
    print(f"📄 All papers distribution saved to: {all_papers_path}")
    
    # Save abstracts distribution
    abstracts_df = pd.DataFrame({
        'Track_Theme': results['abstracts_tracks_distribution'].index,
        'Count': results['abstracts_tracks_distribution'].values,
        'Percentage': results['abstracts_tracks_percentage'].values
    })
    abstracts_path = f"{output_path}_with_abstracts.csv"
    abstracts_df.to_csv(abstracts_path, index=False)
    print(f"📄 Papers with abstracts distribution saved to: {abstracts_path}")


def main():
    csv_file = "C:\\Eric\\Projects\\AI_Researcher_Network\\data\\ACL25_ThemeData_abs.csv"
    
    # Calculate distribution
    print(f"🔍 Analyzing track distribution from: {csv_file}")
    results = calculate_track_distribution(csv_file)
    
    # Print results
    print_distribution_results(results)
    
    # Save results if requested
    # if not args.no_save:
    #     save_results_to_csv(results, args.output)


if __name__ == "__main__":
    main()
