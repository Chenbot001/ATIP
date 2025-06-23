"""
ACL Anthology Researcher Information Extractor

This script extracts researcher information from the ACL Anthology and saves it to a CSV file.
It processes researchers from specified collections, generates unique researcher IDs,
and includes placeholders for external IDs like OpenReview and Google Scholar.

The script uses the ACL Anthology API to access author data and pandas for efficient
data manipulation and storage.

Usage:
    python researcher_table.py [--collection COLLECTION_ID] [--all-collections]

Requirements:
    - acl_anthology library
    - pandas
    - Python 3.6+
"""

import os
import sys
import hashlib
import re
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from acl_anthology import Anthology
from acl_anthology.people.name import Name

def generate_unique_researcher_id(first_name, last_name):
    """
    Generate a unique researcher ID based on name.
    
    Args:
        first_name (str): Researcher's first name
        last_name (str): Researcher's last name
        affiliation (str, optional): Not used in ID generation, kept for backward compatibility
        
    Returns:
        str: A unique researcher ID
        generate_unique_researcher_id 函数创建唯一标识符的逻辑如下：

        输入标准化：
        首先将 first_name 和 last_name 转换为小写并去除前后空格
        这样可以确保相同名字的不同大小写或格式都会生成相同的 ID 基础
        
        创建基础标识符：
        基本标识符是 first_name_last_name 格式
        这个基础标识符用于区分同名但不同机构的研究者
        
        创建唯一哈希：
        使用 MD5 哈希算法对基础标识符进行处理，生成 32 位哈希值
        取这个哈希值的前 6 个字符作为唯一后缀
        使用哈希是为了处理可能的名字冲突，让相同名字的不同人也能获得不同 ID
        
        组合最终 ID：
        最终的 ID 格式为：r_姓_名首字母_哈希后缀
        例如：r_smith_j_a1b2c3
        这种格式既包含可读的名字成分，又通过哈希后缀确保唯一性
        
        净化 ID：
        最后使用正则表达式移除所有非字母数字字符和下划线
        确保生成的 ID 只包含字母、数字和下划线，便于在系统中使用
    """
    # Standardize names to avoid case and space issues
    first_name = first_name.strip().lower() if first_name else ""
    last_name = last_name.strip().lower() if last_name else ""
    
    if not first_name and not last_name:
        return None
    
    # Create an identifier string (without affiliation)
    identifier = f"{first_name}_{last_name}"
    
    # Use MD5 hash to generate a unique suffix
    hash_suffix = hashlib.md5(identifier.encode('utf-8')).hexdigest()[:6]
    
    # Combine into final ID format
    researcher_id = f"r_{last_name}_{first_name[0]}_{hash_suffix}"
    
    # Remove non-alphanumeric characters
    researcher_id = re.sub(r'[^a-z0-9_]', '', researcher_id)
    
    return researcher_id

