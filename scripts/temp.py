import pandas as pd
import os

def analyze_unique_keys():
    """
    Analyze paper_info.csv to check if corpus_id and s2_id are unique keys.
    Print any duplicates found in a readable format.
    """
    
    # Path to the CSV file
    csv_path = os.path.join('data', 'paper_info.csv')
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"Error: File not found at {csv_path}")
        return
    
    try:
        # Read the CSV file
        print("Loading paper_info.csv...")
        df = pd.read_csv(csv_path)
        
        print(f"Total rows in dataset: {len(df)}")
        print(f"Columns found: {list(df.columns)}")
        print()
        
        # Check if required columns exist
        required_columns = ['corpus_id', 's2_id', 'title']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Error: Missing required columns: {missing_columns}")
            return

        # Analyze title uniqueness
        print("=" * 60)
        print("ANALYZING title UNIQUENESS")
        print("=" * 60)
        
        title_counts = df['title'].value_counts()
        title_duplicates = title_counts[title_counts > 1]
        
        if len(title_duplicates) == 0:
            print("✓ title is unique - no duplicates found")
        else:
            print(f"✗ title has {len(title_duplicates)} duplicate values:")
            print(f"  Total duplicate rows: {title_duplicates.sum()}")
            print()
            
            for title, count in title_duplicates.items():
                print(f"title: {title} (appears {count} times)")
                duplicate_rows = df[df['title'] == title]
                print("Duplicate rows:")
                for idx, row in duplicate_rows.iterrows():
                    print(f"  Row {idx}:")
                    print(f"    corpus_id: {row['corpus_id']}")
                    print(f"    s2_id: {row['s2_id']}")
                    print(f"    acl_id: {row['acl_id']}")
                    print(f"    DOI: {row['DOI']}")
                    print(f"    title: {row['title']}")
                    print(f"    venue: {row['venue']}")
                    print(f"    year: {row['year']}")
                print("-" * 40)
        
        print()
        
        # Summary
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total rows: {len(df)}")
        print(f"Unique corpus_id values: {df['corpus_id'].nunique()}")
        print(f"Unique s2_id values: {df['s2_id'].nunique()}")
        print(f"Unique title values: {df['title'].nunique()}")
        if len(corpus_id_duplicates) == 0 and len(s2_id_duplicates) == 0 and len(title_duplicates) == 0:
            print("✓ All columns are unique keys")
        else:
            print("✗ Duplicates found - these columns are not unique keys")
            
    except Exception as e:
        print(f"Error reading CSV file: {e}")

if __name__ == "__main__":
    analyze_unique_keys()
