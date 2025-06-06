from acl_anthology import Anthology
import csv

# 定义一个函数来将数据添加到 CSV 文件中
def add_to_table(paper_id, title, abstract, venue, year, award, tracks):
    # 定义 CSV 文件的文件名
    csv_file = 'papers_data.csv'
    # 定义要写入的行
    row = [paper_id, title, abstract, venue, year, award, tracks]
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
                researcher = author.name
                volume_unique_authors.add(researcher)
                all_unique_authors.add(researcher)
            # 新增代码：统计每篇文献的数据
            paper_id = paper.doi
            title = paper.title
            abstract = paper.abstract
            venue = anthology.venues[paper.venue_ids[0]].name if paper.venue_ids else ''
            year = paper.year
            award = paper.awards
            tracks = None
            # 假设有一个函数 add_to_table 用于将数据添加到表格中
            add_to_table(paper_id, title, abstract, venue, year, award, tracks)
        
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

    search_collection()



