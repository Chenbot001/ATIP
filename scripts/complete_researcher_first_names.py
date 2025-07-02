#!/usr/bin/env python3
"""
作者姓名补全脚本
根据 corpus_id 匹配论文信息，再根据 DOI 或 title 匹配 ACL 作者姓名来补全 first_name
"""

import pandas as pd
import re
import unicodedata
from typing import Tuple, Optional, Dict, List
import sys


def normalize_text(text: str) -> str:
    """标准化文本：去除变音符号、标点、转为小写、去除多余空格"""
    if pd.isna(text) or not text:
        return ""
    
    # 去除变音符号 (Unicode normalization)
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    
    # 转为小写
    text = text.lower()
    
    # 去除标点符号和特殊字符，只保留字母、数字和空格
    text = re.sub(r'[^\w\s]', '', text)
    
    # 去除多余空格
    text = ' '.join(text.split())
    
    return text


def is_name_incomplete(first_name: str) -> bool:
    """判断 first_name 是否不完整"""
    if pd.isna(first_name) or not first_name.strip():
        return True
    
    # 如果只有一个字符，或者以点结尾，认为是不完整的
    name = first_name.strip()
    if len(name) <= 1 or name.endswith('.'):
        return True
    
    return False


def names_match(incomplete_first: str, incomplete_last: str, 
                complete_first: str, complete_last: str) -> bool:
    """
    检查两个姓名是否匹配
    要求：last_name 完全一致，first_name 首字母一致
    """
    if pd.isna(incomplete_last) or pd.isna(complete_last):
        return False
    if pd.isna(incomplete_first) or pd.isna(complete_first):
        return False
    
    # last_name 必须完全一致（忽略大小写和空格）
    if normalize_text(incomplete_last) != normalize_text(complete_last):
        return False
    
    # first_name 首字母必须一致
    incomplete_first = incomplete_first.strip()
    complete_first = complete_first.strip()
    
    if not incomplete_first or not complete_first:
        return False
    
    # 获取首字母（忽略大小写）
    incomplete_initial = incomplete_first[0].lower()
    complete_initial = complete_first[0].lower()
    
    return incomplete_initial == complete_initial


def get_author_papers(researcher_id: int, authorships_df: pd.DataFrame) -> List[str]:
    """获取研究者的所有论文 ID"""
    author_papers = authorships_df[authorships_df['researcher_id'] == researcher_id]
    return author_papers['paper_id'].unique().tolist()


def find_matching_acl_names(doi: str, title: str, acl_data: pd.DataFrame, 
                           incomplete_first: str, incomplete_last: str) -> List[Tuple[str, str, str]]:
    """
    根据 DOI 或 title 在 ACL 数据中查找匹配的作者姓名
    返回: [(first_name, last_name, match_method), ...]
    """
    matches = []
    
    # 优先用 DOI 匹配
    if pd.notna(doi) and doi:
        doi_matches = acl_data[acl_data['paper_doi'] == doi]
        for _, row in doi_matches.iterrows():
            acl_first = row.get('first_name', '')
            acl_last = row.get('last_name', '')
            
            if names_match(incomplete_first, incomplete_last, acl_first, acl_last):
                matches.append((acl_first, acl_last, 'DOI'))
    
    # 如果 DOI 匹配没找到，用 title 匹配
    if not matches and pd.notna(title) and title:
        normalized_title = normalize_text(title)
        
        # 查找标题匹配的记录
        title_matches = acl_data[
            acl_data['paper_title'].apply(lambda x: normalize_text(str(x)) == normalized_title)
        ]
        
        for _, row in title_matches.iterrows():
            acl_first = row.get('first_name', '')
            acl_last = row.get('last_name', '')
            
            if names_match(incomplete_first, incomplete_last, acl_first, acl_last):
                matches.append((acl_first, acl_last, 'Title'))
    
    return matches


