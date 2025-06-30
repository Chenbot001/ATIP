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
        params={'fields': 'paperId,corpusId,externalIds'},
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
            'fields': 'paperId,corpusId,externalIds'
        }
    )
    
    response = r.json()
    return response


if __name__ == "__main__":
    # Add your Semantic Scholar API key here
    API_KEY = "39B73CXWua7xhzGlxFrNJ5wY6uIjXCna9sLxWL2w"  # Replace with your actual API key
    # id_list = ["ACL:2020.emnlp-main.58"]
    title = "Refer360∘: A Referring Expression Recognition Dataset in 360∘ Images"
    
    # response = batch_request(API_KEY, id_list)
    # print(response)
    response = search_by_title(API_KEY, title)
    print(response)

