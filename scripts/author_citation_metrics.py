import pandas as pd

# Load the necessary CSV files
authorships_df = pd.read_csv('./data/authorships.csv') # 
citation_edges_df = pd.read_csv('./data/citation_edges.csv') # [cite: 2]
paper_info_df = pd.read_csv('./data/paper_info.csv') # [cite: 3]
researcher_profiles_df = pd.read_csv('./data/researcher_profiles.csv') #

# Create a dictionary mapping paper IDs (corpus_id) to their publication year
paper_year_map = paper_info_df.set_index('s2_id')['year'].to_dict() # [cite: 3]

# Add the publication year of the citing paper to the citation_edges_df
citation_edges_df['citing_year'] = citation_edges_df['citing_paper_id'].map(paper_year_map) # 

# Filter out rows where the citing paper's year is not available (e.g., if the paper is not in paper_info.csv)
citation_edges_df.dropna(subset=['citing_year'], inplace=True) # [cite: 2]
citation_edges_df['citing_year'] = citation_edges_df['citing_year'].astype(int) # [cite: 2]

# Merge citation_edges with authorships to link cited papers to their authors.
# This gives us which author's paper was cited, and in which year the citing paper was published.
citations_with_authors = pd.merge(
    citation_edges_df,
    authorships_df,
    left_on='cited_paper_id',
    right_on='paper_id',
    how='inner'
) # [cite: 1, 2]

# Group by researcher_id and the year of the citing paper, then count citations
yearly_citations_agg = citations_with_authors.groupby(['researcher_id', 'citing_year']).size().reset_index(name='citation_count') # [cite: 1, 2]

# Calculate total citations per paper for h-index calculation
paper_citations = citations_with_authors.groupby(['researcher_id', 'cited_paper_id']).size().reset_index(name='paper_citation_count')

# Function to calculate h-index
def calculate_h_index(citation_counts):
    """
    Calculate h-index from a list of citation counts.
    H-index is the largest number h such that the researcher has h papers with at least h citations each.
    """
    if not citation_counts:
        return 0
    
    # Sort citation counts in descending order
    sorted_citations = sorted(citation_counts, reverse=True)
    
    # Find the largest h where the h-th paper has at least h citations
    for i, citations in enumerate(sorted_citations):
        if citations < i + 1:
            return i
    
    # If all papers have enough citations, return the number of papers
    return len(sorted_citations)

# Initialize a dictionary to hold the final results before converting to DataFrame
author_citation_dicts = {}
author_h_indices = {}
author_total_citations = {}

for row in yearly_citations_agg.itertuples(index=False):
    researcher_id = row.researcher_id # 
    citing_year = row.citing_year
    citation_count = row.citation_count

    if researcher_id not in author_citation_dicts:
        author_citation_dicts[researcher_id] = {}
    author_citation_dicts[researcher_id][citing_year] = citation_count

# Calculate h-index and total citations for each researcher
for researcher_id in author_citation_dicts.keys():
    # Get all papers and their citation counts for this researcher
    researcher_papers = paper_citations[paper_citations['researcher_id'] == researcher_id]
    citation_counts = researcher_papers['paper_citation_count'].tolist()
    author_h_indices[researcher_id] = calculate_h_index(citation_counts)
    
    # Calculate total citations for this researcher
    author_total_citations[researcher_id] = sum(citation_counts)

# Get unique researcher_ids and their names
# It's best to get the researcher name from researcher_profiles.csv as it's the dedicated researcher info file.
unique_researchers = researcher_profiles_df[['researcher_id', 'first_name', 'last_name']].drop_duplicates(subset=['researcher_id']) # 
unique_researchers['researcher_name'] = unique_researchers['first_name'] + ' ' + unique_researchers['last_name'] # 

# Create a list of dictionaries for the DataFrame
final_data = []
for researcher_id, name_row in unique_researchers.set_index('researcher_id').iterrows():
    researcher_name = name_row['researcher_name']
    citations_by_year_dict = author_citation_dicts.get(researcher_id, {}) # Get the dict or an empty dict if no citations
    total_citations = author_total_citations.get(researcher_id, 0) # Get total citations or 0 if no citations
    h_index = author_h_indices.get(researcher_id, 0) # Get h-index or 0 if no citations

    final_data.append({
        'researcher_id': researcher_id,
        'researcher_name': researcher_name,
        'db_citation_count': total_citations,
        'citations_by_year': citations_by_year_dict,
        'atip_h_index': h_index
    })

# Create the final DataFrame
final_df = pd.DataFrame(final_data)

# Save the final dataframe to CSV
final_df.to_csv('./data/researcher_citation_metrics.csv', index=False)
print("Data saved to ./data/researcher_citation_metrics.csv")