"""
ACL Anthology Paper Award Information Extractor

This script extracts paper award information from the ACL Anthology and saves it to a CSV file.
It creates a one-to-many mapping between papers and their awards.

The script uses the ACL Anthology API to access paper award data and pandas for efficient
data manipulation and storage.

Usage:
    python paper_award_table.py

Requirements:
    - acl_anthology library
    - pandas
    - Python 3.6+
"""

from acl_anthology import Anthology
import pandas as pd
import os
import sys

def save_paper_awards_to_csv(awards_df, csv_file='paper_awards.csv'):
    """
    Save a DataFrame of paper award information to a CSV file.
    
    Args:
        awards_df (pd.DataFrame): DataFrame containing paper award information.
        csv_file (str, optional): Path to the output CSV file. Defaults to 'paper_awards.csv'.
        
    Returns:
        None
    """
    # Always overwrite the file to ensure outdated data is replaced
    awards_df.to_csv(csv_file, mode='w', header=True, index=False, encoding='utf-8')
    print(f"Award data saved to {csv_file}")

def extract_paper_awards(anthology, collection_id=""):
    """
    Extract award information for papers in a collection in the ACL Anthology.
    
    Args:
        anthology (Anthology): Anthology instance to use for searching.
        collection_id (str, optional): ID of the collection to search.
        
    Returns:
        pd.DataFrame: A DataFrame containing paper_id and award mapping.
    """
    try:
        # Get the collection
        collection = anthology.get(collection_id)
        awards_data = []
        
        # Keep track of volumes that contain award annotations
        volume_with_awards = False
        paper_counter = 0
        
        for volume in collection.volumes():
            for paper in volume.papers():
                paper_counter += 1
                paper_id = paper.full_id
                
                # 根据文档使用paper.awards属性（注意是复数形式）获取获奖信息，它是一个列表
                if hasattr(paper, 'awards') and paper.awards:
                    volume_with_awards = True
                    # 对于列表中的每个奖项创建一条记录
                    for award in paper.awards:
                        awards_data.append({
                            'paper_id': paper_id,
                            'award': award
                        })
                        # 打印找到的奖项信息，用于调试
                        print(f"Found award for paper {paper_id}: {award}")
        
        if volume_with_awards:
            print(f"Found awards in collection: {collection_id}")
        
        if paper_counter > 0:
            print(f"Examined {paper_counter} papers in collection: {collection_id}")
            
        return pd.DataFrame(awards_data)
    
    except Exception as e:
        print(f"Error processing collection {collection_id}: {e}")
        return pd.DataFrame()

def main():
    """
    Main function to initialize the Anthology and run the paper award extraction process.
    
    Returns:
        None
    """
    try:
        # Try to initialize anthology from local repo first
        anthology = Anthology.from_repo()
        print("Using local anthology repository.")
    except Exception as e:
        print(f"Error initializing anthology: {e}")
        try:
            # 如果本地仓库不可用，尝试从在线API初始化
            anthology = Anthology()
            print("Using online anthology API.")
        except Exception as e:
            print(f"Error initializing online anthology: {e}")
            print("Could not initialize anthology. Make sure the data or internet connection is available.")
            sys.exit(1)

    # Read all collection IDs from acl_collections.txt
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    collections_file = os.path.join(project_root, "data", "acl_collections.txt")
    
    with open(collections_file, "r") as file:
        collection_ids = [line.strip() for line in file]

    # Initialize an empty DataFrame to accumulate all paper award data
    all_awards_df = pd.DataFrame()

    # Initialize counters
    total_collections_with_awards = 0
    total_awards = 0
    
    # 先尝试处理一些最可能包含奖项的会议集合
    important_collections = [
        "2023.acl", "2022.acl", "2021.acl", "2020.acl",
        "2023.emnlp", "2022.emnlp", "2021.emnlp", "2020.emnlp",
        "2023.naacl", "2022.naacl", "2021.naacl", "2020.naacl"
    ]
    
    priority_collections = [cid for cid in important_collections if cid in collection_ids]
    if priority_collections:
        print("First processing priority collections that are likely to have awards:")
        for collection_id in priority_collections:
            print(f"Processing priority collection: {collection_id}")
            awards_df = extract_paper_awards(anthology, collection_id=collection_id)
            
            if not awards_df.empty:
                all_awards_df = pd.concat([all_awards_df, awards_df], ignore_index=True)
                total_collections_with_awards += 1
                total_awards += len(awards_df)
    
    # 然后处理其余的集合
    remaining_collections = [cid for cid in collection_ids if cid not in priority_collections]
    print("\nProcessing remaining collections:")
    for collection_id in remaining_collections:
        print(f"Processing collection: {collection_id}")
        awards_df = extract_paper_awards(anthology, collection_id=collection_id)
        
        if not awards_df.empty:
            all_awards_df = pd.concat([all_awards_df, awards_df], ignore_index=True)
            total_collections_with_awards += 1
            total_awards += len(awards_df)

    # Save the accumulated data to CSV
    if not all_awards_df.empty:
        output_file = os.path.join(project_root, "data", "paper_awards.csv")
        save_paper_awards_to_csv(all_awards_df, csv_file=output_file)

        # Display total counts
        print(f"\nTotal collections with awards: {total_collections_with_awards}")
        print(f"Total award entries collected: {total_awards}")
        
        # Print summary of awards by collection
        awards_by_collection = all_awards_df['paper_id'].str.split('-').str[0].value_counts()
        print("\nAwards by collection:")
        for collection, count in awards_by_collection.items():
            print(f"{collection}: {count} awards")
    else:
        print("No award information found in any collection.")
        
        # 检查API功能是否正常
        print("\nTesting API functionality with a specific paper...")
        try:
            # 尝试直接获取一个已知的获奖论文（如果存在）
            test_paper_id = "2020.acl-long.1"  # 只是一个示例ID
            paper = anthology.get(test_paper_id)
            if paper:
                print(f"Successfully retrieved paper: {test_paper_id}")
                print(f"Paper title: {paper.title}")
                print(f"Paper awards attribute exists: {hasattr(paper, 'awards')}")
                print(f"Paper awards value: {paper.awards if hasattr(paper, 'awards') else 'None'}")
        except Exception as e:
            print(f"Error testing API: {e}")

    print("Paper award extraction completed successfully.")

if __name__ == "__main__":
    main()



