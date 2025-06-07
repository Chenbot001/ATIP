from acl_anthology import Anthology
from acl_anthology.people.name import Name, NameSpecification
import pandas as pd
import os
import sys

# 定义一个函数来将数据添加到研究者CSV文件中
def save_researchers_to_csv(researchers_df, csv_file='data/researchers_data.csv'):
    # 检查文件是否存在，如果不存在则创建一个新的DataFrame
    # Check if the file exists to determine whether to write headers
    file_exists = os.path.isfile(csv_file)
    
    # Save the DataFrame to CSV
    mode = 'a' if file_exists else 'w'
    header = not file_exists
    
    researchers_df.to_csv(csv_file, mode=mode, header=header, index=False, encoding='utf-8')
    print(f"Data saved to {csv_file}")

def search_collection(anthology, collection_id=""):
    collection = anthology.get(collection_id)
    all_unique_authors = set()
    total_papers = 0
    
    # Create a list to store all paper data
    researchers_data = []

    print(f"Analyzing collection: {collection.id}\n")
    
    for volume in collection.volumes():
        volume_papers = 0
        volume_unique_authors = set()

        for paper in volume.papers():
            volume_papers += 1
            total_papers += 1
            for author in paper.authors:
                # 使用Name类处理作者姓名
                name = Name.from_(author.name)
                first_name = name.first if name.first else ''
                last_name = name.last
                # 使用NameSpecification来获取作者ID
                researcher_id = author.id
                
                researchers_data.append({
                    'researcher_id': researcher_id,
                    'first_name': first_name,
                    'last_name': last_name,
                })
                
                volume_unique_authors.add(name.as_full())
                all_unique_authors.add(name.as_full())
        
        print(f"Volume: {volume.title}")
        print(f"  Number of papers: {volume_papers}")
        print(f"  Number of unique authors: {len(volume_unique_authors)}\n")

    researchers_df = pd.DataFrame(researchers_data)
    print(f"Total {total_papers} papers and unique authors across all volumes in collection {collection.id}: {len(all_unique_authors)}")


    return researchers_df

def main():
    try:
        # Try to initialize anthology from local repo first
        anthology = Anthology.from_repo()
        print("Using local anthology repository.")
    except Exception as e:
        print(f"Error initializing anthology: {e}")
        print("Could not initialize anthology. Make sure the data is available.")
        sys.exit(1)

    # Search the collection and get paper data
    researchers_df = search_collection(anthology, collection_id="2024.acl")

    
    # Save the data to CSV
    save_researchers_to_csv(researchers_df, csv_file='data/researcher_data.csv')

    print("Script completed successfully.")

if __name__ == "__main__":
    main()



