You are an expert Python developer creating a robust, production-scale data-gathering script.

My goal is to create a Python script that enriches an existing database. The script will read a list of external ACL paper identifiers from a local CSV file, fetch their relational data from the Semantic Scholar (S2) API, and save the results into a new set of CSV files. These new files will be used to populate three specific relational tables: `researcher_profile`, `authorship`, and a unified `citations` table.

The script must handle a large number of inputs (~28,000 papers) by respecting the S2 API's batch limit of 500 items per request.

### Phase 1: Fetching Relational Data (Authors & Citations)

This phase processes the input CSV and generates the linking-table data.

1.  **Functionality:**
    * Create a main function, e.g., `fetch_relational_data(input_csv_path: str, output_dir: str)`.
    * **Input Handling:** The function must read the CSV file specified by `input_csv_path` and extract all ACL paper identifiers from its `paper_id` column.
    * **Minibatching:** The total list of paper identifiers must be split into smaller "minibatches" of 500. The script must then loop through these minibatches to perform the API calls.
    * The function should create the `output_dir` if it doesn't exist.

2.  **API Call Workflow:**
    * For each minibatch of 500 identifiers, perform a single batch `POST` request to `https://api.semanticscholar.org/graph/v1/paper/batch`.
    * **ID Formatting:** Crucially, the paper identifiers from the input CSV are external ACL IDs. Before sending a minibatch to the API, the script must format each ID by prepending the `ACL:` prefix. For example, an ID like `2020.acl-main.1` from the CSV must be sent to the API as the string `ACL:2020.acl-main.1`.
    * **Fields:** Request **only** the following fields: `externalIds`, `authors`, `citations`, and `references`. The `externalIds` field is crucial for linking back to the DOI in our database, and requesting both `citations` and `references` is essential for building a complete relationship graph.

3.  **Output Files and Population Logic:**
    * The script should create and append data to the following CSV files in the `output_dir` over the course of the loop.
    * **`authorships.csv`** (Maps researchers to papers)
        * Columns: `researcher_id`, `paper_doi`, `is_first_author`, `is_last_author`
    * **`citations.csv`** (A single, unified table for all citation links)
        * Columns: `citing_paper_id`, `cited_paper_id`, `is_influential`, `context`
        * **Note:** Both `citing_paper_id` and `cited_paper_id` **must be the Semantic Scholar IDs** to correctly handle papers from outside the initial ACL set.
    * **Population Logic for `citations.csv`:** For each paper processed from the API:
        * Loop through its `references` list. For each `ref`, write a row where the *current paper* is the `citing_paper_id` and the `ref` is the `cited_paper_id`.
        * Loop through its `citations` list. For each `cit`, write a row where the `cit` is the `citing_paper_id` and the *current paper* is the `cited_paper_id`.

4.  **Collect Unique Author IDs:**
    * Across all minibatches, collect all unique `authorId`s into a single Python `set`.
    * After the loop is complete, save this unique set to a text file named **`author_ids_to_fetch.txt`** in the `output_dir`.

### Phase 2: Fetching Researcher Profile Data

This phase uses the collected author IDs to build the researcher profiles.

1.  **Functionality:**
    * Create a second function, e.g., `fetch_researcher_profiles(output_dir: str)`.
    * It should read all author IDs from the `author_ids_to_fetch.txt` file.
    * **Minibatching:** This list of author IDs must also be split into minibatches of 500. The script will loop through these minibatches to make API calls.

2.  **API Call:**
    * For each minibatch of author IDs, perform a `POST` request to `https://api.semanticscholar.org/graph/v1/author/batch`.
    * Request the fields: `name`, `hIndex`, `citationCount`, `affiliations`.

3.  **Output File and Columns:**
    * Create the final CSV file for the researcher profiles.
    * **`researcher_profiles.csv`**
        * Columns: `researcher_id`, `first_name`, `last_name`, `h_index`, `total_citations`, `latest_affiliation`

### Technical Specifications & Best Practices

* **Language:** Python 3.
* **Libraries:** Use `requests`, `csv`, `os`, `time`, and `tqdm`.
* **User Feedback:** The script will take time to run. The main loops for processing minibatches should be wrapped with `tqdm` to display a progress bar.
* **Rate Limiting:** After each API call (for both papers and authors), include a short `time.sleep(1)` to be polite to the API servers.
* **Error Handling:** The script must gracefully handle API errors (e.g., non-200 status codes) and safely handle missing or `null` data in the API response.
* **API Key:** Structure the script with a variable at the top (e.g., `S2_API_KEY = "YOUR_KEY_HERE"`) that can be easily edited and passed in the request headers.
* **Code Structure:** Use clear functions for each phase and a `if __name__ == "__main__":` block to make the script runnable.
* The `POST` requests for semantic scholar has this general format:
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