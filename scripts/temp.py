import requests
import json

# Add your Semantic Scholar API key here
API_KEY = "39B73CXWua7xhzGlxFrNJ5wY6uIjXCna9sLxWL2w"  # Replace with your actual API key

r = requests.post(
    'https://api.semanticscholar.org/graph/v1/paper/batch',
    params={'fields': 'externalIds,authors,citations,citationCount'},
    headers={'x-api-key': API_KEY},
    json={"ids": ["DOI:10.18653/v1/2022.findings-emnlp.123"]}
)
print(json.dumps(r.json(), indent=2))
