#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ACL Track Distribution Analysis
===============================

This script analyses and visualizes the distribution of papers across different track themes
in the ACL25_ThemeData.csv dataset.

Author: Eric Chen & GitHub Copilot
Date: June 8, 2025
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
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
    
    # Visualize the distribution
    plot_distribution(track_counts)
    
def plot_distribution(track_counts):
    """
    Create a horizontal bar chart of track distribution.
    
    Args:
        track_counts (DataFrame): DataFrame containing track counts
    """
    plt.figure(figsize=(14, 10))
    
    # Only show top 30 categories if there are many categories
    if len(track_counts) > 30:
        plot_data = track_counts.head(30).copy()
        title_suffix = " (Top 30 Tracks)"
    else:
        plot_data = track_counts.copy()
        title_suffix = ""
    
    # Create horizontal bar chart
    sns.set_style("whitegrid")
    ax = sns.barplot(
        y='Track Theme', 
        x='Number of Papers', 
        data=plot_data,
        palette='viridis'
    )
    
    # Add labels and title
    plt.title(f'Distribution of Papers Across ACL Track Themes{title_suffix}', fontsize=16)
    plt.xlabel('Number of Papers', fontsize=12)
    plt.ylabel('Track Theme', fontsize=12)
    
    # Add count and percentage labels to bars
    for i, row in enumerate(plot_data.itertuples()):
        ax.text(row._2 + 0.3, i, f"{row._2} ({row.Percentage}%)", va='center')
    
    # Ensure output directory exists
    os.makedirs('../visualizations', exist_ok=True)
    
    # Save the figure
    plt.tight_layout()
    output_path = 'C:\\Eric\\Projects\\AI_Researcher_Network\\visualizations\\track_distribution.png'
    plt.savefig(output_path)
    print(f"\nVisualization saved to {output_path}")
    
if __name__ == "__main__":
    # Path to data
    data_path = "C:\\Eric\\Projects\\AI_Researcher_Network\\data\\ACL25_ThemeData.csv"
    
    # Analyze track distribution
    analyze_track_distribution(data_path)
