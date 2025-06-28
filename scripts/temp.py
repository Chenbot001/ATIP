import arxiv
from thefuzz import fuzz

def advanced_arxiv_search(title: str, min_similarity_score=95) -> str | None:
    """
    Tries multiple search strategies to find a paper on arXiv.
    """
    clean_title = title.strip().replace('–', '-').replace('—', '-')
    
    # --- Strategy 1: Search with the colon removed ---
    # The colon is often problematic in search queries.
    title_no_colon = clean_title.replace(":", "")
    
    # --- Strategy 2: Search for just the unique part before the colon ---
    title_short = clean_title.split(":")[0]

    # List of search queries to try in order of preference
    search_queries = [
        clean_title,      # Try the original title first
        title_no_colon,   # Then try without the colon
        title_short       # Finally, try just the unique part
    ]

    print(f"--- Starting Advanced Search for: '{clean_title}' ---")

    for query in search_queries:
        print(f"\n[ATTEMPTING] Searching with query: '{query}'")
        try:
            search = arxiv.Search(query=query, max_results=5)
            results = list(search.results())
            
            if not results:
                print("[DEBUG] API returned no results for this query.")
                continue

            for result in results:
                score = fuzz.ratio(clean_title.lower(), result.title.lower())
                print(f"[DEBUG]   - Comparing with: '{result.title}' (Score: {score})")
                
                if score >= min_similarity_score:
                    print(f"[SUCCESS] Confident match found with query '{query}'!")
                    return result.summary.replace('\n', ' ')

        except Exception as e:
            print(f"[FAIL] An error occurred with query '{query}': {e}")
            continue # Try the next search strategy
            
    print("\n--- Advanced Search Failed: Could not find a confident match with any strategy. ---")
    return None


# --- Main Execution ---
if __name__ == "__main__":
    test_title = "EcomScriptBench: A Multi-task Benchmark for E-commerce Script Planning via Step-wise Intention-Driven Product Association"
    
    abstract = advanced_arxiv_search(test_title)
    
    if abstract:
        print("\n--- Abstract Found ---")
        print(abstract)