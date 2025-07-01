#!/usr/bin/env python3
"""
Script to convert corpus_id column from float to integer in paper_info.csv
"""

import pandas as pd
import numpy as np
import os

def convert_corpus_id_to_int():
    """
    Convert corpus_id column from float to integer in paper_info.csv
    """
    # File paths
    input_file = "data/paper_info.csv"
    output_file = "data/paper_info.csv"  # Overwrite the original file
    
    print(f"Reading {input_file}...")
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    print(f"Original data types:")
    print(df.dtypes)
    print(f"\nOriginal corpus_id sample values:")
    print(df['corpus_id'].head())
    
    # Check for any NaN values in corpus_id column
    nan_count = df['corpus_id'].isna().sum()
    if nan_count > 0:
        print(f"\nWarning: Found {nan_count} NaN values in corpus_id column")
        print("These will be converted to 0 or you may want to handle them differently")
    
    # Convert corpus_id from float to int
    # First fill NaN values with 0 (or you can choose another approach)
    df['corpus_id'] = df['corpus_id'].fillna(0)
    
    # Convert to integer
    df['corpus_id'] = df['corpus_id'].astype(int)
    
    print(f"\nAfter conversion:")
    print(f"New data types:")
    print(df.dtypes)
    print(f"\nNew corpus_id sample values:")
    print(df['corpus_id'].head())
    
    # Check 1: Determine if any corpus_id equals 0
    zero_count = (df['corpus_id'] == 0).sum()
    print(f"\nCheck 1 - Zero values in corpus_id:")
    print(f"Number of rows with corpus_id = 0: {zero_count}")
    if zero_count > 0:
        print(f"Percentage of zero values: {(zero_count / len(df)) * 100:.2f}%")
        print("Sample rows with corpus_id = 0:")
        print(df[df['corpus_id'] == 0][['corpus_id']].head())
    
    # Check 2: Determine if corpus_id contains duplicates
    duplicate_count = df['corpus_id'].duplicated().sum()
    unique_count = df['corpus_id'].nunique()
    total_count = len(df)
    
    print(f"\nCheck 2 - Duplicate values in corpus_id:")
    print(f"Total rows: {total_count}")
    print(f"Unique corpus_id values: {unique_count}")
    print(f"Duplicate rows: {duplicate_count}")
    if duplicate_count > 0:
        print(f"Percentage of duplicates: {(duplicate_count / total_count) * 100:.2f}%")
        print("Sample duplicate corpus_id values:")
        duplicates = df[df['corpus_id'].duplicated(keep=False)].sort_values('corpus_id')
        print(duplicates[['corpus_id']].head(10))
    else:
        print("No duplicate corpus_id values found.")
    
    # Save the updated file
    print(f"\nSaving updated file to {output_file}...")
    df.to_csv(output_file, index=False)
    
    print("Conversion completed successfully!")
    
    # Verify the conversion
    print(f"\nVerification - reading the file back:")
    df_verify = pd.read_csv(output_file)
    print(f"corpus_id dtype: {df_verify['corpus_id'].dtype}")


if __name__ == "__main__":
    convert_corpus_id_to_int() 