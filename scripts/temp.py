import pandas as pd
import numpy as np

def clean_award_names(df: pd.DataFrame, column_name: str = 'award') -> pd.DataFrame:
    """
    Cleans and normalizes the award names in a DataFrame into canonical categories.

    Args:
        df (pd.DataFrame): The DataFrame containing the award data.
        column_name (str): The name of the column with raw award strings.

    Returns:
        pd.DataFrame: The DataFrame with a new 'award_cleaned' column.
    """
    # Mapping of canonical names to the raw strings
    AWARD_CATEGORIES = {
        'Test-of-Time Award': [
            'ACL 2020 Test-of-Time Award (25 years)', 'ACL 2022 25-Year Test of Time',
            'ACL 25-Year Test of Time Paper Award', 'NAACL 2018 Test-of-Time',
            'NAACL 2018 Test-of-Time Award'
        ],
        'Best Overall Paper': [
            'Best Long Paper', 'Best Overall Paper', 'Best Paper', 'Best Paper Award'
        ],
        'Outstanding Paper': [
            'Outstanding Long Paper', 'Outstanding Paper', 'Outstanding Paper Award', 'Outstanding Short Paper'
        ],
        'Best Short Paper': ['Best Short Paper'],
        'Best Demo Paper': [
            'Best Demo Paper', 'Best Demo Paper Award', 'Best Demo paper', 'Best Demonstration Paper',
            'Demo Track: Best Paper Award', 'Demo Track: Outstanding Paper Award', 'Outstanding Demo Paper Award'
        ],
        'Best Thematic/Resource/Impact Paper': [
            'Best Resource Paper', 'Best Resource Paper Award', 'Best Social Impact Paper Award',
            'Best Special Theme Paper', 'Best Thematic Paper', 'Best Theme Paper', 'Best Theme Paper Award',
            'Best paper on human-centered NLP special theme', 'Resource Award', 'Resource Paper Award',
            'Social Impact Award', 'Social Impact Paper Award', 'Special Theme Paper Award', 'Theme Paper Award'
        ],
        'Best Paper Runner-Up': ['Best Paper Runner-Up'],
        'Honorable Mention': [
            'Best Demonstration Runner-up', 'Honorable Demonstration Paper', 'Honorable Mention Paper',
            'Honorable Mention for Best Demonstration Paper', 'Honorable Mention for Best Overall Paper',
            'Honorable Mention for Best Theme Paper', 'Honorable mention for contribution to methods',
            'Honorable mention for contribution to special theme on human-centered NLP',
            'Honorable mention for contributions to resources'
        ],
        'Area Chair/SAC Award': [
            'Area Chair Award (Discourse and Pragmatics)', 'Area Chair Award (Interpretability and Analysis of Models for NLP)',
            'Area Chair Award (Linguistic Diversity)', 'Area Chair Award (Linguistic Theories, Cognitive Modeling, and Psycholinguistics)',
            'Area Chair Award (Multilingualism and Cross-Lingual NLP)', 'Area Chair Award (NLP Applications)',
            'Area Chair Award (Question Answering)', 'Area Chair Award (Resources and Evaluation)',
            'Area Chair Award (Semantics: Lexical)', 'Area Chair Award (Semantics: Sentence-level Semantics, Textual Inference, and Other Areas)',
            'Area Chair Award (Sentiment Analysis, Stylistic Analysis, and Argument Mining)', 'Area Chair Award (Speech and Multimodality)',
            'SAC Award: Computational Social Science and Cultural Analytics', 'SAC Award: Discourse and Pragmatics',
            'SAC Award: Efficient/Low-Resource Methods for NLP', 'SAC Award: Ethics, Bias, and Fairness',
            'SAC Award: Generation', 'SAC Award: Information Retrieval and Text Mining',
            'SAC Award: Interpretability and Analysis of Models for NLP', 'SAC Award: Linguistic theories, Cognitive Modeling and Psycholinguistics',
            'SAC Award: Machine Learning for NLP', 'SAC Award: Machine Translation',
            'SAC Award: Multilinguality and Language Diversity', 'SAC Award: Multimodality and Language Grounding to Vision, Robotics and Beyond',
            'SAC Award: Phonology, Morphology and Word Segmentation', 'SAC Award: Question Answering',
            'SAC Award: Resources and Evaluation', 'SAC Award: Semantics(Lexical)',
            'SAC Award: Semantics(Sentence-level Semantics, Textual Inference and Other areas)', 'SAC Award: Sentiment Analysis, Stylistic Analysis, and Argument Mining',
            'SAC Award: Speech recognition, text-to-speech and spoken language understanding', 'SAC Award: Summarization',
            'SAC Award: Syntax(Tagging, Chunking and Parsing)'
        ],
        'Specific Contribution Award': [
            'Best Explainable NLP Paper', 'Best Industry Paper', 'Best Linguistic Insight Paper',
            'Best efficient NLP paper', 'Best new method paper', 'Best new task (tied) and new resource paper',
            'Best new task paper (tied)'
        ],
        'SRW Best Paper Award': ['SRW Best Paper Award'],
        'Reproduction Award': ['Reproduction Award']
    }

    # Invert the mapping for easy lookup: {raw_name: canonical_name}
    cleaning_map = {raw_name: canonical_name
                    for canonical_name, raw_names in AWARD_CATEGORIES.items()
                    for raw_name in raw_names}

    df['award_cleaned'] = df[column_name].map(cleaning_map)
    return df

