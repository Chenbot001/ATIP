You are an expert Python developer creating a robust, production-scale data-gathering script.

My goal is to create a Python script that enriches an existing database. The script will read a list of external ACL paper identifiers from a local CSV file, fetch their relational data from the Semantic Scholar (S2) API, and save the results into a new set of CSV files. These new files will be used to populate three specific relational tables: `researcher_profile`, `authorship`, and a unified `citations` table.

The script must handle a large number of inputs (~28,000 papers) by respecting the S2 API's batch limit of 500 items per request.

### Phase 1: Fetching Relational Data (various IDs of papers)

This phase processes the input CSV and generates the linking-table data.

1.  **Functionality:**
    * Create a main function, e.g., `fetch_ids(input_csv_path: str, output_dir: str)`.
    * **Input Handling:** The function must read the CSV file specified by `input_csv_path`. For each row, it must read and store the **`acl_id`**.
    * **Minibatching:** The total list of `acl_id` paper identifiers must be split into smaller "minibatches" of 500. The script must then loop through these minibatches to perform the API calls.
    * The function should create the `output_dir` if it doesn't exist.

2.  **API Call Workflow:**
    * For each minibatch of 500 identifiers, perform a single batch `POST` request to `https://api.semanticscholar.org/graph/v1/paper/batch`.
    * **ID Formatting:** Crucially, the paper identifiers from the input CSV are external ACL IDs. Before sending a minibatch to the API, the script must format each ID by prepending the `ACL:` prefix. For example, an ID like `2020.acl-main.1` from the CSV must be sent to the API as the string `ACL:2020.acl-main.1`.
    * **Fields:** Request **only** the following fields: `paperId`, `corpusId`, `externalIds`.

3.  **Output Files and Population Logic:**
    * For each minibatch, request for the paper details using the `acl_id` values. If a valid response is returned, then fill in the missing `corpus_id`, `s2_id`(semantic scholar paperId), and `DOI` values into the corresponding columns in the `paper_info.csv` table.
    * Save the updated table to a new `paper_info_full.csv` file.
    * Gracefully handle potential errors during the query, if the error is status 429 too many requests, repeat the request after a 2 second delay.
    * Skip all rows that have an invalid `acl_id`


### Technical Specifications & Best Practices

* **Language:** Python 3.
* **Libraries:** Use `requests`, `csv`, `os`, `time`, and `tqdm`.
* **User Feedback:** The script will take time to run. The main loops for processing minibatches should be wrapped with `tqdm` to display a progress bar.
* **Rate Limiting:** After each API call (for both papers and authors), include a short `time.sleep(1)` to be polite to the API servers.
* **Error Handling:** The script must gracefully handle API errors (e.g., non-200 status codes) and safely handle missing or `null` data in the API response.
* **API Key:** Structure the script with a variable at the top (e.g., `S2_API_KEY = "YOUR_KEY_HERE"`) that can be easily edited and passed in the request headers.
* **Code Structure:** Use clear functions for each phase and a `if __name__ == "__main__":` block to make the script runnable.
* The following if the official demo code for batch processing ids via POST request:
```r = requests.post(
    'https://api.semanticscholar.org/graph/v1/paper/batch',
    params={'fields': 'referenceCount,citationCount,title'},
    json={"ids": ["649def34f8be52c8b66281af98ae884c09aef38b", "ARXIV:2106.15928"]}
)
print(json.dumps(r.json(), indent=2))

[
  {
    "paperId": "649def34f8be52c8b66281af98ae884c09aef38b",
    "title": "Construction of the Literature Graph in Semantic Scholar",
    "referenceCount": 27,
    "citationCount": 299
  },
  {
    "paperId": "f712fab0d58ae6492e3cdfc1933dae103ec12d5d",
    "title": "Reinfection and low cross-immunity as drivers of epidemic resurgence under high seroprevalence: a model-based approach with application to Amazonas, Brazil",
    "referenceCount": 13,
    "citationCount": 0
  }
]```