import pandas as pd
import os

# --- Configuration ---
AUTHORSHIPS_FILE = './data/authorships.csv'
PAPER_INFO_FILE = './data/paper_info.csv'
OUTPUT_FILE = './data/authorships_updated.csv'

def update_paper_ids():
    """
    Reads authorships.csv and paper_info.csv to replace the paper ID
    from s2_id to corpus_id.
    """
    # 1. Verify that the necessary input files exist
    if not all(os.path.exists(f) for f in [AUTHORSHIPS_FILE, PAPER_INFO_FILE]):
        print(f"❌ Error: Make sure '{AUTHORSHIPS_FILE}' and '{PAPER_INFO_FILE}' are in the same directory.")
        return

    print("▶️ Loading data files...")
    authorships_df = pd.read_csv(AUTHORSHIPS_FILE)
    # Only load the necessary columns from paper_info.csv 
    paper_info_df = pd.read_csv(PAPER_INFO_FILE, usecols=['s2_id', 'corpus_id'])

    print("🔄 Mapping s2_id to corpus_id...")
    # For merging, rename the 'paper_id' column to match 's2_id' in paper_info
    authorships_df.rename(columns={'paper_id': 's2_id'}, inplace=True)

    # Perform a left merge. This keeps all records from authorships.csv
    # and adds the matching corpus_id from paper_info.csv.
    merged_df = pd.merge(authorships_df, paper_info_df, on='s2_id', how='left')
    
    # Report if any IDs could not be mapped
    unmapped_count = merged_df['corpus_id'].isnull().sum()
    if unmapped_count > 0:
        print(f"⚠️ Warning: {unmapped_count} records could not be mapped to a corpus_id.")

    print("📝 Restructuring the DataFrame...")
    # Remove the old 's2_id' column
    merged_df.drop(columns=['s2_id'], inplace=True)
    # Rename 'corpus_id' to 'paper_id' as requested
    merged_df.rename(columns={'corpus_id': 'paper_id'}, inplace=True)

    # Reorder columns to match the original file's structure
    # Original columns are: author_id, paper_id (s2_id), author_name, is_first_author, is_last_author, paper_title 
    final_columns = [
        'author_id', 
        'paper_id', 
        'author_name', 
        'is_first_author', 
        'is_last_author', 
        'paper_title'
    ]
    final_df = merged_df[final_columns]

    print(f"💾 Saving updated data to '{OUTPUT_FILE}'...")
    final_df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n✅ Success! New file created: '{OUTPUT_FILE}'")

if __name__ == '__main__':
    update_paper_ids()