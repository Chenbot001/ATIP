import pandas as pd
from serpapi import GoogleSearch
import time

def get_co_authors(author_id):
    """
    Get the co-authors for a specific author ID
    
    Args:
        author_id (str): The Google Scholar author ID
        
    Returns:
        list: A list of co-author dictionaries
    """
    params = {
        "engine": "google_scholar_author",
        "author_id": author_id,
        "view_op": "list_colleagues",
        "api_key": "d4e7813cd16fda9fa84759812e838c970be19c5bb38181335326f4e669c7eea2"
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    # Check if co_authors key exists in results
    if "co_authors" in results:
        return results["co_authors"]
    else:
        print(f"No co-authors found for author ID: {author_id}")
        return []

# Main author to start with
main_author_name = "Eric Xing"
main_author_id = "5pKTRxEAAAAJ"

# Step 1: Get co-authors for the main author
main_author_co_authors = get_co_authors(main_author_id)

# Create a list to store all relationships (author -> co-author)
all_relationships = []

# Step 2: Process the main author's co-authors
print(f"Processing co-authors for main author: {main_author_name}")
for co_author in main_author_co_authors:
    if "name" in co_author:
        co_author_name = co_author["name"]
        all_relationships.append([main_author_name, co_author_name])
        
        # Check if author_id is available
        if "author_id" in co_author:
            co_author_id = co_author["author_id"]
            
            # Step 3: Get this co-author's co-authors (wait a bit to avoid rate limiting)
            print(f"  Processing co-authors for: {co_author_name}")
            time.sleep(1)  # Sleep 1 second between API calls to avoid rate limiting
            
            second_level_co_authors = get_co_authors(co_author_id)
            
            # Add these second-level relationships
            for second_co_author in second_level_co_authors:
                if "name" in second_co_author:
                    second_co_author_name = second_co_author["name"]
                    all_relationships.append([co_author_name, second_co_author_name])

# Create a DataFrame with the results
df = pd.DataFrame(all_relationships, columns=["Author", "Co-Author"])

# Display the first few rows
print("\nDataFrame Preview:")
print(df.head())

# Save to CSV
df.to_csv("author_network.csv", index=False)
print(f"\nSaved {len(df)} relationships to author_network.csv")