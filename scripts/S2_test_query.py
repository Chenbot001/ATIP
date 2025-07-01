import requests
import json

def batch_request(api_key, id_list):
    """
    Make a batch request to Semantic Scholar API for multiple paper IDs
    
    Args:
        api_key (str): Semantic Scholar API key
        id_list (list): List of paper IDs to fetch
    
    Returns:
        dict: JSON response from the API
    """
    r = requests.post(
        'https://api.semanticscholar.org/graph/v1/paper/batch',
        params={'fields': 'paperId,citations.corpusId,citations.title,references.corpusId,references.title'},
        headers={'x-api-key': api_key},
        json={"ids": id_list}
    )
    return r.json()

def search_by_title(api_key, title):
    """
    Search for a paper by title using Semantic Scholar API
    
    Args:
        api_key (str): Semantic Scholar API key
        title (str): Paper title to search for
    
    Returns:
        str: Paper ID if found, None otherwise
    """
    r = requests.get(
        'https://api.semanticscholar.org/graph/v1/paper/search',
        headers={'x-api-key': api_key},
        params={
            'query': title,
            'limit': 1,
            'fields': 'paperId,references.corpusId'
        }
    )
    
    response = r.json()
    return response


if __name__ == "__main__":
    # Add your Semantic Scholar API key here
    API_KEY = "39B73CXWua7xhzGlxFrNJ5wY6uIjXCna9sLxWL2w"  # Replace with your actual API key
    id_list = ["e7d4fd44400391888226b3f5d8acac0ab2106bac", "894009cd79adab9d32132ea7ea79c8c028d68d3b"]
    # title = "KLMo: Knowledge Graph Enhanced Pretrained Language Model with Fine-Grained Relationships"
    
    papers_data = batch_request(API_KEY, id_list)
    # print(response)
    # response = search_by_title(API_KEY, title)
    # print(json.dumps(response, indent=2, ensure_ascii=False))
    for paper in papers_data:
        print(paper['paperId'])



