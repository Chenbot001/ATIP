#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ACL Track Distribution Analysis
===============================

This script analyses and prints the distribution of papers across different track themes
in the ACL25_ThemeData.csv dataset.

Author: GitHub Copilot
Date: June 8, 2025
"""

import pandas as pd
from collections import Counter

def analyze_track_distribution(csv_path):
    """
    Analyze and display the distribution of papers across different track themes.
    
    Args:
        csv_path (str): Path to the CSV file containing the track theme data
    """
    # Load the data
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Count papers in each track theme
    track_counts = df['Track Theme'].value_counts().reset_index()
    track_counts.columns = ['Track Theme', 'Number of Papers']
      # Print the results
    print("\nDistribution of papers across track themes:")
    print("=" * 50)
    
    # Sort by number of papers in descending order
    track_counts = track_counts.sort_values(by='Number of Papers', ascending=False)
    
    # Calculate total papers and percentages
    total_papers = track_counts['Number of Papers'].sum()
    track_counts['Percentage'] = (track_counts['Number of Papers'] / total_papers * 100).round(2)
    
    # Print formatted table with percentages
    print(f"{'Track Theme':<50} | {'Papers':<7} | {'Percentage':<10}")
    print("-" * 72)
    for _, row in track_counts.iterrows():
        print(f"{row['Track Theme']:<50} | {row['Number of Papers']:<7} | {row['Percentage']:<10}%")
    
    print("-" * 72)
    print(f"Total Papers: {total_papers}")
    
if __name__ == "__main__":
    # Path to data
    data_path = "../data/ACL25_ThemeData.csv"
    
    # Analyze track distribution
    analyze_track_distribution(data_path)
    analyze_track_distribution(data_path)
