# 作者合作关系生成脚本使用说明

## 脚本简介

`generate_coauthors_by_author.py` 脚本用于从 `authorships.csv` 文件中分析每位作者与其合作者之间的合作关系，统计合作次数并按次数排序，生成详细的作者合作关系CSV文件。

## 功能特性

- **合作关系分析**: 分析每位作者与其所有合作者的合作关系
- **合作次数统计**: 统计每对作者之间的合作论文数量
- **智能排序**: 按合作次数对每位作者的合作者进行降序排序
- **排名标记**: 为每位作者的合作者列表添加排名信息
- **完整信息**: 保留作者和合作者的ID、姓名信息
- **高效处理**: 优化算法处理大规模数据集

## 输入文件

- **文件路径**: `data/authorships.csv`
- **必需字段**:
  - `researcher_id`: 研究者ID
  - `paper_id`: 论文ID
  - `author_name`: 作者姓名

## 输出文件

- **文件路径**: `data/coauthors_by_author.csv`
- **字段说明**:
  - `researcher_id`: 本作者ID
  - `author_name`: 本作者姓名
  - `coauthor_id`: 合作者ID
  - `coauthor_name`: 合作者姓名
  - `num_collaborations`: 与该合作者合作的论文数量
  - `rank`: 合作者在该作者的合作列表中的排名（按合作次数降序）

### 输出格式示例

```csv
researcher_id,author_name,coauthor_id,coauthor_name,num_collaborations,rank
1678591,Massimo Poesio,2165202,J. Hitzeman,6,1
1678591,Massimo Poesio,11545402,Silviu Paun,6,2
1678591,Massimo Poesio,144010750,Jon Chamberlain,6,3
1678591,Massimo Poesio,2993548,Udo Kruschwitz,6,4
1678591,Massimo Poesio,3437950,Juntao Yu,6,5
1678591,Massimo Poesio,2067925708,Rahul Mehta,2,6
```

## 使用方法

### 基本用法

```bash
cd /Users/kele/实习/阿联酋/爬取/AI_Researcher_Network
python scripts/generate_coauthors_by_author.py
```

### Python代码中使用

```python
import pandas as pd

# 读取生成的合作关系数据
df = pd.read_csv('data/coauthors_by_author.csv')

# 查询某位作者的所有合作者（按合作次数排序）
researcher_id = 1678591
author_collaborators = df[df['researcher_id'] == researcher_id]

print(f"作者 {researcher_id} 的合作者列表:")
for _, row in author_collaborators.head(10).iterrows():  # 显示前10个合作者
    print(f"{row['rank']}. {row['coauthor_name']} - {row['num_collaborations']}次合作")

# 查找某对作者之间的合作次数
author1_id = 1753344  # Maosong Sun
author2_id = 49293587  # Zhiyuan Liu
collaboration = df[(df['researcher_id'] == author1_id) & (df['coauthor_id'] == author2_id)]
if len(collaboration) > 0:
    print(f"作者 {author1_id} 与 {author2_id} 合作了 {collaboration.iloc[0]['num_collaborations']} 次")

# 统计合作最多的作者对
max_collaborations = df['num_collaborations'].max()
most_collaborative_pairs = df[df['num_collaborations'] == max_collaborations]
print(f"合作最多的作者对（{max_collaborations}次合作）:")
for _, pair in most_collaborative_pairs.iterrows():
    print(f"- {pair['author_name']} 与 {pair['coauthor_name']}")
```

## 处理结果统计

基于最新处理结果（2,556,348条合作关系记录）:

### 基本统计
- **总合作关系记录数**: 2,556,348条
- **独特作者数**: 55,881人
- **独特合作者数**: 55,881人
- **平均每位作者的合作者数量**: 45.75人
- **每位作者合作者数量中位数**: 6人
- **最多合作者数量**: 2,645人
- **最少合作者数量**: 1人

### 合作次数亮点
- **最高合作次数**: 104次（Maosong Sun 与 Zhiyuan Liu）
- **高频合作对**: 有多对作者合作超过60次
- **大部分合作**: 以1-2次合作为主

### 数据规模
- **文件大小**: 约131MB
- **处理时间**: 约5-10分钟（取决于硬件配置）
- **内存需求**: 约2GB RAM

## 应用场景

### 学术网络分析
1. **核心合作者识别**: 找出每位作者的核心合作伙伴
2. **合作强度分析**: 基于合作次数评估合作关系强度
3. **学术团队分析**: 识别固定的研究团队和合作模式
4. **跨机构合作**: 分析不同机构间的合作关系

### 推荐系统
1. **合作者推荐**: 基于现有合作网络推荐潜在合作者
2. **研究方向推荐**: 根据合作者的研究方向推荐新的研究领域
3. **团队组建**: 为新项目推荐合适的团队成员

## 注意事项

- 处理大文件时需要足够的内存空间（推荐8GB以上）
- 生成的文件较大（131MB），请确保有足够的磁盘空间
- 处理时间较长，建议在服务器或高性能计算机上运行
- 输出文件按作者ID排序，便于后续数据处理和分析
