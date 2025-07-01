# 详细合作者信息生成脚本使用说明

## 脚本简介

`generate_coauthors_by_paper_detailed.py` 脚本用于从 `authorships.csv` 文件中提取每篇论文的详细作者信息，包括作者在论文中的顺序，并生成规范化的CSV文件。

## 功能特性

- **详细作者信息**: 提取每篇论文的所有作者信息，包括作者顺序
- **标准化格式**: 每位作者占据一行，便于数据分析和处理
- **作者顺序**: 保留作者在论文中的原始顺序信息
- **完整信息**: 保留作者ID、姓名和顺序信息
- **进度显示**: 处理过程中显示实时进度
- **统计分析**: 提供详细的数据统计信息

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
  - `researcher_id`: 研究者ID
  - `author_name`: 作者姓名
  - `authorship_order`: 作者在论文中的顺序（从1开始）

### 输出格式示例

```csv
paper_id,researcher_id,author_name,authorship_order
341,1778523,Lluís Padró,1
341,3049328,Lluís Màrquez i Villodre,2
537,1745366,Doug Beeferman,1
537,1710580,A. Berger,2
537,1739581,J. Lafferty,3
```

## 使用方法

### 基本用法

```bash
cd /Users/kele/实习/阿联酋/爬取/AI_Researcher_Network
python scripts/generate_coauthors_by_paper_detailed.py
```

### Python代码中使用

```python
import pandas as pd

# 读取生成的详细作者数据
df = pd.read_csv('data/coauthors_by_paper.csv')

# 查询某篇论文的所有作者
paper_id = 341
paper_authors = df[df['paper_id'] == paper_id].sort_values('authorship_order')

print(f"论文 {paper_id} 的作者列表:")
for _, author in paper_authors.iterrows():
    print(f"{author['authorship_order']}. {author['author_name']} (ID: {author['researcher_id']})")

# 查找某位作者的所有论文
researcher_id = 1778523
author_papers = df[df['researcher_id'] == researcher_id]

print(f"作者 {researcher_id} 参与的论文:")
for _, paper in author_papers.iterrows():
    print(f"论文ID: {paper['paper_id']}, 作者顺序: {paper['authorship_order']}")

# 统计第一作者的论文数量
first_author_papers = df[df['authorship_order'] == 1]
print(f"第一作者论文数量: {len(first_author_papers)}")
```

## 处理结果统计

基于最新处理结果（133,468条作者记录）:

### 基本统计
- **总作者记录数**: 133,468条
- **独特论文数**: 28,025篇
- **独特作者数**: 56,297人
- **平均每篇论文作者数**: 4.76人
- **每篇论文作者数中位数**: 4人
- **最多作者数的论文**: 500位作者
- **最少作者数的论文**: 1位作者

### 作者顺序分布
- **第1作者**: 28,025人次（每篇论文都有第一作者）
- **第2作者**: 26,811人次（95.7%的论文有第二作者）
- **第3作者**: 22,662人次（80.9%的论文有第三作者）
- **第4作者**: 16,921人次（60.4%的论文有第四作者）
- **第5作者**: 11,632人次（41.5%的论文有第五作者）

## 数据质量说明

1. **顺序准确性**: 作者顺序严格按照原始CSV中的出现顺序编号
2. **数据完整性**: 保留所有原始作者信息，无数据丢失
3. **格式规范**: 标准CSV格式，便于各种工具处理
4. **编码支持**: 支持Unicode字符，正确处理非英文姓名
5. **连续性验证**: 每篇论文的作者顺序都是连续的整数序列

## 应用场景

### 学术分析
1. **作者贡献分析**: 基于作者顺序分析贡献模式
2. **合作模式研究**: 分析不同位置作者的合作关系
3. **第一作者统计**: 识别和统计第一作者论文
4. **通讯作者分析**: 结合其他数据识别通讯作者

### 网络分析
1. **合作网络构建**: 基于共同发表论文构建作者网络
2. **影响力评估**: 结合作者顺序评估作者影响力
3. **团队分析**: 分析固定团队的合作模式
4. **跨机构合作**: 识别机构间的合作关系

### 数据挖掘
1. **作者画像**: 构建基于发表论文的作者画像
2. **趋势分析**: 分析作者合作趋势的变化
3. **影响因子**: 结合论文影响因子分析作者贡献
4. **领域分析**: 按研究领域分析作者合作模式

## 注意事项

- 确保输入文件存在且格式正确
- 处理大文件时需要足够的内存空间（约需要1GB内存）
- 作者顺序基于原始数据中的出现顺序，可能与实际署名顺序有细微差异
- 输出文件使用UTF-8编码，确保多语言字符正确显示

## 文件大小参考

- 输入文件 (`authorships.csv`): 约20MB
- 输出文件 (`coauthors_by_paper.csv`): 约15MB
- 处理时间: 约30-60秒（取决于硬件配置）
