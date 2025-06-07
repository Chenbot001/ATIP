**LLM Prompt to Generate SciBERT Fine-tuning Code for ACL Paper Track Classification**

"You are an expert Python programmer specializing in NLP and PyTorch. Generate a complete, runnable Python script to fine-tune a pre-trained SciBERT model for multi-class text classification. The goal is to classify ACL research papers into their respective tracks based on their titles (and optionally, abstracts).

**I. Project Overview & Core Libraries:**

1.  **Task:** Multi-class text classification.
2.  **Model:** Fine-tune `allenai/scibert_scivocab_uncased` from Hugging Face.
3.  **Input Data for Fine-tuning:** ACL 2025 accepted papers with titles and official track information. Assume this data is in a CSV file named `ACL25_ThemeData.csv`.
4.  **Target Application:** Classify past ACL papers (for which track information is unavailable) using the fine-tuned model. Expect past papers to be given as a csv file.
5.  **Primary Python Libraries to Use:**
    * `torch` (PyTorch)
    * `transformers` (Hugging Face: `AutoTokenizer`, `AutoModelForSequenceClassification`, `Trainer`, `TrainingArguments`, `EarlyStoppingCallback`)
    * `datasets` (Hugging Face: for loading and processing data, e.g., `Dataset.from_pandas`)
    * `pandas` (for reading the CSV file)
    * `sklearn.model_selection.train_test_split` (for splitting data)
    * `sklearn.metrics` (for `accuracy_score`, `precision_recall_fscore_support`, `confusion_matrix`)
    * `numpy`

**II. Data Handling and Preprocessing:**

1.  **Load Data:**
    * Read `ACL25_ThemeData.csv` into a pandas DataFrame.
    * Essential columns:
        * `Title` (string: paper title)
        * `Track Theme` (string: official track name, this is the target label)
        * (Optional but preferred) `abstract` (string: paper abstract). If this column is present, combine it with the `Title`.
2.  **Text Combination (if `abstract` is used):**
    * Create a new column `text_input` by concatenating `title` and `abstract`, separated by a space or a `[SEP]` token analog (e.g., "title text [SEP] abstract text"). If `abstract` is not available or empty, `text_input` should just be the `title`. Handle missing abstracts gracefully.
3.  **Label Encoding:**
    * Identify all unique track names from the `track` column.
    * Create a mapping from track names (strings) to integer IDs (e.g., `{'TrackA': 0, 'TrackB': 1, ...}`). Store this mapping (e.g., as `label2id` and `id2label` dictionaries) as it's needed for the model and for interpreting predictions.
    * Add a new column `label` to the DataFrame containing these integer IDs.
4.  **Data Splitting:**
    * Split the dataset into training and validation sets (e.g., 80% train, 20% validation). Use `train_test_split` from `sklearn.model_selection`, ensuring stratification based on the `label` column to handle potential class imbalance.
5.  **Convert to Hugging Face `Dataset`:**
    * Convert the training and validation pandas DataFrames into Hugging Face `Dataset` objects.

**III. Tokenization:**

1.  **Tokenizer:** Load the tokenizer for `allenai/scibert_scivocab_uncased`.
2.  **Tokenization Function:**
    * Create a function that takes a batch of examples from the `Dataset`.
    * Tokenizes the `text_input` field.
    * **Parameters:**
        * `truncation=True`
        * `padding="max_length"` (or another appropriate padding strategy like "longest" if preferred, but ensure consistency)
        * `max_length=512` (standard for BERT-like models).
    * This function should be applied to the training and validation `Dataset` objects using the `.map()` method.

**IV. Model Initialization:**

1.  **Load Model:** Load `allenai/scibert_scivocab_uncased` using `AutoModelForSequenceClassification`.
2.  **Configuration:**
    * Set `num_labels` in the model configuration to the number of unique tracks.
    * Pass the `label2id` and `id2label` mappings to the model's configuration.

**V. Training Configuration (Hugging Face `TrainingArguments`):**
    *This configuration is tailored for an NVIDIA RTX 4060 Laptop GPU with 8GB VRAM.*

