from acl_anthology import Anthology
from acl_anthology.people.name import Name, NameSpecification
import pandas as pd
import os
import sys
import requests
import time
import logging
import openreview
import json
import random
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# 配置日志 - 修改配置使其能正确记录信息，并降低日志级别
log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'openreview_errors.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,  # 降低日志级别，记录更多信息
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# 添加一条启动日志，验证日志系统是否工作
logging.info("脚本启动: 日志系统初始化")

# 创建OpenReview客户端，使用增强版本，包含重试机制
class EnhancedOpenReviewClient:
    def __init__(self, base_url='https://api.openreview.net', cache_file='data/openreview_cache.json'):
        self.client = openreview.Client(baseurl=base_url)
        self.base_url = base_url
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()
        self.request_count = 0
        self.last_request_time = 0
        
        # 确保缓存目录存在
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        logging.info(f"增强版OpenReview客户端初始化，缓存文件: {self.cache_file}")
    
    def _load_cache(self):
        """加载缓存文件"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    logging.info(f"成功加载缓存，包含 {len(cache_data)} 条记录")
                    return cache_data
            except Exception as e:
                logging.error(f"加载缓存失败: {str(e)}")
                return {}
        logging.info("缓存文件不存在，创建新的缓存")
        return {}
    
    def _save_cache(self):
        """保存缓存到文件"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False)
            # 每100次请求后记录一次缓存大小
            if self.request_count % 100 == 0:
                logging.info(f"已保存缓存，当前包含 {len(self.cache)} 条记录")
        except Exception as e:
            logging.error(f"保存缓存失败: {str(e)}")
    
    def _rate_limit(self):
        """实现请求速率限制"""
        current_time = time.time()
        if self.request_count > 0:
            elapsed = current_time - self.last_request_time
            if elapsed < 1.5:  # 每次请求间隔至少1.5秒
                sleep_time = 1.5 - elapsed + random.random() * 0.5  # 添加随机抖动
                logging.debug(f"限流: 暂停 {sleep_time:.2f} 秒")
                time.sleep(sleep_time)
                
        self.last_request_time = time.time()
        self.request_count += 1
        
        # 每20次请求后暂停一段时间
        if self.request_count % 20 == 0:
            pause_time = 5 + random.random() * 3  # 5-8秒随机暂停
            logging.info(f"已发送{self.request_count}个请求，暂停{pause_time:.2f}秒...")
            time.sleep(pause_time)
    
    def search_profiles(self, **kwargs):
        """带重试和缓存的配置文件搜索"""
        # 生成缓存键
        cache_key = f"search_profiles_{json.dumps(kwargs, sort_keys=True)}"
        
        # 检查缓存
        if cache_key in self.cache:
            logging.info(f"从缓存中获取配置文件搜索结果: {kwargs}")
            profiles_data = self.cache[cache_key]
            
            # 将字典数据转换回Profile对象
            if profiles_data is not None and isinstance(profiles_data, list):
                try:
                    profiles = []
                    for p in profiles_data:
                        if p is not None:
                            try:
                                profiles.append(openreview.Profile.from_json(p))
                            except Exception as e:
                                logging.warning(f"无法解析缓存的Profile数据: {str(e)}")
                    return profiles
                except Exception as e:
                    logging.warning(f"缓存数据解析失败: {str(e)}")
                    # 如果转换失败，删除缓存并重新获取
                    del self.cache[cache_key]
            elif profiles_data is None:
                return None
        
        # 应用请求速率限制
        self._rate_limit()
        
        # 记录API请求
        logging.info(f"向OpenReview API发送profiles请求: {kwargs}")
        
        # 带重试的API请求
        max_retries = 5
        for attempt in range(max_retries):
            try:
                profiles = self.client.search_profiles(**kwargs)
                
                # 缓存结果
                if profiles is not None:
                    # 将Profile对象转换为可序列化的字典
                    profiles_data = [p.to_json() if p else None for p in profiles]
                    logging.info(f"API返回了 {len(profiles)} 个配置文件")
                else:
                    profiles_data = None
                    logging.info("API没有返回配置文件")
                    
                self.cache[cache_key] = profiles_data
                self._save_cache()
                
                return profiles
                
            except openreview.OpenReviewException as e:
                if "429" in str(e):  # Too Many Requests
                    wait_time = (2 ** attempt) * 2 + random.random() * 3
                    logging.warning(f"请求过多 (429)，等待 {wait_time:.2f} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                elif "400" in str(e):  # Bad Request
                    logging.warning(f"请求格式错误 (400): {str(e)}")
                    # 缓存空结果避免重复请求
                    self.cache[cache_key] = None
                    self._save_cache()
                    return None
                else:
                    logging.error(f"OpenReview API错误: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        return None
            except Exception as e:
                logging.error(f"请求异常: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    return None
        
        return None
    
    def get_profile(self, profile_id):
        """带重试和缓存的获取配置文件"""
        # 生成缓存键
        cache_key = f"get_profile_{profile_id}"
        
        # 检查缓存
        if cache_key in self.cache:
            logging.info(f"从缓存中获取配置文件: {profile_id}")
            profile_data = self.cache[cache_key]
            
            # 将字典数据转换回Profile对象
            if profile_data is not None:
                try:
                    profile = openreview.Profile.from_json(profile_data)
                    return profile
                except Exception as e:
                    logging.warning(f"缓存数据解析失败: {str(e)}")
                    # 如果转换失败，删除缓存并重新获取
                    del self.cache[cache_key]
            elif profile_data is None:
                return None
        
        # 应用请求速率限制
        self._rate_limit()
        
        # 记录API请求
        logging.info(f"向OpenReview API发送profile请求: {profile_id}")
        
        # 带重试的API请求
        max_retries = 5
        for attempt in range(max_retries):
            try:
                profile = self.client.get_profile(profile_id)
                
                # 缓存结果
                if profile is not None:
                    profile_data = profile.to_json()
                    logging.info(f"找到配置文件: {profile_id}")
                else:
                    profile_data = None
                    logging.info(f"未找到配置文件: {profile_id}")
                
                self.cache[cache_key] = profile_data
                self._save_cache()
                
                return profile
                
            except openreview.OpenReviewException as e:
                if "429" in str(e):  # Too Many Requests
                    wait_time = (2 ** attempt) * 2 + random.random() * 3
                    logging.warning(f"请求过多 (429)，等待 {wait_time:.2f} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                elif "404" in str(e) or "not found" in str(e).lower():
                    logging.info(f"配置文件未找到: {profile_id}")
                    # 缓存空结果避免重复请求
                    self.cache[cache_key] = None
                    self._save_cache()
                    return None
                else:
                    logging.error(f"OpenReview API错误: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        return None
            except Exception as e:
                logging.error(f"请求异常: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    return None
        
        return None
    
    def get_notes(self, **kwargs):
        """带重试和缓存的获取笔记，避免原始客户端的重试问题"""
        # 对于重要的查询，也实现缓存以提高效率
        cache_key = None
        try:
            # 只对包含authorids的查询进行缓存
            if 'content' in kwargs and 'authorids' in kwargs['content']:
                author_id = kwargs['content']['authorids']
                cache_key = f"get_notes_{author_id}"
                
                # 检查缓存
                if cache_key in self.cache:
                    logging.info(f"从缓存中获取笔记: {author_id}")
                    notes_data = self.cache[cache_key]
                    
                    if notes_data is not None:
                        try:
                            notes = []
                            for n in notes_data:
                                if n is not None:
                                    notes.append(openreview.Note.from_json(n))
                            return notes
                        except Exception as e:
                            logging.warning(f"笔记缓存解析失败: {str(e)}")
                            # 如果解析失败，删除缓存并重新获取
                            del self.cache[cache_key]
        except Exception as e:
            logging.warning(f"处理笔记缓存键时出错: {str(e)}")
        
        # 应用请求速率限制
        self._rate_limit()
        
        # 使用直接HTTP请求而不是客户端的get_notes方法，避免内部重试逻辑
        endpoint = 'notes'
        params = {}
        
        # 将kwargs转换为API参数
        for key, value in kwargs.items():
            if key == 'content':
                for content_key, content_value in value.items():
                    params[f"content.{content_key}"] = content_value
            else:
                params[key] = value
        
        url = urljoin(self.base_url, endpoint)
        logging.info(f"向OpenReview API发送直接notes请求: URL={url}, params={params}")
        
        # 带重试的直接API请求
        max_retries = 3  # 减少重试次数
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    params=params,
                    headers={'User-Agent': 'EnhancedOpenReviewClient/1.0'},
                    timeout=30
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        notes = [openreview.Note.from_json(n) for n in data.get('notes', [])]
                        
                        # 如果有缓存键且包含authorids查询，缓存结果
                        if cache_key:
                            try:
                                notes_data = [n.to_json() if n else None for n in notes]
                                self.cache[cache_key] = notes_data
                                self._save_cache()
                            except Exception as e:
                                logging.warning(f"缓存笔记时出错: {str(e)}")
                        
                        logging.info(f"API返回了 {len(notes)} 个笔记")
                        return notes
                    except json.JSONDecodeError:
                        logging.error("API返回了无效的JSON数据")
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            continue
                        else:
                            return []
                        
                elif response.status_code == 429:  # Too Many Requests
                    wait_time = (2 ** attempt) * 3 + random.random() * 2
                    logging.warning(f"笔记请求过多 (429)，等待 {wait_time:.2f} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code in [400, 404]:
                    logging.warning(f"OpenReview API错误 ({response.status_code}): {response.text}")
                    return []  # 对于400/404错误直接返回空列表，不再重试
                else:
                    logging.error(f"OpenReview API错误: 状态码={response.status_code}, 响应={response.text}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        return []
                        
            except requests.exceptions.RequestException as e:
                logging.error(f"HTTP请求异常: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    return []
        
        return []

# 创建增强版OpenReview客户端
client = EnhancedOpenReviewClient(base_url='https://api.openreview.net', cache_file='data/openreview_cache.json')
print("已初始化增强版OpenReview客户端，包含速率限制和缓存功能")

# 定义一个函数来将数据添加到研究者CSV文件中
def save_researchers_to_csv(researchers_df, csv_file='data/researchers_data.csv'):
    # 检查文件是否存在，如果不存在则创建一个新的DataFrame
    file_exists = os.path.isfile(csv_file)
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    
    # Save the DataFrame to CSV
    mode = 'a' if file_exists else 'w'
    header = not file_exists
    
    researchers_df.to_csv(csv_file, mode=mode, header=header, index=False, encoding='utf-8')
    print(f"Data saved to {csv_file}")

# 使用增强版OpenReview客户端的OpenReview ID查找函数
def get_openreview_id(author_full_name=None, paper_title=None, first_name=None, last_name=None, acl_author_id=None):
    """
    使用增强版OpenReview客户端查找作者的OpenReview ID
    
    Args:
        author_full_name: 作者全名
        paper_title: 论文标题 (可选，用于验证)
        first_name: 作者名
        last_name: 作者姓
        acl_author_id: ACL作者ID
        
    Returns:
        str or None: OpenReview ID 或 None
    """
    # 确保我们至少有作者的姓和名
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
    first_name = first_name.strip()
    last_name = last_name.strip()
    full_name = f"{first_name} {last_name}"
    
    logging.info(f"开始查找作者OpenReview ID: {full_name}")
    
    try:
        # 方法1: 使用增强版客户端按名字搜索
        profiles = None
        try:
            # 使用完整姓名搜索
            profiles = client.search_profiles(fullname=full_name)
            
            # 如果没有找到结果，尝试单独搜索姓和名
            if not profiles:
                logging.info(f"使用完整姓名未找到作者 '{full_name}'，尝试单独搜索姓和名")
                profiles = client.search_profiles(first=first_name, last=last_name)
                
        except Exception as e:
            logging.warning(f"OpenReview API搜索异常: {str(e)}")
        
        # 如果找到了配置文件
        if profiles and len(profiles) > 0:
            # 如果只找到一个配置文件，直接返回
            if len(profiles) == 1:
                profile_id = profiles[0].id
                logging.info(f"找到唯一匹配的配置文件: {profile_id} (作者: {full_name})")
                return profile_id
            
            # 如果找到多个配置文件，尝试找到最佳匹配
            logging.info(f"找到多个匹配的配置文件 ({len(profiles)})，寻找最佳匹配")
            best_profile = None
            max_score = -1
            
            for profile in profiles:
                score = 0
                profile_names = []
                if hasattr(profile, 'content') and profile.content:
                    profile_names = profile.content.get('names', [])
                
                # 检查配置文件中的名字是否匹配
                for name_obj in profile_names:
                    profile_first = name_obj.get('first', '').lower()
                    profile_last = name_obj.get('last', '').lower()
                    
                    if first_name.lower() in profile_first or profile_first in first_name.lower():
                        score += 1
                    
                    if last_name.lower() in profile_last or profile_last in last_name.lower():
                        score += 2  # 姓氏匹配权重更高
                
                # 如果提供了论文标题，检查作者的论文
                if paper_title and score > 0 and hasattr(profile, 'id'):
                    try:
                        # 获取作者的论文，但如果不存在论文也没关系
                        author_id = profile.id
                        papers = client.get_notes(content={'authorids': author_id})
                        
                        # 如果找到了论文，增加匹配分数
                        if papers:
                            for paper in papers:
                                title = ''
                                if hasattr(paper, 'content') and paper.content and 'title' in paper.content:
                                    title = paper.content.get('title', '')
                                if title and paper_title.lower() in title.lower():
                                    score += 3  # 论文标题匹配权重更高
                                    # 一旦找到匹配，立即退出循环，避免进一步请求
                                    break
                                # 只检查最多3篇论文，避免过多请求
                                if papers.index(paper) >= 2:
                                    break
                    except Exception as e:
                        logging.warning(f"获取作者论文时出错，忽略论文匹配: {str(e)}")
                        # 忽略论文匹配错误，继续使用其他标准
                
                if score > max_score:
                    max_score = score
                    best_profile = profile
            
            if best_profile and max_score > 0 and hasattr(best_profile, 'id'):
                logging.info(f"找到最佳匹配配置文件: {best_profile.id} (分数: {max_score}, 作者: {full_name})")
                return best_profile.id
            
            # 如果没有找到明显最佳的配置文件，返回第一个
            if hasattr(profiles[0], 'id'):
                logging.info(f"返回第一个匹配的配置文件: {profiles[0].id} (作者: {full_name})")
                return profiles[0].id
        
        # 方法2: 如果客户端搜索失败，尝试构建可能的ID
        if not profiles:
            logging.info(f"未通过API搜索找到作者 '{full_name}'，尝试构建可能的ID")
            # 构建一些可能的ID格式
            potential_ids = [
                f"~{first_name}_{last_name}1",
                f"~{first_name.lower()}_{last_name.lower()}1",
                f"~{first_name}{last_name}1"
            ]
            
            for potential_id in potential_ids:
                try:
                    # 使用OpenReview客户端检查ID是否存在
                    profile = client.get_profile(potential_id)
                    if profile:
                        logging.info(f"通过ID构建找到配置文件: {potential_id} (作者: {full_name})")
                        return potential_id
                except Exception as e:
                    logging.debug(f"尝试ID '{potential_id}' 未找到: {str(e)}")
                    continue  # ID不存在，继续尝试
    
    except Exception as e:
        logging.error(f"搜索作者 '{full_name}' 时出错: {str(e)}")
    
    logging.info(f"未能为作者 {full_name} 找到OpenReview ID")
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
        try:
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
        except Exception as e:
            # 更详细地记录处理单个作者时的错误
            full_name = f"{first_name} {last_name}" if 'first_name' in locals() and 'last_name' in locals() else str(author.name)
            logging.error(f"处理作者 '{full_name}' 数据时出错: {str(e)}", exc_info=True)
            # 返回部分信息，避免丢失数据
            return {
                'researcher_id': None,
                'first_name': first_name if 'first_name' in locals() else '',
                'last_name': last_name if 'last_name' in locals() else '',
                'error': str(e)
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
        with ThreadPoolExecutor(max_workers=5) as executor:  # 减少线程数，防止API过载
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
                        
                    # 每处理100个作者保存一次结果，防止数据丢失
                    if processed_authors % 100 == 0:
                        partial_df = pd.DataFrame(researchers_data)
                        save_researchers_to_csv(partial_df, csv_file="data/researcher_data_partial.csv")
                        logging.info(f"已保存部分结果，已处理: {processed_authors}/{total_authors} 作者")
                        
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
    parser.add_argument('--threads', type=int, default=5,
                        help='线程数量 (默认: 5)')
    parser.add_argument('--batch-size', type=int, default=100,
                        help='每次保存的批次大小 (默认: 100)')
    args = parser.parse_args()
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    try:
        # 尝试从本地仓库初始化anthology
        start_time = time.time()
        print(f"开始处理，时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"开始处理数据，时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
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
        logging.warning("程序被用户中断")
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        logging.error(f"执行过程中出现未处理的错误: {str(e)}", exc_info=True)
        print(f"遇到错误: {str(e)}")
        sys.exit(1)
    finally:
        # 记录脚本结束
        logging.info(f"脚本执行结束，时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()



