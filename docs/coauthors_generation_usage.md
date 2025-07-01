# 合作者列表生成脚本使用说明

## 脚本简介

`generate_coauthors_by_paper.py` 脚本用于从 `authorships.csv` 文件中提取每篇论文的合作者信息，并生成包含所有合作者的CSV文件。

## 功能特性

- **按论文分组**: 将 `authorships.csv` 中的作者信息按 `paper_id` 分组
- **JSON格式输出**: 每篇论文的合作者列表以JSON字符串形式存储
- **完整信息保留**: 保留每个合作者的 `researcher_id` 和 `author_name`
- **进度显示**: 处理过程中显示实时进度
- **统计信息**: 提供合作者数量的统计分析

## 输入文件

- **文件路径**: `data/authorships.csv`
- **必需字段**:
  - `researcher_id`: 研究者ID
  - `paper_id`: 论文ID
  - `author_name`: 作者姓名

## 输出文件

- **文件路径**: `data/coauthors_by_paper.csv`
- **字段说明**:
  - `paper_id`: 论文ID
  - `coauthors`: JSON格式的合作者列表字符串

### 输出格式示例

```csv
paper_id,coauthors
341,"[{""researcher_id"": 1778523, ""author_name"": ""Lluís Padró""}, {""researcher_id"": 3049328, ""author_name"": ""Lluís Màrquez i Villodre""}]"
```

### JSON结构示例

```json
[
    {
        "researcher_id": 1778523,
        "author_name": "Lluís Padró"
    },
    {
        "researcher_id": 3049328,
        "author_name": "Lluís Màrquez i Villodre"
    }
]
```

## 使用方法

### 基本用法

```bash
cd /Users/kele/实习/阿联酋/爬取/AI_Researcher_Network
python scripts/generate_coauthors_by_paper.py
```

### Python代码中使用

```python
import pandas as pd
import json

# 读取生成的合作者数据
df = pd.read_csv('data/coauthors_by_paper.csv')

# 解析某篇论文的合作者信息
paper_id = 341
row = df[df['paper_id'] == paper_id].iloc[0]
coauthors = json.loads(row['coauthors'])

print(f"论文 {paper_id} 的合作者:")
for coauthor in coauthors:
    print(f"- ID: {coauthor['researcher_id']}, 姓名: {coauthor['author_name']}")
```

## 处理结果统计

基于最新处理结果（133,468条作者记录 → 28,025篇论文）:

- **论文总数**: 28,025篇
- **平均合作者数量**: 4.76人
- **合作者数量中位数**: 4人
- **最多合作者数量**: 500人（大型协作论文）
- **最少合作者数量**: 1人（单作者论文）

## 数据质量说明

1. **数据来源**: 基于Semantic Scholar的authorships数据
2. **完整性**: 保留所有原始作者信息，无数据丢失
3. **格式规范**: JSON格式便于后续数据处理和分析
4. **编码支持**: 支持Unicode字符，正确处理非英文姓名

## 后续应用场景

1. **合作网络分析**: 构建研究者合作关系图
2. **团队研究模式**: 分析不同规模团队的研究特点
3. **跨机构合作**: 识别机构间的合作模式
4. **作者影响力**: 基于合作关系评估作者影响力

## 注意事项

- 确保输入文件存在且格式正确
- 处理大文件时需要足够的内存空间
- JSON字符串中的双引号已正确转义
- 输出文件使用UTF-8编码，支持多语言字符
