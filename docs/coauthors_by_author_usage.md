# 作者合作者列表生成脚本使用说明

## 脚本简介

`generate_coauthors_by_author.py` 脚本用于从 `authorships.csv` 文件中分析每个作者的合作关系，并生成包含所有合作者信息的CSV文件。与 `generate_coauthors_by_paper.py` 不同，此脚本是以作者为维度进行分析。

## 功能特性

- **按作者分组**: 将 `authorships.csv` 中的作者信息按 `researcher_id` 分组
- **合作关系分析**: 通过共同参与论文建立作者间的合作关系
- **JSON格式输出**: 每个作者的合作者列表和参与论文列表均以JSON字符串形式存储
- **去重处理**: 同一合作者只出现一次，避免重复
- **完整信息保留**: 保留每个合作者的 `researcher_id` 和 `author_name`
- **进度显示**: 处理过程中显示实时进度
- **统计信息**: 提供详细的合作关系统计分析

## 输入文件

- **文件路径**: `data/authorships.csv`
- **必需字段**:
  - `researcher_id`: 研究者ID
  - `paper_id`: 论文ID
  - `author_name`: 作者姓名

## 输出文件

- **文件路径**: `data/coauthors_by_author.csv`
- **字段说明**:
  - `researcher_id`: 研究者ID
  - `author_name`: 作者姓名
  - `coauthors`: JSON格式的合作者列表字符串
  - `coauthored_papers`: JSON格式的参与论文ID列表字符串

### 输出格式示例

```csv
researcher_id,author_name,coauthors,coauthored_papers
1678473,Wenjie Pei,"[{""researcher_id"": 1753529, ""author_name"": ""Ruifeng Xu""}, {""researcher_id"": 144691693, ""author_name"": ""Bin Liang""}]","[248780517]"
```

### JSON结构示例

#### coauthors字段
```json
[
    {
        "researcher_id": 1753529,
        "author_name": "Ruifeng Xu"
    },
    {
        "researcher_id": 144691693,
        "author_name": "Bin Liang"
    }
]
```

#### coauthored_papers字段
```json
[248780517, 259064226]
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
import json

# 读取生成的作者合作者数据
df = pd.read_csv('data/coauthors_by_author.csv')

# 查询某个作者的合作者信息
researcher_id = 1678473
row = df[df['researcher_id'] == researcher_id].iloc[0]

# 解析合作者列表
coauthors = json.loads(row['coauthors'])
papers = json.loads(row['coauthored_papers'])

print(f"作者 {row['author_name']} (ID: {researcher_id}) 的合作关系:")
print(f"- 合作者数量: {len(coauthors)}")
print(f"- 参与论文数量: {len(papers)}")

print("合作者列表:")
for coauthor in coauthors:
    print(f"- ID: {coauthor['researcher_id']}, 姓名: {coauthor['author_name']}")

print(f"参与论文ID: {papers}")
```

### 高级查询示例

```python
import pandas as pd
import json
from collections import Counter

# 读取数据
df = pd.read_csv('data/coauthors_by_author.csv')

# 1. 找出合作者最多的前10个作者
coauthor_counts = []
for _, row in df.iterrows():
    coauthors = json.loads(row['coauthors'])
    coauthor_counts.append((row['researcher_id'], row['author_name'], len(coauthors)))

top_collaborators = sorted(coauthor_counts, key=lambda x: x[2], reverse=True)[:10]
print("合作者最多的前10个作者:")
for rank, (rid, name, count) in enumerate(top_collaborators, 1):
    print(f"{rank}. {name} (ID: {rid}): {count} 个合作者")

# 2. 找出参与论文最多的前10个作者
paper_counts = []
for _, row in df.iterrows():
    papers = json.loads(row['coauthored_papers'])
    paper_counts.append((row['researcher_id'], row['author_name'], len(papers)))

top_productive = sorted(paper_counts, key=lambda x: x[2], reverse=True)[:10]
print("\n参与论文最多的前10个作者:")
for rank, (rid, name, count) in enumerate(top_productive, 1):
    print(f"{rank}. {name} (ID: {rid}): {count} 篇论文")

# 3. 分析合作关系密度
total_collaborations = sum(len(json.loads(row['coauthors'])) for _, row in df.iterrows())
print(f"\n总合作关系数: {total_collaborations}")
print(f"平均每个作者的合作者数量: {total_collaborations / len(df):.2f}")
```

## 处理结果统计

基于最新处理结果（133,468条作者记录 → 56,297个不同作者）:

- **作者总数**: 56,297个
- **平均合作者数量**: 45.41人/作者
- **合作者数量中位数**: 6人
- **最多合作者数量**: 2,645人（超级连接者）
- **最少合作者数量**: 0人（仅单作者论文）
- **平均论文数量**: 2.37篇/作者
- **论文数量中位数**: 1篇
- **最多论文数量**: 146篇（高产作者）
- **最少论文数量**: 1篇

## 数据质量说明

1. **数据来源**: 基于Semantic Scholar的authorships数据
2. **完整性**: 保留所有原始作者信息和合作关系，无数据丢失
3. **去重处理**: 每个合作者在列表中只出现一次
4. **格式规范**: JSON格式便于后续数据处理和分析
5. **编码支持**: 支持Unicode字符，正确处理非英文姓名
6. **一致性**: 结果按researcher_id排序，确保输出一致性

## 应用场景

### 学术网络分析
- **合作网络构建**: 构建作者间的合作关系图
- **影响力分析**: 基于合作者数量评估作者在学术网络中的影响力
- **社区发现**: 识别学术研究中的紧密合作社区

### 推荐系统
- **合作者推荐**: 基于共同合作者推荐潜在的合作伙伴
- **项目匹配**: 根据合作历史匹配合适的项目团队成员
- **导师推荐**: 为学生推荐合适的导师或合作导师

### 研究趋势分析
- **跨领域合作**: 识别不同研究领域间的合作模式
- **机构合作**: 分析不同机构间的合作关系
- **时间序列分析**: 结合论文发表时间分析合作关系的演变

## 与其他脚本的关系

- **`generate_coauthors_by_paper.py`**: 以论文为维度分析合作关系
- **`generate_coauthors_by_author.py`**: 以作者为维度分析合作关系
- **`advanced_name_completion.py`**: 为本脚本提供更完整的作者姓名信息

## 注意事项

1. **内存使用**: 处理大量数据时需要足够的内存空间（约2-4GB）
2. **文件大小**: 输出文件较大（约169MB），需要足够的存储空间
3. **处理时间**: 完整处理需要几分钟时间，请耐心等待
4. **JSON解析**: 使用时需要解析JSON字符串，注意处理异常情况
5. **数据完整性**: 只有在authorships.csv中同时出现的作者才会建立合作关系

## 性能优化建议

1. **分批处理**: 对于超大数据集，可以考虑分批处理
2. **并行处理**: 可以使用多进程并行处理不同的作者组
3. **内存优化**: 使用生成器或迭代器减少内存占用
4. **索引优化**: 为频繁查询的字段建立索引

## 错误处理

脚本包含完善的错误处理机制：
- 检查必需字段是否存在
- 处理空值和异常数据
- 验证JSON格式正确性
- 提供详细的进度和统计信息
