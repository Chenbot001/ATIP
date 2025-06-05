import pandas as pd
from thefuzz import fuzz
from thefuzz import process

# Read the Excel file
df = pd.read_excel('Conference Submission Topics.xlsx')

# Function to find similar strings in a list
def find_similar_topics(topics, similarity_threshold=70):
    unique_topics = []
    duplicates = {}
    
    for topic in topics:
        if not unique_topics:
            unique_topics.append(topic)
            continue
            
        # Find the best match and its score
        best_match, score = process.extractOne(topic, unique_topics, scorer=fuzz.ratio)
        
        if score >= similarity_threshold:
            # Keep the longer version
            if len(topic) > len(best_match):
                # Replace the shorter match with longer topic
                unique_topics[unique_topics.index(best_match)] = topic
                # Update existing duplicates pointing to the old match
                for k in list(duplicates.keys()):
                    if duplicates[k] == best_match:
                        duplicates[k] = topic
                duplicates[best_match] = topic
            else:
                duplicates[topic] = best_match
        else:
            unique_topics.append(topic)
    
    return unique_topics, duplicates

# Group by area and process topics
result_data = []
for area in df['Research Area'].unique():
    area_topics = df[df['Research Area'] == area]['Submission Topics'].tolist()
    unique_topics, _ = find_similar_topics(area_topics)
    
    # Add each unique topic with its area to results
    for topic in unique_topics:
        result_data.append({'Research Area': area, 'Unique Topics': topic})

# Create new dataframe with results
result_df = pd.DataFrame(result_data)

# Save to CSV
result_df.to_csv('NLP_topics.csv', index=False)

print(f"Processing complete. Found {len(result_df)} unique topics across {len(df['Research Area'].unique())} areas.")