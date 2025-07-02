"""
Advanced Researcher Name Completion Script

This script cleans and completes researcher names in the researcher profiles data
by matching with ACL Anthology author information through Semantic Scholar authorships.

The script identifies researchers with incomplete first names and attempts to complete them
using a sophisticated matching process that considers both last name consistency and
first name initial matching.

Matching criteria:
1. Last name must be identical (case-insensitive)
2. First name initial must match (case-insensitive)
3. Must find exactly one unique candidate to proceed with replacement

Author: AI Assistant
Date: 2025-07-01
"""

import pandas as pd
import os
import sys
from typing import Dict, List, Tuple, Optional
import re


def is_incomplete_first_name(first_name: str) -> bool:
    """
    Check if a first name is incomplete based on defined criteria.
    
    Args:
        first_name (str): The first name to check
        
    Returns:
        bool: True if the first name is incomplete, False otherwise
        
    Criteria:
        - Length <= 2 characters
        - Ends with '.'
        - Is None or empty
    """
    if not first_name or pd.isna(first_name):
        return True
    
    first_name = str(first_name).strip()
    
    if not first_name:
        return True
    
    # Check if length <= 2
    if len(first_name) <= 2:
        return True
    
    # Check if ends with '.'
    if first_name.endswith('.'):
        return True
    
    return False


def get_first_initial(name: str) -> str:
    """
    Get the first initial of a name (lowercase).
    
    Args:
        name (str): The name to extract initial from
        
    Returns:
        str: First initial in lowercase, or empty string if invalid
    """
    if not name or pd.isna(name):
        return ""
    
    name = str(name).strip()
    if not name:
        return ""
    
    return name[0].lower()


