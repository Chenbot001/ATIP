#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
爬取ACL会议文章的所有作者和对应所属机构
"""

import csv
import os
import pandas as pd
from collections import defaultdict
import time

# 尝试不同的导入方式
try:
    # 新版本的导入方式
    from acl_anthology import Anthology
except ImportError:
    try:
        # 旧版本的导入方式
        from anthology import Anthology
    except ImportError:
        print("无法导入Anthology类，请确保已安装acl-anthology库")
        raise


def get_authors_and_affiliations(venue='2024.acl'):
    """
    获取指定会议的所有论文作者和机构信息
    
    参数:
        venue (str): 会议标识，默认为'2024.acl'
    
    返回:
        tuple: (作者-机构映射, 所有机构集合, 论文信息列表)
    """
    print(f"开始获取{venue}会议的论文作者和机构信息...")
    
    # 创建anthology客户端
    # 使用from_repo()方法自动从ACL Anthology仓库获取数据
    try:
        client = Anthology.from_repo()
    except Exception as e:
        print(f"从仓库获取数据失败: {e}")
        print("尝试使用本地数据目录...")
        # 如果从仓库获取失败，尝试使用本地数据目录
        data_dir = os.path.join(os.getcwd(), 'anthology_data')
        os.makedirs(data_dir, exist_ok=True)
        # 克隆ACL Anthology仓库到本地
        import subprocess
        try:
            print("克隆ACL Anthology仓库...")
            subprocess.run(["git", "clone", "https://github.com/acl-org/acl-anthology.git", data_dir], check=True)
            client = Anthology(importdir=os.path.join(data_dir, 'data'))
        except subprocess.CalledProcessError:
            print("克隆仓库失败，请确保已安装git并且网络连接正常")
            raise
    
    # 存储作者和机构信息的字典
    authors_dict = defaultdict(set)  # 作者 -> 机构集合
    affiliations_set = set()  # 所有机构集合
    papers_info = []  # 存储论文信息
    
    try:
        # 获取所有论文
        print(f"正在获取{venue}会议的论文...")
        
        # 根据API文档，获取特定会议的论文
        venue_papers = []
        venue_id = venue.replace('.', '-')
        
        # 尝试两种方法获取论文
        try:
            # 方法1：尝试通过事件获取
            event_id = venue_id.split('-')[1] + '-' + venue_id.split('-')[0]
            print(f"尝试通过事件ID获取: {event_id}")
            event = client.get_event(event_id)
            
            if event:
                print(f"找到事件: {event.id}")
                for volume in event.volumes():
                    print(f"处理卷: {volume.full_id}")
                    for paper_id, paper in volume.items():
                        venue_papers.append(paper)
            else:
                print(f"未找到事件: {event_id}，尝试直接获取卷...")
                # 如果找不到事件，尝试直接获取卷
                volume = client.get_volume(venue_id)
                if volume:
                    print(f"找到卷: {volume.full_id}")
                    for paper_id, paper in volume.items():
                        venue_papers.append(paper)
                else:
                    print(f"未找到卷: {venue_id}，尝试直接获取集合...")
                    # 如果找不到卷，尝试获取集合
                    collection = client.get_collection(venue_id.split('-')[0])
                    if collection:
                        print(f"找到集合: {collection.id}")
                        for vol_id, volume in collection.items():
                            if vol_id.startswith(venue_id.split('-')[1]):
                                print(f"处理卷: {volume.full_id}")
                                for paper_id, paper in volume.items():
                                    venue_papers.append(paper)
        except Exception as e:
            print(f"通过事件获取论文失败: {e}")
            print("尝试通过直接搜索获取论文...")
            
            # 方法2：尝试直接搜索所有论文
            # 注意：这种方法可能效率较低，但作为备选方案
            for collection_id, collection in client.collections.items():
                if collection_id.startswith(venue_id.split('-')[0]):
                    for vol_id, volume in collection.items():
                        if venue_id.split('-')[1] in vol_id:
                            for paper_id, paper in volume.items():
                                venue_papers.append(paper)
        
        if not venue_papers:
            print(f"警告: 未找到{venue}会议的论文，请检查会议ID是否正确")
            return authors_dict, affiliations_set, papers_info
            
        total_papers = len(venue_papers)
        print(f"找到{total_papers}篇论文")
        
        for i, paper in enumerate(venue_papers, 1):
            try:
                # 获取论文信息
                paper_id = getattr(paper, 'id', 'unknown_id')
                paper_title = getattr(paper, 'title', 'Untitled')
                
                paper_info = {
                    'paper_id': paper_id,
                    'title': paper_title,
                    'authors': [],
                    'affiliations': []
                }
                
                print(f"处理第{i}/{total_papers}篇论文: {paper_title}")
                
                # 处理每个作者及其机构
                if hasattr(paper, 'authors'):
                    for author in paper.authors:
                        try:
                            name = str(author.name) if hasattr(author, 'name') else 'Unknown Author'
                            affiliation = str(author.affiliation) if hasattr(author, 'affiliation') and author.affiliation else 'Unknown'
                            
                            # 更新作者-机构映射
                            authors_dict[name].add(affiliation)
                            # 更新机构集合
                            affiliations_set.add(affiliation)
                            
                            # 添加到论文信息中
                            paper_info['authors'].append(name)
                            paper_info['affiliations'].append(affiliation)
                        except Exception as e:
                            print(f"处理作者时出错: {str(e)}")
                else:
                    print(f"警告: 论文 {paper_id} 没有作者信息")
                
                papers_info.append(paper_info)
                
                # 每处理10篇论文打印一次进度
                if i % 10 == 0:
                    print(f"已处理 {i}/{total_papers} 篇论文")
            except Exception as e:
                print(f"处理论文时出错: {str(e)}")
                continue
        
        print("所有论文处理完成!")
        return authors_dict, affiliations_set, papers_info
    
    except Exception as e:
        print(f"获取论文信息时出错: {str(e)}")
        return authors_dict, affiliations_set, papers_info


def save_results(authors_dict, affiliations_set, papers_info, output_dir="/Users/kele/实习/爬取/anthology/output"):
    """
    将结果保存到CSV文件
    
    参数:
        authors_dict (dict): 作者-机构映射
        affiliations_set (set): 所有机构集合
        papers_info (list): 论文信息列表
        output_dir (str): 输出目录
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n保存数据到 {output_dir}...")
    print(f"作者数量: {len(authors_dict)}")
    print(f"机构数量: {len(affiliations_set)}")
    print(f"论文数量: {len(papers_info)}")
    
    # 打印统计信息
    print("\n统计信息:")
    print(f"总共找到 {len(papers_info)} 篇论文")
    print(f"总共找到 {len(authors_dict)} 位独特作者")
    print(f"总共找到 {len(affiliations_set)} 个独特机构")
    
    # 计算每位作者的平均机构数
    avg_affiliations = sum(len(affiliations) for affiliations in authors_dict.values()) / len(authors_dict) if authors_dict else 0
    print(f"每位作者平均关联 {avg_affiliations:.2f} 个机构")
    
    # 找出关联机构最多的作者
    if authors_dict:
        max_author = max(authors_dict.items(), key=lambda x: len(x[1]))
        print(f"关联机构最多的作者是 {max_author[0]}，关联了 {len(max_author[1])} 个机构")
    
    # 将作者-机构映射转换为列表格式
    authors_info = []
    for author, affiliations in authors_dict.items():
        authors_info.append({
            'author': author,
            'affiliations': list(affiliations)
        })
    
    # 1. 保存作者-机构映射
    authors_df = pd.DataFrame(authors_info)
    # 确保affiliations列存在
    if len(authors_df) > 0 and 'affiliations' in authors_df.columns:
        authors_df['affiliations'] = authors_df['affiliations'].apply(lambda x: '; '.join(x) if isinstance(x, list) else x)
    authors_file = os.path.join(output_dir, 'acl2024_authors.csv')
    authors_df.to_csv(authors_file, index=False, encoding='utf-8')
    print(f"作者信息已保存到: {authors_file}")
    
    # 检查文件是否成功写入
    if os.path.exists(authors_file):
        print(f"文件大小: {os.path.getsize(authors_file)} 字节")
    else:
        print("警告: 文件未成功创建!")
    
    # 2. 保存所有独特机构列表
    affiliations_df = pd.DataFrame(list(affiliations_set), columns=['affiliation'])
    affiliations_file = os.path.join(output_dir, 'acl2024_affiliations.csv')
    affiliations_df.to_csv(affiliations_file, index=False, encoding='utf-8')
    print(f"机构信息已保存到: {affiliations_file}")
    
    # 检查文件是否成功写入
    if os.path.exists(affiliations_file):
        print(f"文件大小: {os.path.getsize(affiliations_file)} 字节")
    else:
        print("警告: 文件未成功创建!")
    
    # 规范化论文标题的函数（确保在此作用域中可用）
    def normalize_title(title):
        if not isinstance(title, str):
            return str(title)
        return title.strip()
    
    # 3. 保存论文详细信息
    # 确保论文信息中包含规范化的标题，以便在CSV中也能区分相同paper_id的不同论文
    for paper in papers_info:
        if 'normalized_title' not in paper and 'title' in paper:
            paper['normalized_title'] = normalize_title(str(paper['title']))
    
    # 对论文信息进行去重，确保没有重复的论文
    unique_papers = []
    seen_identifiers = set()
    
    for paper in papers_info:
        paper_id = str(paper.get('paper_id', ''))
        normalized_title = str(paper.get('normalized_title', ''))
        identifier = (paper_id, normalized_title)
        
        if identifier not in seen_identifiers:
            unique_papers.append(paper)
            seen_identifiers.add(identifier)
    
    print(f"论文去重: 原始数量 {len(papers_info)}，去重后数量 {len(unique_papers)}")
    
    papers_df = pd.DataFrame(unique_papers)
    
    # 将作者和机构列表转换为字符串
    if len(papers_df) > 0:
        if 'authors' in papers_df.columns:
            papers_df['authors'] = papers_df['authors'].apply(lambda x: '; '.join(x) if isinstance(x, list) else x)
        if 'affiliations' in papers_df.columns:
            papers_df['affiliations'] = papers_df['affiliations'].apply(lambda x: '; '.join(x) if isinstance(x, list) else x)
    papers_file = os.path.join(output_dir, 'acl2024_papers.csv')
    papers_df.to_csv(papers_file, index=False, encoding='utf-8')
    print(f"论文信息已保存到: {papers_file}")
    
    # 检查文件是否成功写入
    if os.path.exists(papers_file):
        print(f"文件大小: {os.path.getsize(papers_file)} 字节")
    else:
        print("警告: 文件未成功创建!")
    
    # 注意：我们已经使用pandas的to_csv方法保存了数据，不需要重复保存


