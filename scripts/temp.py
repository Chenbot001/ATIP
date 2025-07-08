import pandas as pd
import numpy as np

def calculate_career_length_distribution(paper_info_df: pd.DataFrame,
                                         authorships_df: pd.DataFrame,
                                         author_profiles_df: pd.DataFrame) -> pd.Series:
    """
    Calculates the career length for every author in the dataset and returns the distribution.

    Args:
        paper_info_df (pd.DataFrame): DataFrame from 'paper_info.csv'. 
                                      Must contain 's2_id' and 'year'.
        authorships_df (pd.DataFrame): DataFrame from 'authorships.csv'. 
                                       Must contain 'author_id' and 'paper_id'.
        author_profiles_df (pd.DataFrame): DataFrame from 'author_profiles.csv'. 
                                           Used to get a complete list of author_ids.

    Returns:
        pd.Series: A pandas Series containing the career length for each author, 
                   indexed by author_id.
    """
    print("Starting career length calculation for all authors...")

    # For clarity, rename 'paper_id' in authorships_df to 's2_id' to match paper_info_df
    if 'paper_id' in authorships_df.columns:
        authorships_df = authorships_df.rename(columns={'paper_id': 's2_id'})

    # Merge the two dataframes to link author_id directly to publication year
    author_paper_years_df = pd.merge(
        authorships_df[['author_id', 's2_id']],
        paper_info_df[['s2_id', 'year']],
        on='s2_id'
    )

    # Find the first publication year for each author
    first_pub_years = author_paper_years_df.groupby('author_id')['year'].min()

    # Get a complete list of all author IDs from the profiles file
    all_author_ids = author_profiles_df['author_id'].unique()
    
    # Map the first publication year to the full list of authors
    # Authors without publications will have NaN for their first pub year
    first_pub_years = first_pub_years.reindex(all_author_ids)

    # Calculate career length Y = 2025 - (min(publication_year)) + 1
    current_year = 2025
    career_lengths = current_year - first_pub_years + 1

    print("Calculation complete.")
    return career_lengths.dropna().astype(int) # Drop authors with no papers and convert to int

# --- Example Usage ---
if __name__ == '__main__':
    # Load the necessary datasets
    try:
        paper_info_df = pd.read_csv('data/paper_info.csv')
        authorships_df = pd.read_csv('data/authorships.csv')
        author_profiles_df = pd.read_csv('data/author_profiles.csv')
    except FileNotFoundError:
        print("Make sure 'paper_info.csv', 'authorships.csv', and 'author_profiles.csv' are in a 'data/' directory.")
        exit()

    # Calculate career lengths
    career_lengths_dist = calculate_career_length_distribution(paper_info_df, authorships_df, author_profiles_df)

    print("\n--- Career Length Distribution Analysis ---\n")

    # 1. Summary Statistics (still useful for a general overview)
    print("Key Statistics:")
    print(career_lengths_dist.describe())

    # 2. Distribution by exact career length
    print("\nDistribution by Exact Career Length:")
    
    # Get counts for each unique career length value
    exact_counts = career_lengths_dist.value_counts().sort_index()
    exact_percentages = career_lengths_dist.value_counts(normalize=True).sort_index() * 100
    
    # Create a DataFrame for a clean display
    exact_dist_df = pd.DataFrame({
        'Career Length (Years)': exact_counts.index,
        'Author Count': exact_counts.values,
        'Percentage': exact_percentages.values
    })
    
    exact_dist_df['Percentage'] = exact_dist_df['Percentage'].map('{:.2f}%'.format)
    
    # Set the career length as the index for better readability
    exact_dist_df.set_index('Career Length (Years)', inplace=True)
    
    # Display the full distribution table
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(exact_dist_df)