def complete_researcher_names():
    """主函数：补全研究者姓名"""
    
    # 读取数据文件
    print("正在读取数据文件...")
    
    try:
        # 读取研究者画像数据
        researchers_df = pd.read_csv('/Users/kele/实习/阿联酋/爬取/AI_Researcher_Network/data/researcher_profiles_copy.csv')
        print(f"研究者画像数据: {len(researchers_df)} 条记录")
        
        # 读取论文信息数据  
        papers_df = pd.read_csv('/Users/kele/实习/阿联酋/爬取/AI_Researcher_Network/data/paper_info.csv')
        print(f"论文信息数据: {len(papers_df)} 条记录")
        
        # 读取作者关系数据
        authorships_df = pd.read_csv('/Users/kele/实习/阿联酋/爬取/AI_Researcher_Network/data/authorships.csv')
        print(f"作者关系数据: {len(authorships_df)} 条记录")
        
        # 读取 ACL 作者数据
        acl_df = pd.read_csv('/Users/kele/实习/阿联酋/爬取/AI_Researcher_Network/data/researchers_data_with_paper.csv')
        print(f"ACL 作者数据: {len(acl_df)} 条记录")
        
    except Exception as e:
        print(f"读取数据文件时出错: {e}")
        return
    
    # 创建论文 ID 到 corpus_id 的映射
    print("创建论文映射...")
    paper_id_to_corpus = dict(zip(papers_df['s2_id'], papers_df['corpus_id']))
    
    # 统计信息
    total_researchers = len(researchers_df)
    incomplete_researchers = researchers_df[
        researchers_df['first_name'].apply(is_name_incomplete)
    ]
    total_incomplete = len(incomplete_researchers)
    
    print(f"\n=== 数据统计 ===")
    print(f"总研究者数量: {total_researchers}")
    print(f"first_name 不完整的研究者数量: {total_incomplete}")
    print(f"不完整比例: {total_incomplete/total_researchers:.2%}")
    
    # 补全处理
    print(f"\n开始补全处理...")
    
    completed_count = 0
    doi_matches = 0
    title_matches = 0
    no_papers_count = 0
    no_matches_count = 0
    
    completed_examples = []
    
    # 复制数据框用于修改
    result_df = researchers_df.copy()
    
    for idx, researcher in incomplete_researchers.iterrows():
        researcher_id = researcher['researcher_id']  # 保持为整数
        incomplete_first = researcher['first_name']
        incomplete_last = researcher['last_name']
        
        if pd.isna(incomplete_last):
            continue
        
        # 1. 根据 researcher_id 找到所有论文
        author_paper_ids = get_author_papers(researcher_id, authorships_df)
        
        if not author_paper_ids:
            no_papers_count += 1
            continue
        
        # 2. 将 paper_id 转换为 corpus_id，然后在 papers_df 中查找 DOI 和 title
        found_match = False
        match_method = ""
        completed_name = ""
        
        for paper_id in author_paper_ids:
            corpus_id = paper_id_to_corpus.get(paper_id)
            if corpus_id is None:
                continue
            
            # 查找论文信息
            paper_info = papers_df[papers_df['corpus_id'] == corpus_id]
            if paper_info.empty:
                continue
            
            paper_row = paper_info.iloc[0]
            doi = paper_row.get('DOI', '')
            title = paper_row.get('title', '')
            
            # 3. 在 ACL 数据中查找匹配的作者姓名
            matching_names = find_matching_acl_names(
                doi, title, acl_df, incomplete_first, incomplete_last
            )
            
            if matching_names:
                # 选择第一个匹配的姓名（通常 DOI 匹配优先级更高）
                complete_first, complete_last, method = matching_names[0]
                
                # 更新数据
                result_df.at[idx, 'first_name'] = complete_first
                completed_count += 1
                found_match = True
                match_method = method
                completed_name = f"{complete_first} {complete_last}"
                
                if method == 'DOI':
                    doi_matches += 1
                else:
                    title_matches += 1
                
                # 保存前几个示例
                if len(completed_examples) < 10:
                    completed_examples.append({
                        'researcher_id': str(researcher_id),
                        'original_name': f"{incomplete_first} {incomplete_last}",
                        'completed_name': completed_name,
                        'match_method': method,
                        'paper_title': title[:60] + "..." if len(title) > 60 else title
                    })
                
                break
        
        if not found_match:
            no_matches_count += 1
    
    # 输出统计结果
    print(f"\n=== 补全结果统计 ===")
    print(f"成功补全的研究者数量: {completed_count}")
    print(f"补全率: {completed_count/total_incomplete:.2%}")
    print(f"  - 通过 DOI 匹配: {doi_matches} ({doi_matches/total_incomplete:.2%})")
    print(f"  - 通过 Title 匹配: {title_matches} ({title_matches/total_incomplete:.2%})")
    print(f"未找到论文的研究者: {no_papers_count} ({no_papers_count/total_incomplete:.2%})")
    print(f"找到论文但无匹配姓名: {no_matches_count} ({no_matches_count/total_incomplete:.2%})")
    
    # 显示补全示例
    if completed_examples:
        print(f"\n=== 补全示例 ===")
        for i, example in enumerate(completed_examples, 1):
            print(f"{i}. ID: {example['researcher_id']}")
            print(f"   原姓名: {example['original_name']}")
            print(f"   补全后: {example['completed_name']}")
            print(f"   匹配方式: {example['match_method']}")
            print(f"   论文标题: {example['paper_title']}")
            print()
    
    # 保存结果
    output_file = '/Users/kele/实习/阿联酋/爬取/AI_Researcher_Network/data/researcher_profiles_completed.csv'
    result_df.to_csv(output_file, index=False)
    print(f"补全结果已保存到: {output_file}")
    
    # 验证补全后的完整性
    final_incomplete = result_df[result_df['first_name'].apply(is_name_incomplete)]
    print(f"\n=== 最终统计 ===")
    print(f"补全后仍不完整的 first_name 数量: {len(final_incomplete)}")
    print(f"最终完整率: {(total_researchers - len(final_incomplete))/total_researchers:.2%}")


if __name__ == "__main__":
    complete_researcher_names()