# 已将print_statistics函数的功能整合到save_results函数中


def main():
    """
    主函数
    """
    start_time = time.time()
    
    # 获取ACL 2024会议的作者和机构信息
    authors_dict, affiliations_set, papers_info = get_authors_and_affiliations('2024.acl')
    
    # 对作者和机构信息进行去重处理
    print("\n开始进行数据去重处理...")
    
    # 1. 清理机构名称中的重复部分
    print("清理机构名称...")
    
    # 规范化机构名称的函数
    def normalize_affiliation(affiliation):
        if not isinstance(affiliation, str):
            return str(affiliation)
        
        # 转换为小写进行比较
        affiliation = affiliation.strip()
        
        # 处理形如 "University A, University A" 的重复
        parts = [part.strip() for part in affiliation.split(';')]
        # 移除重复的部分
        unique_parts = []
        for part in parts:
            # 进一步处理逗号分隔的情况
            subparts = [subpart.strip() for subpart in part.split(',')]
            unique_subparts = []
            for subpart in subparts:
                if subpart and subpart not in unique_subparts:
                    unique_subparts.append(subpart)
            unique_parts.append(', '.join(unique_subparts))
        # 合并去重后的部分
        return '; '.join(unique_parts)
    
    # 创建规范化映射表，用于处理不同格式的相同机构
    affiliation_mapping = {}
    normalized_affiliations = {}
    
    # 第一步：规范化所有机构名称
    for affiliation in affiliations_set:
        normalized = normalize_affiliation(affiliation)
        normalized_lower = normalized.lower()
        
        # 记录原始形式和规范化形式的映射
        if normalized_lower in normalized_affiliations:
            # 如果已存在相似机构名称，选择较长的一个作为标准形式
            if len(normalized) > len(normalized_affiliations[normalized_lower]):
                normalized_affiliations[normalized_lower] = normalized
        else:
            normalized_affiliations[normalized_lower] = normalized
        
        # 记录原始形式到规范化形式的映射
        affiliation_mapping[affiliation] = normalized_lower
    
    # 创建最终的去重机构集合
    cleaned_affiliations_set = set(normalized_affiliations.values())
    
    # 打印去重结果
    print(f"机构去重: 原始数量 {len(affiliations_set)}，去重后数量 {len(cleaned_affiliations_set)}")
    
    # 2. 清理作者字典中的机构信息
    print("清理作者的机构信息...")
    cleaned_authors_dict = {}
    
    # 创建作者名称的规范化映射
    author_mapping = {}
    normalized_authors = {}
    
    # 规范化作者名称的函数
    def normalize_author(author):
        if not isinstance(author, str):
            return str(author)
        return author.strip()
    
    # 第一步：规范化所有作者名称
    for author in authors_dict.keys():
        normalized_author = normalize_author(author)
        author_mapping[author] = normalized_author
        normalized_authors[normalized_author] = author
    
    # 第二步：处理每个作者的机构信息
    for author, affiliations in authors_dict.items():
        normalized_author = author_mapping[author]
        cleaned_affiliations = set()
        
        for affiliation in affiliations:
            # 使用之前创建的机构映射表获取规范化的机构名称
            if affiliation in affiliation_mapping:
                # 获取规范化后的机构名称
                normalized_affiliation_key = affiliation_mapping[affiliation]
                normalized_affiliation = normalized_affiliations[normalized_affiliation_key]
                cleaned_affiliations.add(normalized_affiliation)
            else:
                # 如果在映射表中找不到，则直接规范化处理
                normalized = normalize_affiliation(affiliation)
                parts = normalized.split(';')
                for part in parts:
                    if part.strip():  # 确保不添加空字符串
                        cleaned_affiliations.add(part.strip())
        
        # 如果作者已存在，合并机构信息
        if normalized_author in cleaned_authors_dict:
            cleaned_authors_dict[normalized_author].update(cleaned_affiliations)
        else:
            cleaned_authors_dict[normalized_author] = cleaned_affiliations
    
    # 打印去重结果
    print(f"作者去重: 原始数量 {len(authors_dict)}，去重后数量 {len(cleaned_authors_dict)}")
    
    # 3. 对论文信息进行去重
    print("对论文信息进行去重...")
    unique_papers_info = []
    seen_papers = set()
    
    # 规范化论文标题的函数
    def normalize_title(title):
        if not isinstance(title, str):
            return str(title)
        return title.strip()
    
    # 创建标题规范化映射
    title_mapping = {}
    
    # 第一步：规范化所有论文标题
    for paper in papers_info:
        title = str(paper['title'])
        normalized_title = normalize_title(title)
        title_mapping[title] = normalized_title
    
    # 第二步：处理每篇论文
    for paper in papers_info:
        # 将paper_id和title转换为字符串，确保可哈希
        paper_id_str = str(paper['paper_id'])
        title_str = str(paper['title'])
        normalized_title = title_mapping.get(title_str, title_str)
        
        # 将规范化的标题保存到论文信息中，以便在CSV中区分相同paper_id的不同论文
        paper['normalized_title'] = normalized_title
        
        # 使用规范化的标题创建唯一标识
        paper_identifier = (paper_id_str, normalized_title)
        
        if paper_identifier not in seen_papers:
            # 清理论文中的作者信息
            if 'authors' in paper and isinstance(paper['authors'], list):
                cleaned_authors = []
                for author in paper['authors']:
                    # 使用规范化的作者名称
                    normalized_author = normalize_author(author)
                    if normalized_author in normalized_authors:
                        cleaned_authors.append(normalized_author)
                    else:
                        cleaned_authors.append(author)
                paper['authors'] = cleaned_authors
            
            # 清理论文中的机构信息
            if 'affiliations' in paper and isinstance(paper['affiliations'], list):
                cleaned_affiliations = []
                for affiliation in paper['affiliations']:
                    # 使用规范化的机构名称
                    if affiliation in affiliation_mapping:
                        normalized_affiliation_key = affiliation_mapping[affiliation]
                        normalized_affiliation = normalized_affiliations[normalized_affiliation_key]
                        cleaned_affiliations.append(normalized_affiliation)
                    else:
                        # 如果在映射表中找不到，则直接规范化处理
                        normalized = normalize_affiliation(affiliation)
                        cleaned_affiliations.append(normalized)
                paper['affiliations'] = cleaned_affiliations
            
            unique_papers_info.append(paper)
            seen_papers.add(paper_identifier)
    
    # 打印去重结果
    print(f"论文去重: 原始数量 {len(papers_info)}，去重后数量 {len(unique_papers_info)}")
    
    print(f"去重前: {len(authors_dict)}位作者, {len(affiliations_set)}个机构, {len(papers_info)}篇论文")
    print(f"去重后: {len(cleaned_authors_dict)}位作者, {len(cleaned_affiliations_set)}个机构, {len(unique_papers_info)}篇论文")
    
    # 保存去重后的结果
    save_results(cleaned_authors_dict, cleaned_affiliations_set, unique_papers_info)
    
    end_time = time.time()
    print(f"\n总耗时: {end_time - start_time:.2f} 秒")


if __name__ == '__main__':
    main()