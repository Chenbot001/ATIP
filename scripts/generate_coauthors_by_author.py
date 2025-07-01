#!/usr/bin/env python3
"""
生成每个作者的合作者列表CSV文件

从authorships.csv中分析每个作者的合作关系，为每个作者生成包含所有合作者信息的JSON格式字符串，
输出为coauthors_by_author.csv文件，包含researcher_id、author_name、coauthors和coauthored_papers字段。

coauthors字段为JSON格式字符串，包含该作者所有合作者的researcher_id和author_name。
coauthored_papers字段为JSON格式字符串，包含该作者参与的所有论文paper_id列表。
"""

import pandas as pd
import json
import os
from typing import List, Dict, Set, Tuple
from collections import defaultdict

def generate_coauthors_by_author(input_file: str, output_file: str) -> None:
    """
    生成按作者分组的合作者列表CSV文件
    
    Args:
        input_file: 输入的authorships.csv文件路径
        output_file: 输出的coauthors_by_author.csv文件路径
    """
    
    print(f"读取文件: {input_file}")
    
    # 读取authorships数据
    try:
        df = pd.read_csv(input_file)
        print(f"成功读取 {len(df)} 行数据")
    except Exception as e:
        print(f"读取文件出错: {e}")
        return
    
    # 检查必要的列是否存在
    required_columns = ['researcher_id', 'paper_id', 'author_name']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"缺少必要的列: {missing_columns}")
        return
    
    print("构建作者合作关系...")
    
    # 首先构建每篇论文的作者列表
    paper_authors = defaultdict(list)
    author_info = {}  # 存储作者ID到姓名的映射
    
    for _, row in df.iterrows():
        researcher_id = int(row['researcher_id']) if pd.notna(row['researcher_id']) else None
        paper_id = int(row['paper_id']) if pd.notna(row['paper_id']) else None
        author_name = str(row['author_name']) if pd.notna(row['author_name']) else None
        
        if researcher_id and paper_id and author_name:
            paper_authors[paper_id].append(researcher_id)
            author_info[researcher_id] = author_name
    
    print(f"发现 {len(paper_authors)} 篇论文，{len(author_info)} 个不同作者")
    
    # 构建每个作者的合作者集合和合作论文集合
    author_coauthors = defaultdict(set)  # 每个作者的合作者ID集合
    author_papers = defaultdict(set)     # 每个作者参与的论文ID集合
    
    # 遍历每篇论文，建立合作关系
    for paper_id, authors in paper_authors.items():
        # 为该论文的每个作者记录论文ID
        for author_id in authors:
            author_papers[author_id].add(paper_id)
        
        # 为该论文的每个作者建立与其他作者的合作关系
        for i, author1 in enumerate(authors):
            for j, author2 in enumerate(authors):
                if i != j:  # 不包括自己
                    author_coauthors[author1].add(author2)
    
    print("生成合作者列表...")
    
    # 生成最终结果
    coauthors_data = []
    total_authors = len(author_info)
    
    for i, (researcher_id, author_name) in enumerate(author_info.items()):
        # 获取该作者的合作者列表
        coauthor_ids = author_coauthors.get(researcher_id, set())
        coauthors = []
        
        for coauthor_id in coauthor_ids:
            coauthor_name = author_info.get(coauthor_id, "Unknown")
            coauthors.append({
                'researcher_id': coauthor_id,
                'author_name': coauthor_name
            })
        
        # 按researcher_id排序，确保结果一致性
        coauthors.sort(key=lambda x: x['researcher_id'])
        
        # 获取该作者参与的论文列表
        papers = list(author_papers.get(researcher_id, set()))
        papers.sort()  # 排序确保一致性
        
        # 转换为JSON字符串
        coauthors_json = json.dumps(coauthors, ensure_ascii=False)
        papers_json = json.dumps(papers, ensure_ascii=False)
        
        coauthors_data.append({
            'researcher_id': researcher_id,
            'author_name': author_name,
            'coauthors': coauthors_json,
            'coauthored_papers': papers_json
        })
        
        # 显示进度
        if (i + 1) % 1000 == 0 or (i + 1) == total_authors:
            print(f"已处理 {i + 1}/{total_authors} 个作者 ({(i + 1) / total_authors * 100:.1f}%)")
    
    # 创建DataFrame并按researcher_id排序
    result_df = pd.DataFrame(coauthors_data)
    result_df = result_df.sort_values('researcher_id').reset_index(drop=True)
    
    print(f"保存结果到: {output_file}")
    result_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"完成! 共处理 {len(result_df)} 个作者")
    
    # 显示统计信息
    print("\n=== 统计信息 ===")
    print(f"作者总数: {len(result_df)}")
    
    # 统计合作者数量分布
    coauthor_counts = []
    paper_counts = []
    
    for _, row in result_df.iterrows():
        coauthors = json.loads(row['coauthors'])
        papers = json.loads(row['coauthored_papers'])
        coauthor_counts.append(len(coauthors))
        paper_counts.append(len(papers))
    
    coauthor_counts_series = pd.Series(coauthor_counts)
    paper_counts_series = pd.Series(paper_counts)
    
    print(f"平均合作者数量: {coauthor_counts_series.mean():.2f}")
    print(f"合作者数量中位数: {coauthor_counts_series.median():.0f}")
    print(f"最多合作者数量: {coauthor_counts_series.max()}")
    print(f"最少合作者数量: {coauthor_counts_series.min()}")
    
    print(f"平均论文数量: {paper_counts_series.mean():.2f}")
    print(f"论文数量中位数: {paper_counts_series.median():.0f}")
    print(f"最多论文数量: {paper_counts_series.max()}")
    print(f"最少论文数量: {paper_counts_series.min()}")
    
    # 找出合作者最多的作者
    max_coauthors_idx = coauthor_counts.index(max(coauthor_counts))
    max_row = result_df.iloc[max_coauthors_idx]
    max_coauthors = json.loads(max_row['coauthors'])
    
    print(f"\n合作者最多的作者:")
    print(f"作者ID: {max_row['researcher_id']}")
    print(f"作者姓名: {max_row['author_name']}")
    print(f"合作者数量: {len(max_coauthors)}")
    
    # 显示前3个示例
    print("\n=== 前3个作者示例 ===")
    for i in range(min(3, len(result_df))):
        row = result_df.iloc[i]
        coauthors = json.loads(row['coauthors'])
        papers = json.loads(row['coauthored_papers'])
        
        print(f"\n作者ID: {row['researcher_id']}")
        print(f"作者姓名: {row['author_name']}")
        print(f"合作者数量: {len(coauthors)}")
        print(f"参与论文数量: {len(papers)}")
        
        if coauthors:
            print("前3个合作者:")
            for j, coauthor in enumerate(coauthors[:3]):
                print(f"  {j+1}. ID: {coauthor['researcher_id']}, 姓名: {coauthor['author_name']}")
        else:
            print("无合作者（单作者论文）")

def main():
    """主函数"""
    
    # 文件路径设置
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    input_file = os.path.join(data_dir, 'authorships.csv')
    output_file = os.path.join(data_dir, 'coauthors_by_author.csv')
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"输入文件不存在: {input_file}")
        return
    
    print("=== 生成每个作者的合作者列表 ===")
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print()
    
    # 生成合作者列表
    generate_coauthors_by_author(input_file, output_file)

if __name__ == "__main__":
    main()
