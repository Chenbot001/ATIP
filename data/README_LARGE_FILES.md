# 大数据文件说明

由于GitHub对单个文件100MB的限制，以下大数据文件不包含在版本控制中：

## 生成的大数据文件

### `data/coauthors_by_author.csv` (约131MB)
- **描述**: 每位作者与其合作者的详细合作关系数据
- **记录数**: 2,556,348条
- **生成方法**: 运行 `python scripts/generate_coauthors_by_author.py`
- **用途**: 学术合作网络分析、合作者推荐等

### 如何生成这些文件

1. 确保您有足够的内存空间（推荐8GB以上RAM）
2. 运行相应的脚本：
   ```bash
   # 生成作者合作关系数据
   python scripts/generate_coauthors_by_author.py
   
   # 生成详细论文作者信息
   python scripts/generate_coauthors_by_paper_detailed.py
   ```

3. 生成的文件将保存在 `data/` 目录下

### 文件规格

| 文件名 | 大小 | 记录数 | 生成时间 | 用途 |
|--------|------|---------|----------|------|
| `coauthors_by_author.csv` | ~131MB | 2,556,348 | 5-10分钟 | 作者合作关系分析 |
| `coauthors_by_paper.csv` | ~15MB | 133,468 | 1-2分钟 | 论文作者信息 |

### 注意事项

- 这些文件基于 `authorships.csv` 生成，确保该文件存在
- 处理大数据时建议在性能较好的计算机上运行
- 生成的文件可用于各种学术网络分析和数据挖掘任务

### 联系方式

如果您需要获取预生成的大数据文件，请联系项目维护者。