1.  **`output_dir`:** Set to `./scibert_acl_classifier_results`.
2.  **`num_train_epochs`:** Set to `4`.
3.  **`per_device_train_batch_size`:** Set to `4`.
4.  **`per_device_eval_batch_size`:** Set to `8`.
5.  **`gradient_accumulation_steps`:** Set to `8` (to achieve an effective training batch size of 32).
6.  **`learning_rate`:** Set to `3e-5`.
7.  **`weight_decay`:** Set to `0.01`.
8.  **`evaluation_strategy`:** Set to `"steps"`.
9.  **`eval_steps`:** Set to a reasonable value (e.g., `200`, or based on dataset size, like 10-20% of total training steps per epoch).
10. **`save_strategy`:** Set to `"steps"`.
11. **`save_steps`:** Set to the same value as `eval_steps`.
12. **`logging_steps`:** Set to a reasonable value (e.g., `50`).
13. **`fp16`:** Set to `True` (CRITICAL for 8GB VRAM).
14. **`load_best_model_at_end`:** Set to `True`.
15. **`metric_for_best_model`:** Set to `"eval_f1_macro"` (or `"eval_f1_weighted"` if class imbalance is significant, or `"eval_accuracy"`).
16. **`greater_is_better`:** Set to `True` for F1/accuracy.
17. **`report_to`:** Set to `"tensorboard"` (or `"none"` if not needed).
18. (Optional, but recommended) `gradient_checkpointing=False`. Only set to `True` if Out-of-Memory errors persist after all above settings, as it slows down training.

**VI. Evaluation Metrics:**

1.  **`compute_metrics` Function:**
    * Define a function that takes `EvalPrediction` (p) as input.
    * Extract predictions (logits) and true labels.
    * Convert logits to predicted class IDs using `np.argmax`.
    * Calculate and return a dictionary containing:
        * `accuracy`: `accuracy_score(labels, preds)`
        * `precision_macro`: `precision_recall_fscore_support(labels, preds, average='macro')[0]`
        * `recall_macro`: `precision_recall_fscore_support(labels, preds, average='macro')[1]`
        * `f1_macro`: `precision_recall_fscore_support(labels, preds, average='macro')[2]`
        * `precision_weighted`: `precision_recall_fscore_support(labels, preds, average='weighted')[0]`
        * `recall_weighted`: `precision_recall_fscore_support(labels, preds, average='weighted')[1]`
        * `f1_weighted`: `precision_recall_fscore_support(labels, preds, average='weighted')[2]`
    * Consider adding per-class F1 scores if the number of classes is small enough to be manageable.

**VII. Training Execution:**

1.  **Initialize `Trainer`:**
    * Pass the model, training arguments, train dataset, eval dataset, tokenizer, and the `compute_metrics` function.
    * Include `EarlyStoppingCallback(early_stopping_patience=3)` in the `callbacks` list.
2.  **Start Training:** Call `trainer.train()`.
3.  **Save Best Model:** The `Trainer` will handle saving the best model based on `load_best_model_at_end=True`. Also explicitly call `trainer.save_model("./final_best_model")` and `tokenizer.save_pretrained("./final_best_model")` after training. Save the `label2id` mapping as well (e.g., to a JSON file).

**VIII. Inference Function:**

1.  **Define `predict_track(texts, model_path, tokenizer_path, label2id_path)`:**
    * `texts`: A list of strings, where each string is the `text_input` (title or title + abstract) of a paper to classify.
    * `model_path`: Path to the saved fine-tuned model directory (e.g., `"./final_best_model"`).
    * `tokenizer_path`: Path to the saved tokenizer directory.
    * `label2id_path`: Path to the saved `label2id` JSON file.
    * **Inside the function:**
        1.  Load the tokenizer from `tokenizer_path`.
        2.  Load the model from `model_path` (ensure it's on the correct device, e.g., 'cuda' if available).
        3.  Load the `label2id` mapping and create `id2label` from it.
        4.  Set model to evaluation mode (`model.eval()`).
        5.  Tokenize the input `texts` (padding, truncation, `max_length=512`, return PyTorch tensors).
        6.  Perform inference (`with torch.no_grad(): outputs = model(**inputs)`).
        7.  Get predicted class IDs from logits (`torch.argmax(outputs.logits, dim=-1)`).
        8.  Convert predicted IDs back to track names using `id2label`.
        9.  Return a list of predicted track names.

**IX. Code Structure & Best Practices:**

1.  **Imports:** Include all necessary imports at the beginning of the script.
2.  **Modularity:** Structure the code into logical functions (e.g., `load_and_preprocess_data`, `train_model`, `evaluate_model`, `predict_track`).
3.  **Comments:** Add comments to explain key steps and logic.
4.  **Device Handling:** Ensure PyTorch tensors are moved to the correct device (e.g., `device = torch.device("cuda" if torch.cuda.is_available() else "cpu")`).
5.  **Main Execution Block:** Use `if __name__ == "__main__":` to organize the main workflow (load data, train, evaluate, example prediction).

**Example Usage (within `if __name__ == "__main__":`)**

* Show an example of how to call the `predict_track` function with a few sample paper titles/texts after training is complete.

Please generate the Python script based on these detailed requirements."