#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
示例脚本：爬取其他会议的作者和机构信息
"""

from acl_authors_affiliations import get_authors_and_affiliations, save_results, print_statistics
import time
import os

def crawl_venue(venue_id, output_subdir):
    """
    爬取指定会议的作者和机构信息
    
    参数:
        venue_id (str): 会议标识，例如 '2023.acl'
        output_subdir (str): 输出子目录名
    """
    print(f"\n开始爬取 {venue_id} 会议数据...")
    start_time = time.time()
    
    # 获取会议的作者和机构信息
    authors_dict, affiliations_set, papers_info = get_authors_and_affiliations(venue_id)
    
    # 创建输出目录
    output_dir = os.path.join("./output", output_subdir)
    
    # 保存结果
    save_results(authors_dict, affiliations_set, papers_info, output_dir)
    
    # 打印统计信息
    print_statistics(authors_dict, affiliations_set, papers_info)
    
    end_time = time.time()
    print(f"爬取 {venue_id} 总耗时: {end_time - start_time:.2f} 秒\n")

def main():
    """
    主函数：爬取多个会议的数据
    """
    # 定义要爬取的会议列表
    venues = [
        ('2023.acl', 'acl2023'),  # ACL 2023
        ('2023.emnlp', 'emnlp2023'),  # EMNLP 2023
        ('2024.eacl', 'eacl2024'),  # EACL 2024
    ]
    
    for venue_id, output_subdir in venues:
        crawl_venue(venue_id, output_subdir)

if __name__ == '__main__':
    main()