#!/usr/bin/env python3
"""
Script to analyze the column structure of CSV files in the data folder.
This helps understand the structure of large CSV files without loading them entirely.
"""

import os
import pandas as pd
import csv
from pathlib import Path

def analyze_csv_structure(csv_file_path):
    """
    Analyze the structure of a CSV file and return column information.
    
    Args:
        csv_file_path (str): Path to the CSV file
        
    Returns:
        dict: Dictionary containing file info and column structure
    """
    file_info = {
        'file_name': os.path.basename(csv_file_path),
        'file_size_mb': round(os.path.getsize(csv_file_path) / (1024 * 1024), 2),
        'columns': [],
        'total_rows': 0
    }
    
    try:
        # Read just the header to get column names
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            file_info['columns'] = header
            
            # Count total rows (excluding header)
            row_count = sum(1 for row in reader)
            file_info['total_rows'] = row_count
            
    except Exception as e:
        file_info['error'] = str(e)
    
    return file_info

def main():
    """Main function to analyze all CSV files in the data folder."""
    
    # Define paths
    data_folder = Path("./data")
    output_file = Path("./data/data_structure_analysis.txt")
    
    # Ensure data folder exists
    if not data_folder.exists():
        print(f"Data folder not found: {data_folder}")
        return
    
    # Find all CSV files
    csv_files = list(data_folder.glob("*.csv"))
    
    if not csv_files:
        print("No CSV files found in the data folder.")
        return
    
    print(f"Found {len(csv_files)} CSV files to analyze...")
    
    # Analyze each CSV file
    results = []
    for csv_file in csv_files:
        print(f"Analyzing: {csv_file.name}")
        result = analyze_csv_structure(csv_file)
        results.append(result)
    
    # Write results to text file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("CSV FILES STRUCTURE ANALYSIS\n")
        f.write("=" * 50 + "\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"{i}. FILE: {result['file_name']}\n")
            f.write(f"   Size: {result['file_size_mb']} MB\n")
            f.write(f"   Total Rows: {result['total_rows']:,}\n")
            f.write(f"   Columns ({len(result['columns'])}):\n")
            
            for j, col in enumerate(result['columns'], 1):
                f.write(f"     {j:2d}. {col}\n")
            
            if 'error' in result:
                f.write(f"   ERROR: {result['error']}\n")
            
            f.write("\n" + "-" * 50 + "\n\n")
    
    print(f"Analysis complete! Results written to: {output_file}")
    print(f"Analyzed {len(results)} CSV files.")

if __name__ == "__main__":
    main() 