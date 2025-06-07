from acl_anthology import Anthology
from acl_anthology.people.name import Name
import csv

# 定义一个函数来将数据添加到研究者CSV文件中
def add_to_researcher_table(researcher_id, first_name, last_name, affiliation):
    # 定义 CSV 文件的文件名
    csv_file = 'researchers_data.csv'
    # 定义要写入的行
    row = [researcher_id, first_name, last_name, affiliation]
    # 打开 CSV 文件并追加写入
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # 写入行
        writer.writerow(row)

def search_collection():
    collection = anthology.get("2024.acl")
    all_unique_authors = set()
    total_papers = 0
    
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
                # 获取作者机构信息
                affiliation = author.affiliation if hasattr(author, 'affiliation') else ''
                # 使用作者姓名作为临时ID（实际应用中应该使用OpenReview.net ID）
                researcher_id = name.as_full().lower().replace(' ', '_')
                
                # 将作者信息添加到研究者表中
                add_to_researcher_table(researcher_id, first_name, last_name, affiliation)
                
                volume_unique_authors.add(name.as_full())
                all_unique_authors.add(name.as_full())
        
        print(f"Volume: {volume.title}")
        print(f"  Number of papers: {volume_papers}")
        print(f"  Number of unique authors: {len(volume_unique_authors)}\n")

    print(f"Total {total_papers} papers and unique authors across all volumes in collection {collection.id}: {len(all_unique_authors)}")

if __name__ == "__main__":
    try:
        anthology = Anthology.from_repo()
    except:
        try:
            anthology = Anthology()
        except:
            print("Could not initialize anthology. Make sure the data is available.")
            import sys
            sys.exit(1)

    # 创建研究者表的表头
    with open('researchers_data.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['researcher_id', 'first_name', 'last_name', 'affiliation_history'])
    
    search_collection()



