import pandas as pd
import os

# 使用绝对路径指向正确的输出目录
output_dir = '/Users/kele/实习/爬取/output/'
print(f'Checking output directory: {output_dir}')

try:
    files = os.listdir(output_dir)
    print(f'Files in directory: {files}')
except Exception as e:
    print(f'Error listing directory: {e}')

print('\nFile sizes:')
for file_name in ['acl2024_papers.csv', 'acl2024_authors.csv', 'acl2024_affiliations.csv']:
    try:
        file_path = os.path.join(output_dir, file_name)
        size = os.path.getsize(file_path)
        print(f'{file_name}: {size} bytes')
    except Exception as e:
        print(f'Error getting size of {file_name}: {e}')

print('\nTrying to read CSV files:')
try:
    papers_file = os.path.join(output_dir, 'acl2024_papers.csv')
    print(f'Reading papers file: {papers_file}')
    df_papers = pd.read_csv(papers_file)
    print(f'Papers CSV read successful, rows: {len(df_papers)}')
    print(f'Columns: {df_papers.columns.tolist()}')
    if len(df_papers) > 0:
        print('First row:')
        print(df_papers.iloc[0])
    else:
        print('DataFrame is empty')
except Exception as e:
    print(f'Papers CSV read failed: {e}')

try:
    authors_file = os.path.join(output_dir, 'acl2024_authors.csv')
    print(f'Reading authors file: {authors_file}')
    df_authors = pd.read_csv(authors_file)
    print(f'Authors CSV read successful, rows: {len(df_authors)}')
    print(f'Columns: {df_authors.columns.tolist()}')
    if len(df_authors) > 0:
        print('First row:')
        print(df_authors.iloc[0])
    else:
        print('DataFrame is empty')
except Exception as e:
    print(f'Authors CSV read failed: {e}')

try:
    affiliations_file = os.path.join(output_dir, 'acl2024_affiliations.csv')
    print(f'Reading affiliations file: {affiliations_file}')
    df_affiliations = pd.read_csv(affiliations_file)
    print(f'Affiliations CSV read successful, rows: {len(df_affiliations)}')
    print(f'Columns: {df_affiliations.columns.tolist()}')
    if len(df_affiliations) > 0:
        print('First row:')
        print(df_affiliations.iloc[0])
    else:
        print('DataFrame is empty')
except Exception as e:
    print(f'Affiliations CSV read failed: {e}')