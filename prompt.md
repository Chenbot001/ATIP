You are an expert Python developer and prompt engineer with deep experience in machine learning and interacting with Large Language Model APIs. Your task is to generate a complete, well-structured, and robust Python script that uses the Qwen LLM API to classify research papers via few-shot prompt engineering.

### **Project Goal**

The goal of the generated script is to classify research papers into one of 26 predefined tracks using only their titles. It will use a few-shot prompting strategy to guide the Qwen model and then calculate performance metrics to assess the method's viability.

### **Core Script Requirements**

**1. Configuration:**
* At the top of the script, include a configuration section with easily editable variables for `QWEN_API_KEY`, `MODEL_NAME` (e.g., `qwen-max`) and INPUT_CSV_PATH.
* Ensure the API key is read from an environment variable for security (`os.getenv("DASHSCOPE_API_KEY")`).

**2. Data Loading and Preparation:**
* Load the data from a filepath variable INPUT_CSV_PATH into a pandas DataFrame.
* For this machine, use the path: C:\Eric\Projects\AI_Researcher_Network\data\ACL25_ThemeData.csv
* Obtain a list of unique tracks from the 'Track Theme' column to be used for response validation.
* Define the 5 few-shot examples (title-track pairs) in the form of a list of dictionaries ([{'title': '...', 'track': '...'}, ...]) that will be hard-coded in the prompt.
* Create a test set by removing the rows that correspond to the papers selected as few-shot examples.

**3. Few-Shot Prompt Engineering:**
* Create a clear, multi-line PROMPT_TEMPLATE string. It should include instructions for the model, the full list of 26 possible tracks, and placeholders for the 5 examples and the final query title.
* Instruct the model to only respond with the predicted track name from the provided list.
* Create a generate_prompt(title, examples) function that inserts the 5 few-shot examples and the query title into the template.

**4. Qwen API Interaction:**
* Create a function `get_qwen_prediction(prompt)` that takes the generated prompt and calls the Qwen API.
* The function should handle the API call, extract the text content from the response, and include basic error handling.
* Set the `temperature` to a low value (e.g., `0.1`) for deterministic and consistent outputs.

**5. Main Classification and Evaluation Loop:**
* The main part of the script should iterate through each row of the test set DataFrame. A `tqdm` progress bar should be used to monitor progress.
* For each paper, it should:
    1.  Call `get_qwen_prediction()` to get the model's classification.
    2.  Implement a simple `parse_response(response_text)` helper function to clean the model's output and match it against the list of tracks. This handles cases where the model might add extra conversational text.
    3.  Store the ground truth label and the parsed prediction in two separate lists.
* After the loop finishes, the script must calculate and print the final performance metrics.

**6. Performance Metrics:**
* Use `sklearn.metrics.classification_report` to generate a detailed report. This report should be printed to the console and must include:
    * Per-class precision, recall, and F1-score.
    * Overall accuracy.
    * Macro-averaged and weighted-averaged scores.
* This provides a comprehensive view of the performance, especially given the class imbalance.

**7. Code Structure:**
* The final script should be modular, with clear functions for each logical step (data loading, prompt generation, API call, evaluation).
* Include comments to explain each part of the process.
* Use a `if __name__ == "__main__":` block to orchestrate the execution flow.

Please generate the complete Python script based on these detailed requirements.