from acl_anthology import Anthology
from acl_anthology.people.name import Name, NameSpecification
import pandas as pd
import os
import sys
import requests
import time
import logging
from concurrent.futures import ThreadPoolExecutor

# 配置日志
logging.basicConfig(
    filename='openreview_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 定义一个函数来将数据添加到研究者CSV文件中
def save_researchers_to_csv(researchers_df, csv_file='data/researchers_data.csv'):
    # 检查文件是否存在，如果不存在则创建一个新的DataFrame
    file_exists = os.path.isfile(csv_file)
    
    # Save the DataFrame to CSV
    mode = 'a' if file_exists else 'w'
    header = not file_exists
    
    researchers_df.to_csv(csv_file, mode=mode, header=header, index=False, encoding='utf-8')
    print(f"Data saved to {csv_file}")

# 简化版的OpenReview ID查找函数
def get_openreview_id(author_full_name=None, paper_title=None, acl_author_id=None, first_name=None, last_name=None):
    """
    通过作者姓名查找 OpenReview ID (优化版)
    
    Args:
        author_full_name, paper_title, acl_author_id, first_name, last_name
        
    Returns:
        str or None: OpenReview ID 或 None
    """
    # 确保我们至少有作者的姓或名
    if not ((author_full_name and author_full_name.strip()) or 
            (first_name and last_name and first_name.strip() and last_name.strip())):
        logging.error(f"参数错误: 未提供足够的作者信息")
        return None
    
    # 从全名提取姓名或使用提供的姓名
    if not (first_name and last_name):
        if author_full_name:
            name_parts = author_full_name.split()
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = name_parts[-1]
            else:
                logging.error(f"无法解析作者全名: '{author_full_name}'")
                return None
    
    # 标准化姓名
    first_name = first_name.strip().capitalize()
    last_name = last_name.strip().capitalize()
    full_name = f"{first_name} {last_name}"
    
    try:
        # 构建最常见的几种ID格式 (减少变体数量以提高速度)
        potential_ids = [
            f"~{first_name}_{last_name}1", 
            f"~{first_name.lower()}_{last_name.lower()}1",
            f"~{first_name}{last_name}1",
            f"~{last_name}1"
        ]
        
        # 批量检查ID (减少API调用次数)
        for potential_id in potential_ids:
            try:
                openreview_api_url = f"https://api.openreview.net/profiles?id={potential_id}"
                response = requests.get(openreview_api_url)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('profiles') and len(result.get('profiles')) > 0:
                        return potential_id
            except Exception:
                # 单个ID查询失败不影响整体流程
                continue
        
        # 通过全名搜索
        try:
            formatted_name = full_name.replace(" ", "+")
            openreview_search_url = f"https://api.openreview.net/profiles?fullname={formatted_name}"
            response = requests.get(openreview_search_url)
            
            if response.status_code == 200:
                profiles = response.json().get('profiles', [])
                
                if profiles and len(profiles) > 0:
                    # 简化：直接返回第一个匹配结果
                    return profiles[0].get('id')
        except Exception:
            # 全名搜索失败则跳过
            pass
                
    except Exception as e:
        logging.error(f"搜索作者 '{full_name}' 论文 '{paper_title}' 时出错: {str(e)}")
    
    return None

def search_collection(anthology, collection_id=""):
    collection = anthology.get(collection_id)
    all_unique_authors = set()
    total_papers = 0
    
    # 创建列表存储所有研究者数据
    researchers_data = []
    
    print(f"开始分析数据集: {collection.id}")
    
    # 添加处理单个作者的函数用于多线程处理
    def process_author(author, paper_title):
        name = Name.from_(author.name)
        first_name = name.first if name.first else ''
        last_name = name.last
        
        # 获取OpenReview ID
        openreview_id = get_openreview_id(
            first_name=first_name,
            last_name=last_name,
            paper_title=paper_title,
            acl_author_id=author.id
        )
        
        return {
            'researcher_id': openreview_id,
            'first_name': first_name,
            'last_name': last_name,
        }

    # 用于跟踪已处理的作者数量
    processed_authors = 0
    total_authors = 0  # 将在处理过程中更新
    
    # 遍历卷和论文收集作者
    for volume in collection.volumes():
        volume_papers = 0
        authors_tasks = []
        
        for paper in volume.papers():
            volume_papers += 1
            total_papers += 1
            
            # 获取论文标题
            paper_title_text = None
            if paper.title:
                try:
                    paper_title_text = paper.title.as_text() if hasattr(paper.title, 'as_text') else str(paper.title)
                except Exception:
                    paper_title_text = str(paper.title) if paper.title else None

            # 准备作者处理任务
            for author in paper.authors:
                all_unique_authors.add(author.name)
                authors_tasks.append((author, paper_title_text))
                total_authors += 1
        
        # 使用线程池处理当前卷中的所有作者
        with ThreadPoolExecutor(max_workers=10) as executor:
            # 提交所有作者处理任务
            future_results = {executor.submit(process_author, author, paper_title): (author, paper_title) 
                             for author, paper_title in authors_tasks}
            
            # 收集结果
            for future in future_results:
                try:
                    result = future.result()
                    researchers_data.append(result)
                    processed_authors += 1
                    
                    # 每处理100个作者显示一次进度
                    if processed_authors % 100 == 0:
                        print(f"已处理: {processed_authors}/{total_authors} 作者")
                except Exception as e:
                    author, paper_title = future_results[future]
                    name = Name.from_(author.name)
                    logging.error(f"处理作者出错 '{name.as_full()}', 论文 '{paper_title}': {str(e)}")
        
        # 记录每卷的基本统计信息
        print(f"完成卷: {volume.title} - {volume_papers} 篇论文")
    
    # 创建数据框架
    researchers_df = pd.DataFrame(researchers_data)
    print(f"总计: {total_papers} 篇论文, {len(all_unique_authors)} 位独立作者")

    return researchers_df

def main():
    import argparse
    
    # 添加命令行参数支持
    parser = argparse.ArgumentParser(description='爬取研究者数据并关联OpenReview ID')
    parser.add_argument('--collection', type=str, default="2024.acl", 
                        help='要爬取的ACL集合ID (默认: 2024.acl)')
    parser.add_argument('--output', type=str, default="data/researcher_data.csv",
                        help='输出CSV文件路径 (默认: data/researcher_data.csv)')
    parser.add_argument('--threads', type=int, default=10,
                        help='线程数量 (默认: 10)')
    parser.add_argument('--batch-size', type=int, default=100,
                        help='每次保存的批次大小 (默认: 100)')
    args = parser.parse_args()
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    try:
        # 尝试从本地仓库初始化anthology
        start_time = time.time()
        print(f"开始处理，时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        anthology = None
        try:
            anthology = Anthology.from_repo()
            print("使用本地anthology仓库")
        except Exception as e:
            print(f"初始化anthology出错: {e}")
            print("尝试使用在线仓库...")
            try:
                anthology = Anthology.from_url()
                print("使用在线anthology仓库")
            except Exception as e2:
                print(f"无法初始化anthology: {e2}")
                sys.exit(1)

        # 爬取集合数据
        print(f"开始爬取集合: {args.collection}")
        researchers_df = search_collection(anthology, collection_id=args.collection)
        
        # 保存数据到CSV
        save_researchers_to_csv(researchers_df, csv_file=args.output)
        
        # 打印统计信息
        success_count = researchers_df['researcher_id'].notna().sum()
        total_count = len(researchers_df)
        success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
        print(f"成功率: {success_rate:.2f}% ({success_count}/{total_count})")
        
        # 计算总用时
        end_time = time.time()
        total_time = end_time - start_time
        print(f"总用时: {total_time:.2f} 秒")
        print(f"脚本成功完成，结果保存到: {args.output}")
        
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        logging.error(f"执行过程中出现未处理的错误: {str(e)}")
        print(f"遇到错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()



