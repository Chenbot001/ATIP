import os
from scholarly import scholarly, ProxyGenerator

# 1. Set up the ProxyGenerator
pg = ProxyGenerator()

# 2. Get your ScraperAPI key (replace with your actual key)
# It's good practice to use an environment variable, but for testing, direct assignment is fine.
api_key = "a85311ebe02d0c06b99e0f7ead062c6b" 

# 3. Set the proxy for scholarly using the correct ScraperAPI format
# This is the most critical line.
success = pg.ScraperAPI(api_key)

if not success:
    print("Failed to set up the ScraperAPI proxy. Check your API key and network.")
else:
    print("Successfully set up ScraperAPI proxy.")
    scholarly.use_proxy(pg)

    # 4. Now, try to make a request
    print("Attempting to search for a publication...")
    try:
        search_query = scholarly.search_pubs('EcomScriptBench: A Multi-task Benchmark for E-commerce Script Planning via Step-wise Intention-Driven Product Association')
        first_result = next(search_query)
        
        print("\n=== PUBLICATION DETAILS ===")
        scholarly.pprint(first_result)
        
        print("\n=== ABSTRACT EXTRACTION ===")
        # Extract and print the abstract
        if first_result and 'bib' in first_result and 'abstract' in first_result['bib']:
            abstract = first_result['bib'].get('abstract')
            if abstract and abstract.strip():
                print("✅ Abstract found:")
                print("-" * 50)
                print(abstract.strip())
                print("-" * 50)
            else:
                print("❌ Abstract field exists but is empty or whitespace only")
        else:
            print("❌ No abstract found in the publication result")
            print("Available keys in 'bib':", list(first_result.get('bib', {}).keys()) if first_result and 'bib' in first_result else "No 'bib' key found")
        
        print("\nTest successful!")
    except Exception as e:
        print(f"\nAn error occurred during the search: {e}")
        print("This could be due to an incorrect API key, expired trial, or a network issue.")