def assign_award_weights(df: pd.DataFrame, cleaned_column_name: str = 'award_cleaned') -> pd.DataFrame:
    """
    Assigns a weight to each paper based on its cleaned award category.

    Args:
        df (pd.DataFrame): DataFrame with a cleaned award column.
        cleaned_column_name (str): The name of the column with cleaned award names.

    Returns:
        pd.DataFrame: The DataFrame with a new 'award_weight' column.
    """
    WEIGHT_MAP = {
        # Tier 1: Premier Awards
        'Test-of-Time Award': 2.0,
        'Best Overall Paper': 2.0,
        # Tier 2: Major Awards
        'Outstanding Paper': 1.5,
        'Best Short Paper': 1.5,
        'Best Demo Paper': 1.5,
        'Best Thematic/Resource/Impact Paper': 1.5,
        'Best Paper Runner-Up': 1.5,
        # Tier 3: Special Recognition
        'Honorable Mention': 1.0,
        'Area Chair/SAC Award': 1.0,
        'Specific Contribution Award': 1.0,
        'SRW Best Paper Award': 1.0,
        # Tier 4: Other Recognitions
        'Reproduction Award': 0.5
    }

    df['award_weight'] = df[cleaned_column_name].map(WEIGHT_MAP).fillna(0)
    return df

# --- Example Usage ---
if __name__ == '__main__':
    # 1. Create a sample DataFrame mimicking your data
    csv_filepath = "data/paper_awards.csv"
    df = pd.read_csv(csv_filepath)
    print("--- Original DataFrame ---")
    print(df)
    print("\n" + "="*30 + "\n")

    # 2. Clean the award names
    cleaned_df = clean_award_names(df, column_name='award')
    print("--- DataFrame After Cleaning ---")
    print(cleaned_df[['paper_id', 'award_cleaned']])
    print("\n" + "="*30 + "\n")


    # 3. Assign weights based on the cleaned names
    final_df = assign_award_weights(cleaned_df, cleaned_column_name='award_cleaned')
    print("--- Final DataFrame with Weights ---")
    print(final_df)

    # 4. Save the final DataFrame to a new CSV file
    output_filepath = "data/paper_awards_cleaned.csv"
    final_df.to_csv(output_filepath, index=False)
    print(f"Final DataFrame saved to {output_filepath}")