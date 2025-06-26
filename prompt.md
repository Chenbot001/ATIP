You are an expert Python developer specializing in robust data scraping and workflow automation. Your task is to generate a complete, production-ready Python script that accomplishes the following: It reads a CSV file containing publication titles, searches for each publication on Google Scholar to retrieve its abstract, and saves the enriched data to a new CSV file.

The script must be robust and include advanced error handling and anti-blocking mechanisms.

**Key Functional Requirements:**

1.  **Read Input CSV:**
    * The target CSV file is currently: C:\Eric\Projects\AI_Researcher_Network\data\ACL25_ThemeData.csv
    * Use the `pandas` library to read a CSV file specified by a command-line argument.
    * The input CSV is expected to have a column named `Title` which contains the publication titles to search for.


2.  **Process Data:**
    * Create a new column in the DataFrame called `Abstract` if not present.
    * Iterate through each row of the DataFrame.
    * For each title, use the find the abstract using the `semantic scholar` API paper endpoint.
    * Skip rows that has an abstract present.
    * If a publication is not found or has no abstract, the `Abstract` cell for that row should be left blank or filled with `None`.

3.  **Save Output CSV:**
    * After processing all rows, save the updated DataFrame (including the new `abstract` column) into a new CSV, name it by adding `_abs` to the end to the input filename.

3.  **Comprehensive Error Handling:**
    * Wrap the search call in a `try...except` block.
    * Gracefully handle specific exceptions.
    * Log any errors to the console with the title that caused the failure but continue processing the remaining rows.
4.  **Incremental Saving:** For large datasets, the script should save its progress to the output CSV file incrementally (e.g., every 50 rows processed). This prevents total data loss if the script is interrupted.

**Code Structure and Usability:**

* **Progress Indicator:** Use `tqdm` to display a progress bar showing the processing status.
* **Main Function:** Structure the code within a `main()` function and use the `if __name__ == "__main__":` block.
* **Dependencies:** Include a comment block at the top of the script listing all necessary libraries