def load_data_files(acl_file: str, authorships_file: str, profiles_file: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load all required data files.
    
    Args:
        acl_file (str): Path to ACL researchers data file
        authorships_file (str): Path to authorships data file
        profiles_file (str): Path to researcher profiles data file
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: Loaded dataframes
    """
    try:
        print("Loading data files...")
        
        # Load ACL researchers data
        print(f"Loading ACL data from: {acl_file}")
        acl_df = pd.read_csv(acl_file, encoding='utf-8')
        print(f"✓ Loaded ACL data: {len(acl_df):,} records")
        
        # Load authorships data
        print(f"Loading authorships data from: {authorships_file}")
        authorships_df = pd.read_csv(authorships_file, encoding='utf-8')
        print(f"✓ Loaded authorships data: {len(authorships_df):,} records")
        
        # Load researcher profiles data
        print(f"Loading researcher profiles from: {profiles_file}")
        profiles_df = pd.read_csv(profiles_file, encoding='utf-8')
        print(f"✓ Loaded researcher profiles: {len(profiles_df):,} records")
        
        return acl_df, authorships_df, profiles_df
        
    except Exception as e:
        print(f"Error loading data files: {str(e)}")
        sys.exit(1)


def find_incomplete_researchers(profiles_df: pd.DataFrame) -> pd.DataFrame:
    """
    Find researchers with incomplete first names.
    
    Args:
        profiles_df (pd.DataFrame): Researcher profiles dataframe
        
    Returns:
        pd.DataFrame: Subset of researchers with incomplete first names
    """
    print("\nIdentifying researchers with incomplete first names...")
    
    # Apply the incomplete name check
    incomplete_mask = profiles_df['first_name'].apply(is_incomplete_first_name)
    incomplete_researchers = profiles_df[incomplete_mask].copy()
    
    print(f"Found {len(incomplete_researchers):,} researchers with incomplete first names")
    
    # Show some examples of incomplete names
    if len(incomplete_researchers) > 0:
        print("\nExamples of incomplete first names:")
        sample_size = min(10, len(incomplete_researchers))
        for i, (idx, row) in enumerate(incomplete_researchers.head(sample_size).iterrows()):
            first_name = row['first_name'] if pd.notna(row['first_name']) else 'None'
            print(f"  {i+1}. ID: {row['researcher_id']}, Name: '{first_name}' {row['last_name']}")
    
    return incomplete_researchers


def get_researcher_papers(researcher_id: str, authorships_df: pd.DataFrame) -> List[str]:
    """
    Get all paper IDs (DOIs) for a given researcher from authorships data.
    
    Args:
        researcher_id (str): The researcher ID to look up
        authorships_df (pd.DataFrame): Authorships dataframe
        
    Returns:
        List[str]: List of paper IDs (DOIs) for the researcher
    """
    # Convert researcher_id to ensure string matching
    researcher_id_str = str(researcher_id)
    
    # Filter authorships for this researcher
    researcher_papers = authorships_df[
        authorships_df['researcher_id'].astype(str) == researcher_id_str
    ]['paper_id'].tolist()
    
    return researcher_papers


def find_candidate_names(paper_ids: List[str], current_last_name: str, current_first_name: str, 
                        acl_df: pd.DataFrame) -> List[Tuple[str, str]]:
    """
    Find candidate (first_name, last_name) combinations from ACL data that match criteria.
    
    Args:
        paper_ids (List[str]): List of paper IDs (DOIs) to search in
        current_last_name (str): Current last name to match
        current_first_name (str): Current first name for initial matching
        acl_df (pd.DataFrame): ACL researchers dataframe
        
    Returns:
        List[Tuple[str, str]]: List of candidate (first_name, last_name) combinations
    """
    if not paper_ids:
        return []
    
    # Find all ACL records for these papers
    acl_records = acl_df[acl_df['paper_doi'].isin(paper_ids)]
    
    if len(acl_records) == 0:
        return []
    
    # Get current first initial for matching
    current_first_initial = get_first_initial(current_first_name)
    current_last_name_lower = str(current_last_name).strip().lower()
    
    candidates = []
    
    for _, row in acl_records.iterrows():
        acl_first_name = str(row['first_name']).strip() if pd.notna(row['first_name']) else ''
        acl_last_name = str(row['last_name']).strip() if pd.notna(row['last_name']) else ''
        
        # Skip if either name is empty
        if not acl_first_name or not acl_last_name:
            continue
        
        # Check last name match (case-insensitive)
        if acl_last_name.lower() != current_last_name_lower:
            continue
        
        # Check first name initial match (case-insensitive)
        acl_first_initial = get_first_initial(acl_first_name)
        if current_first_initial and acl_first_initial != current_first_initial:
            continue
        
        # Add to candidates
        candidates.append((acl_first_name, acl_last_name))
    
    # Return unique candidates
    unique_candidates = list(set(candidates))
    return unique_candidates


def complete_researcher_name(researcher_id: str, current_first_name: str, current_last_name: str,
                           authorships_df: pd.DataFrame, acl_df: pd.DataFrame) -> Optional[Tuple[str, str]]:
    """
    Attempt to complete a researcher's name using ACL data with advanced matching.
    
    Args:
        researcher_id (str): The researcher ID to complete
        current_first_name (str): Current first name from profiles
        current_last_name (str): Current last name from profiles
        authorships_df (pd.DataFrame): Authorships dataframe
        acl_df (pd.DataFrame): ACL researchers dataframe
        
    Returns:
        Optional[Tuple[str, str]]: (first_name, last_name) if exactly one match found, None otherwise
    """
    # Convert researcher_id to string for comparison
    researcher_id_str = str(researcher_id)
    
    # Get papers for this researcher
    paper_ids = get_researcher_papers(researcher_id_str, authorships_df)
    
    if not paper_ids:
        return None
    
    # Find candidate names from ACL data
    candidates = find_candidate_names(paper_ids, current_last_name, current_first_name, acl_df)
    
    # Return the candidate only if exactly one unique combination is found
    if len(candidates) == 1:
        return candidates[0]
    
    return None


def process_name_completion(profiles_df: pd.DataFrame, authorships_df: pd.DataFrame, 
                          acl_df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Process name completion for all researchers with incomplete names.
    
    Args:
        profiles_df (pd.DataFrame): Researcher profiles dataframe
        authorships_df (pd.DataFrame): Authorships dataframe
        acl_df (pd.DataFrame): ACL researchers dataframe
        
    Returns:
        Tuple[pd.DataFrame, int]: Updated profiles dataframe and count of completed names
    """
    print("\n" + "="*60)
    print("STARTING NAME COMPLETION PROCESS")
    print("="*60)
    
    # Create a copy of the profiles dataframe
    updated_profiles = profiles_df.copy()
    
    # Find researchers with incomplete first names
    incomplete_researchers = find_incomplete_researchers(profiles_df)
    
    if len(incomplete_researchers) == 0:
        print("No incomplete researchers found. Nothing to process.")
        return updated_profiles, 0
    
    completed_count = 0
    processed_count = 0
    
    print(f"\nProcessing name completion for {len(incomplete_researchers):,} researchers...")
    print("This may take a while...\n")
    
    for idx, row in incomplete_researchers.iterrows():
        processed_count += 1
        
        researcher_id = row['researcher_id']
        current_first_name = str(row['first_name']) if pd.notna(row['first_name']) else ''
        current_last_name = str(row['last_name']) if pd.notna(row['last_name']) else ''
        
        # Attempt to complete the name
        completed_name = complete_researcher_name(
            researcher_id, current_first_name, current_last_name, 
            authorships_df, acl_df
        )
        
        if completed_name:
            new_first_name, new_last_name = completed_name
            
            # Update the dataframe
            updated_profiles.loc[idx, 'first_name'] = new_first_name
            updated_profiles.loc[idx, 'last_name'] = new_last_name
            
            completed_count += 1
            
            print(f"✓ [{completed_count:>4}] {current_first_name} {current_last_name} → {new_first_name} {new_last_name}")
        
        # Show progress every 1000 records
        if processed_count % 1000 == 0:
            completion_rate = (completed_count / processed_count) * 100
            print(f"Progress: {processed_count:,}/{len(incomplete_researchers):,} processed, {completed_count:,} completed ({completion_rate:.1f}%)")
    
    print(f"\n" + "="*60)
    print(f"NAME COMPLETION FINISHED")
    print(f"Total processed: {processed_count:,}")
    print(f"Successfully completed: {completed_count:,}")
    print(f"Success rate: {(completed_count/processed_count)*100:.1f}%")
    print("="*60)
    
    return updated_profiles, completed_count


def save_results(updated_profiles: pd.DataFrame, output_file: str):
    """
    Save the updated researcher profiles to a CSV file.
    
    Args:
        updated_profiles (pd.DataFrame): Updated profiles dataframe
        output_file (str): Output file path
    """
    try:
        print(f"\nSaving results to: {output_file}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save to CSV with UTF-8 encoding
        updated_profiles.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✓ Results successfully saved!")
        print(f"  - Total records: {len(updated_profiles):,}")
        print(f"  - File size: {os.path.getsize(output_file) / 1024 / 1024:.1f} MB")
        
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")
        sys.exit(1)


def print_detailed_statistics(original_profiles: pd.DataFrame, updated_profiles: pd.DataFrame, completed_count: int):
    """
    Print detailed statistics about the name completion process.
    
    Args:
        original_profiles (pd.DataFrame): Original profiles dataframe
        updated_profiles (pd.DataFrame): Updated profiles dataframe
        completed_count (int): Number of names completed
    """
    print("\n" + "="*60)
    print("DETAILED COMPLETION STATISTICS")
    print("="*60)
    
    # Count incomplete names before and after
    original_incomplete = sum(original_profiles['first_name'].apply(is_incomplete_first_name))
    updated_incomplete = sum(updated_profiles['first_name'].apply(is_incomplete_first_name))
    
    print(f"Total researchers in dataset: {len(original_profiles):,}")
    print(f"Originally incomplete first names: {original_incomplete:,}")
    print(f"Successfully completed names: {completed_count:,}")
    print(f"Remaining incomplete names: {updated_incomplete:,}")
    print(f"Overall completion rate: {(completed_count/original_incomplete)*100:.1f}%")
    print(f"Dataset improvement: {((original_incomplete - updated_incomplete)/original_incomplete)*100:.1f}%")
    
    print(f"\n" + "-"*40)
    print("SAMPLE OF COMPLETED NAMES")
    print("-"*40)
    
    # Find examples of completed names
    sample_count = 0
    max_samples = 10
    
    for idx, row in updated_profiles.iterrows():
        if sample_count >= max_samples:
            break
            
        original_first = original_profiles.loc[idx, 'first_name']
        updated_first = row['first_name']
        
        if str(original_first) != str(updated_first) and is_incomplete_first_name(original_first):
            sample_count += 1
            original_display = original_first if pd.notna(original_first) else 'None'
            print(f"  {sample_count:2d}. {original_display} {row['last_name']} → {updated_first} {row['last_name']}")
    
    if sample_count == 0:
        print("  No completed names to display.")
    
    print("="*60)


def validate_data_consistency(acl_df: pd.DataFrame, authorships_df: pd.DataFrame, profiles_df: pd.DataFrame):
    """
    Validate data consistency across the three datasets.
    
    Args:
        acl_df (pd.DataFrame): ACL researchers dataframe
        authorships_df (pd.DataFrame): Authorships dataframe
        profiles_df (pd.DataFrame): Profiles dataframe
    """
    print("\n" + "-"*40)
    print("DATA VALIDATION")
    print("-"*40)
    
    # Check for overlapping DOIs/paper_ids
    acl_dois = set(acl_df['paper_doi'].dropna().astype(str))
    authorship_papers = set(authorships_df['paper_id'].dropna().astype(str))
    
    overlap = len(acl_dois.intersection(authorship_papers))
    print(f"ACL papers: {len(acl_dois):,}")
    print(f"Authorship papers: {len(authorship_papers):,}")
    print(f"Overlapping papers: {overlap:,}")
    print(f"Overlap rate: {(overlap/len(acl_dois))*100:.1f}% (ACL coverage)")
    
    # Check researcher ID ranges
    profile_researchers = set(profiles_df['researcher_id'].dropna().astype(str))
    authorship_researchers = set(authorships_df['researcher_id'].dropna().astype(str))
    
    researcher_overlap = len(profile_researchers.intersection(authorship_researchers))
    print(f"Profile researchers: {len(profile_researchers):,}")
    print(f"Authorship researchers: {len(authorship_researchers):,}")
    print(f"Overlapping researchers: {researcher_overlap:,}")
    print(f"Researcher overlap rate: {(researcher_overlap/len(profile_researchers))*100:.1f}%")


def main():
    """
    Main function to run the advanced researcher name completion process.
    """
    print("🔍 Advanced Researcher Name Completion Script")
    print("=" * 50)
    
    # File paths
    acl_file = "./data/researchers_data_with_paper.csv"
    authorships_file = "./data/authorships.csv"
    profiles_file = "./data/researcher_profiles.csv"
    output_file = "./data/researchers_profiles_cleaned2.csv"
    
    # Check if all input files exist
    for file_path in [acl_file, authorships_file, profiles_file]:
        if not os.path.exists(file_path):
            print(f"❌ Error: Required file not found: {file_path}")
            sys.exit(1)
    
    # Load data files
    acl_df, authorships_df, profiles_df = load_data_files(acl_file, authorships_file, profiles_file)
    
    # Validate data consistency
    validate_data_consistency(acl_df, authorships_df, profiles_df)
    
    # Keep a copy of original data for statistics
    original_profiles = profiles_df.copy()
    
    # Process name completion
    updated_profiles, completed_count = process_name_completion(profiles_df, authorships_df, acl_df)
    
    # Save results
    save_results(updated_profiles, output_file)
    
    # Print detailed statistics
    print_detailed_statistics(original_profiles, updated_profiles, completed_count)
    
    print(f"\n🎉 Script completed successfully!")
    print(f"📁 Updated data saved to: {output_file}")
    print(f"📊 {completed_count:,} researcher names were successfully completed!")


if __name__ == "__main__":
    main()