def save_researchers_to_csv(researchers_df, csv_file='data/researchers_data.csv'):
    """
    Save a DataFrame of researcher information to a CSV file.
    
    Args:
        researchers_df (pd.DataFrame): DataFrame containing researcher information.
        csv_file (str, optional): Path to the output CSV file.
        
    Returns:
        None
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    
    # Save the DataFrame to CSV, overwriting any existing file
    researchers_df.to_csv(csv_file, mode='w', header=True, index=False, encoding='utf-8')
    print(f"Data saved to {csv_file}")

def process_author(author):
    """
    Process a single author and extract their information.
    
    Args:
        author: An author object from ACL Anthology
        
    Returns:
        dict: Dictionary containing author information
    """
    try:
        name = Name.from_(author.name)
        first_name = name.first if name.first else ''
        last_name = name.last
        affiliation = author.affiliation if hasattr(author, 'affiliation') else None
        
        # Generate a custom researcher ID
        researcher_id = generate_unique_researcher_id(first_name, last_name)
        
        # External IDs are set to None as placeholders
        openreview_id = None
        google_scholar_id = None
        
        return {
            'researcher_id': researcher_id,
            'first_name': first_name,
            'last_name': last_name,
            'openreview_id': openreview_id,
            'google_scholar_id': google_scholar_id
        }
    except Exception as e:
        print(f"Error processing author {author.name}: {str(e)}")
        return None

def search_collection(anthology, collection_id):
    """
    Extract researcher information from a specific collection.
    
    Args:
        anthology (Anthology): Anthology instance to use for searching
        collection_id (str): ID of the collection to search
        
    Returns:
        pd.DataFrame: DataFrame containing researcher information
    """
    collection = anthology.get(collection_id)
    all_authors = set()  # Set of unique author objects
    author_data = []  # List to store processed author data
    
    print(f"Analyzing collection: {collection_id}")
    
    # Collect all unique authors from the collection
    for volume in collection.volumes():
        for paper in volume.papers():
            for author in paper.authors:
                all_authors.add(author)
    
    print(f"Found {len(all_authors)} unique authors in collection {collection_id}")
    
    # Process authors in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_author, all_authors))
    
    # Filter out None results and add valid results to author_data
    author_data = [result for result in results if result is not None]
    
    # Create DataFrame from author data
    researchers_df = pd.DataFrame(author_data)
    
    return researchers_df

def process_collections(anthology, collection_ids, output_file):
    """
    Process multiple collections and extract researcher information.
    
    Args:
        anthology (Anthology): Anthology instance to use for searching
        collection_ids (list): List of collection IDs to process
        output_file (str): Path to the output CSV file
        
    Returns:
        pd.DataFrame: DataFrame containing all researcher information
    """
    # Initialize an empty DataFrame to store all researcher data
    all_researchers_df = pd.DataFrame()
    
    # Process each collection
    for i, collection_id in enumerate(collection_ids):
        print(f"\nProcessing collection [{i+1}/{len(collection_ids)}]: {collection_id}")
        
        try:
            # Extract researcher data from the current collection
            researchers_df = search_collection(anthology, collection_id)
            
            # Append to all_researchers_df
            if all_researchers_df.empty:
                all_researchers_df = researchers_df
            else:
                all_researchers_df = pd.concat([all_researchers_df, researchers_df], ignore_index=True)
            
            # Save intermediate results periodically
            if (i + 1) % 5 == 0 or (i + 1) == len(collection_ids):
                # Remove duplicate researchers based on researcher_id
                all_researchers_df = all_researchers_df.drop_duplicates(subset=['researcher_id'])
                save_researchers_to_csv(all_researchers_df, output_file)
                print(f"Saved intermediate results, processed {i+1}/{len(collection_ids)} collections")
                
        except Exception as e:
            print(f"Error processing collection {collection_id}: {str(e)}")
            continue
    
    # Final deduplication
    all_researchers_df = all_researchers_df.drop_duplicates(subset=['researcher_id'])
    
    return all_researchers_df

def main():
    """
    Main function to run the researcher extraction process.
    """
    import argparse
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Extract researcher data from ACL Anthology')
    parser.add_argument('--collection', type=str, default="2024.acl", 
                        help='ACL collection ID to process (default: 2024.acl)')
    parser.add_argument('--output', type=str, default="data/researchers_data.csv",
                        help='Output CSV file path (default: data/researchers_data.csv)')
    parser.add_argument('--collections-file', type=str, default="data/acl_collections.txt",
                        help='File containing multiple collection IDs')
    parser.add_argument('--all-collections', action='store_true',
                        help='Process all collections in collections-file')
    args = parser.parse_args()
    
    # Start timing
    start_time = time.time()
    print(f"Starting process at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize anthology
        try:
            anthology = Anthology.from_repo()
            print("Using local anthology repository")
        except Exception as e:
            print(f"Error initializing local anthology: {e}")
            print("Trying online repository...")
            try:
                anthology = Anthology.from_url()
                print("Using online anthology repository")
            except Exception as e2:
                print(f"Cannot initialize anthology: {e2}")
                sys.exit(1)
        
        # Determine which collections to process
        if args.all_collections:
            # Read collection IDs from file
            try:
                with open(args.collections_file, 'r') as f:
                    collection_ids = [line.strip() for line in f if line.strip()]
                print(f"Read {len(collection_ids)} collections from {args.collections_file}")
            except Exception as e:
                print(f"Error reading collections file: {str(e)}")
                sys.exit(1)
                
            # Process all collections
            researchers_df = process_collections(anthology, collection_ids, args.output)
        else:
            # Process single collection
            print(f"Processing single collection: {args.collection}")
            researchers_df = search_collection(anthology, args.collection)
            
            # Save results
            save_researchers_to_csv(researchers_df, args.output)
        
        # Print statistics
        print(f"\nTotal unique researchers: {len(researchers_df)}")
        
        # Calculate total time
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Script completed successfully, results saved to: {args.output}")
        
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
