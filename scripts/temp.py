import pandas as pd
import utils.csv_utils as csv_utils

df = pd.read_csv('data/paper_awards.csv')
df = csv_utils.remove_column(df, "award_weight", save_to_file=True, filepath='data/paper_awards_cleaned.csv')
