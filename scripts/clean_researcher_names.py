#!/usr/bin/env python
"""
Research Name Cleaner

This script cleans and standardizes researcher names in profiles by matching against
more accurate name data from ACL Anthology.

It matches researchers based on matching last name and first name initial,
then replaces incomplete or abbreviated names with complete ones.
"""

import os
import pandas as pd
import time

def load_data(data_dir):
    """
    Load the researcher data from CSV files.
    
    Args:
        data_dir (str): Directory containing the CSV files
        
    Returns:
        tuple: Tuple containing three DataFrames (researchers_data, researchers_profiles, authorships)
    """
    researchers_data_path = os.path.join(data_dir, 'researchers_data.csv')
    researchers_profiles_path = os.path.join(data_dir, 'researcher_profiles.csv')
    authorships_path = os.path.join(data_dir, 'authorships.csv')
    
    print(f"Loading data from {data_dir}...")
    
    # Check if files exist
    for path in [researchers_data_path, researchers_profiles_path, authorships_path]:
        if not os.path.exists(path):
            print(f"Warning: File {path} does not exist")
    
    # Load the data
    researchers_data = pd.read_csv(researchers_data_path)
    researchers_profiles = pd.read_csv(researchers_profiles_path)
    authorships = pd.read_csv(authorships_path) if os.path.exists(authorships_path) else None
    
    print(f"Loaded {len(researchers_data)} records from researchers_data.csv")
    print(f"Loaded {len(researchers_profiles)} records from researcher_profiles.csv")
    
    return researchers_data, researchers_profiles, authorships

def preprocess_names(df):
    """
    Preprocess names by extracting first letter of first name.
    
    Args:
        df (pd.DataFrame): DataFrame containing first_name and last_name columns
        
    Returns:
        pd.DataFrame: DataFrame with added first_initial column
    """
    df = df.copy()
    
    # Convert names to strings to handle any non-string values
    df['first_name'] = df['first_name'].astype(str)
    df['last_name'] = df['last_name'].astype(str)
    
    # Strip whitespaces
    df['first_name'] = df['first_name'].str.strip()
    df['last_name'] = df['last_name'].str.strip()
    
    # Extract first initial
    df['first_initial'] = df['first_name'].str[0:1].str.upper()
    
    return df

def is_abbreviated_name(first_name):
    """
    Check if a first name is abbreviated and needs correction.
    
    Args:
        first_name (str): First name to check
        
    Returns:
        bool: True if the name is abbreviated, False otherwise
    """
    if not first_name or first_name == 'nan':
        return False
    
    # Check if name is abbreviated: length <= 2 or ends with '.'
    return len(first_name) <= 2 or first_name.endswith('.')

def create_name_lookup(researchers_data):
    """
    Create a lookup dictionary for efficient matching.
    Groups researchers by (last_name_lower, first_initial) for fast lookup.
    
    Args:
        researchers_data (pd.DataFrame): DataFrame with researcher data from ACL
        
    Returns:
        dict: Dictionary mapping (last_name_lower, first_initial) to list of candidate names
    """
    name_lookup = {}
    
    for _, row in researchers_data.iterrows():
        last_name_lower = row['last_name'].lower().strip()
        first_initial = row['first_initial'].upper() if row['first_initial'] else ""
        key = (last_name_lower, first_initial)
        
        if key not in name_lookup:
            name_lookup[key] = []
        
        # Add candidate to list
        candidate = {
            'first_name': row['first_name'].strip(),
            'last_name': row['last_name'].strip()
        }
        
        # Avoid duplicates in the same group
        if candidate not in name_lookup[key]:
            name_lookup[key].append(candidate)
    
    return name_lookup

def match_and_clean_names(researchers_profiles, name_lookup):
    """
    Match researcher profiles with more complete names and update them.
    Only updates names that are abbreviated and have exactly one match.
    
    Args:
        researchers_profiles (pd.DataFrame): DataFrame with researcher profiles
        name_lookup (dict): Lookup dictionary for name matching
        
    Returns:
        tuple: (updated_dataframe, stats_dict)
    """
    updated_profiles = researchers_profiles.copy()
    
    # Statistics tracking
    stats = {
        'total_records': len(researchers_profiles),
        'abbreviated_names': 0,
        'updated_names': 0,
        'skipped_multiple_matches': 0,
        'skipped_no_matches': 0,
        'skipped_already_full': 0
    }
    
    for i, row in updated_profiles.iterrows():
        current_first_name = row['first_name']
        current_last_name = row['last_name']
        
        # Check if first name is abbreviated
        if not is_abbreviated_name(current_first_name):
            stats['skipped_already_full'] += 1
            continue
        
        stats['abbreviated_names'] += 1
        
        # Create lookup key
        last_name_lower = current_last_name.lower().strip()
        first_initial = row['first_initial'].upper() if row['first_initial'] else ""
        key = (last_name_lower, first_initial)
        
        # Look for matches
        if key in name_lookup:
            candidates = name_lookup[key]
            
            if len(candidates) == 1:
                # Exactly one match - update the name
                match = candidates[0]
                updated_profiles.at[i, 'first_name'] = match['first_name']
                updated_profiles.at[i, 'last_name'] = match['last_name']
                stats['updated_names'] += 1
            else:
                # Multiple matches - skip
                stats['skipped_multiple_matches'] += 1
        else:
            # No matches found - skip
            stats['skipped_no_matches'] += 1
    
    return updated_profiles, stats

def main():
    """
    Main function to orchestrate the name cleaning process.
    """
    start_time = time.time()
    
    # Paths
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    output_path = os.path.join(data_dir, 'researchers_profiles_cleaned.csv')
    
    print("=== ACL Anthology Name Cleaner ===")
    print("This script fixes abbreviated names in researcher profiles using ACL Anthology data.\n")
    
    # Load data
    researchers_data, researchers_profiles, _ = load_data(data_dir)
    
    # Preprocess names
    print("Preprocessing names...")
    researchers_data = preprocess_names(researchers_data)
    researchers_profiles = preprocess_names(researchers_profiles)
    
    # Create lookup dictionary
    print("Creating name lookup dictionary...")
    name_lookup = create_name_lookup(researchers_data)
    print(f"Created lookup for {len(name_lookup)} unique (last_name, first_initial) combinations")
    
    # Match and clean names
    print("Matching and cleaning researcher names...")
    cleaned_profiles, stats = match_and_clean_names(researchers_profiles, name_lookup)
    
    # Remove the temporary column
    cleaned_profiles = cleaned_profiles.drop('first_initial', axis=1)
    
    # Save the results
    cleaned_profiles.to_csv(output_path, index=False)
    
    # Print detailed statistics
    print("\n=== Processing Results ===")
    print(f"Total records processed: {stats['total_records']}")
    print(f"Records with abbreviated names: {stats['abbreviated_names']}")
    print(f"Names successfully updated: {stats['updated_names']}")
    print(f"Skipped (multiple matches): {stats['skipped_multiple_matches']}")
    print(f"Skipped (no matches found): {stats['skipped_no_matches']}")
    print(f"Skipped (already full names): {stats['skipped_already_full']}")
    
    if stats['abbreviated_names'] > 0:
        success_rate = (stats['updated_names'] / stats['abbreviated_names']) * 100
        print(f"Success rate for abbreviated names: {success_rate:.1f}%")
    
    print(f"\nResults saved to: {output_path}")
    print(f"Process completed in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
