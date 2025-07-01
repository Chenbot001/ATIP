#!/usr/bin/env python3
"""
生成每篇论文的合作者列表CSV文件

从authorships.csv中按paper_id分组，为每篇论文生成包含所有合作者信息的JSON格式字符串，
输出为coauthors_by_paper.csv文件，包含paper_id和coauthors两个字段。

coauthors字段为JSON格式字符串，包含该论文所有作者的researcher_id和author_name。
"""

import pandas as pd
import json
import os
from typing import List, Dict

def generate_coauthors_by_paper(input_file: str, output_file: str) -> None:
    """
    生成按论文分组的合作者列表CSV文件
    
    Args:
        input_file: 输入的authorships.csv文件路径
        output_file: 输出的coauthors_by_paper.csv文件路径
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
    
    print("按paper_id分组处理合作者信息...")
    
    # 按paper_id分组，为每篇论文生成合作者列表
    coauthors_data = []
    
    grouped = df.groupby('paper_id')
    total_papers = len(grouped)
    
    for i, (paper_id, group) in enumerate(grouped):
        # 为每篇论文创建合作者列表
        coauthors = []
        
        for _, row in group.iterrows():
            coauthor_info = {
                'researcher_id': int(row['researcher_id']) if pd.notna(row['researcher_id']) else None,
                'author_name': str(row['author_name']) if pd.notna(row['author_name']) else None
            }
            coauthors.append(coauthor_info)
        
        # 将合作者列表转换为JSON字符串
        coauthors_json = json.dumps(coauthors, ensure_ascii=False)
        
        coauthors_data.append({
            'paper_id': int(paper_id),
            'coauthors': coauthors_json
        })
        
        # 显示进度
        if (i + 1) % 1000 == 0 or (i + 1) == total_papers:
            print(f"已处理 {i + 1}/{total_papers} 篇论文 ({(i + 1) / total_papers * 100:.1f}%)")
    
    # 创建DataFrame并保存
    result_df = pd.DataFrame(coauthors_data)
    
    print(f"保存结果到: {output_file}")
    result_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"完成! 共处理 {len(result_df)} 篇论文")
    
    # 显示一些统计信息
    print("\n=== 统计信息 ===")
    print(f"论文总数: {len(result_df)}")
    
    # 统计合作者数量分布
    coauthor_counts = []
    for coauthors_json in result_df['coauthors']:
        coauthors = json.loads(coauthors_json)
        coauthor_counts.append(len(coauthors))
    
    coauthor_counts_series = pd.Series(coauthor_counts)
    print(f"平均合作者数量: {coauthor_counts_series.mean():.2f}")
    print(f"合作者数量中位数: {coauthor_counts_series.median():.0f}")
    print(f"最多合作者数量: {coauthor_counts_series.max()}")
    print(f"最少合作者数量: {coauthor_counts_series.min()}")
    
    # 显示前3个示例
    print("\n=== 前3个示例 ===")
    for i in range(min(3, len(result_df))):
        row = result_df.iloc[i]
        coauthors = json.loads(row['coauthors'])
        print(f"\n论文ID: {row['paper_id']}")
        print(f"合作者数量: {len(coauthors)}")
        print("合作者列表:")
        for j, coauthor in enumerate(coauthors):
            print(f"  {j+1}. ID: {coauthor['researcher_id']}, 姓名: {coauthor['author_name']}")

def main():
    """主函数"""
    
    # 文件路径设置
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    input_file = os.path.join(data_dir, 'authorships.csv')
    output_file = os.path.join(data_dir, 'coauthors_by_paper.csv')
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"输入文件不存在: {input_file}")
        return
    
    print("=== 生成每篇论文的合作者列表 ===")
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print()
    
    # 生成合作者列表
    generate_coauthors_by_paper(input_file, output_file)

if __name__ == "__main__":
    main()
