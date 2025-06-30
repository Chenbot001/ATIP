# Researcher-Paper Mapping Extractor

## 概述

这个脚本从 ACL Anthology 中提取研究者与论文的详细对应关系，为每个作者-论文对创建一条记录。与原始脚本不同，这个脚本保留了所有的作者-论文关系，不进行去重，同一作者在多篇论文中出现会有多条记录。

## 主要功能

1. **提取作者-论文关系**：每个作者在每篇论文中都会生成一条记录
2. **生成一致的研究者ID**：使用 UUID v5 基于姓名生成，确保同名作者的ID一致
3. **支持批量处理**：可以处理多个 collections
4. **保留所有关系**：不去重，完整保留作者-论文映射关系

## 输出字段

- `researcher_id`: 基于姓名生成的唯一ID (UUID v5)
- `first_name`: 作者名字
- `last_name`: 作者姓氏  
- `paper_doi`: 论文的DOI或ID
- `affiliation`: 作者所属机构（如果有）

## 使用方法

### 1. 处理单个 collection

```bash
python scripts/researcher_paper_mapping.py --collection 2024.acl
```

### 2. 处理所有 collections

```bash
python scripts/researcher_paper_mapping.py --all-collections
```

### 3. 指定输出文件

```bash
python scripts/researcher_paper_mapping.py --all-collections --output data/my_output.csv
```

### 4. 指定 collections 文件

```bash
python scripts/researcher_paper_mapping.py --all-collections --collections-file data/my_collections.txt
```

## 命令行参数

- `--collection`: 指定单个 collection ID (默认: 2024.acl)
- `--output`: 输出CSV文件路径 (默认: data/researchers_data_with_paper.csv)
- `--collections-file`: 包含多个 collection ID 的文件 (默认: data/acl_collections.txt)
- `--all-collections`: 处理 collections 文件中的所有 collections

## 测试

运行测试脚本来验证功能：

```bash
python scripts/test_researcher_mapping.py
```

## 依赖

- `acl_anthology`
- `pandas`
- `uuid` (Python 标准库)

## 注意事项

1. **数据量**：处理所有 collections 会产生大量数据，建议先用单个 collection 测试
2. **性能**：使用多线程处理以提高效率
3. **编码**：输出文件使用 UTF-8 编码
4. **错误处理**：包含完整的错误处理和日志记录
5. **中间保存**：每处理5个 collections 会保存一次中间结果

## 与 Semantic Scholar 匹配

输出的CSV文件可以直接用于与 Semantic Scholar 的 authorships 数据进行匹配：

- 使用 `first_name` 和 `last_name` 进行姓名匹配
- 使用 `paper_doi` 与 Semantic Scholar 的论文ID进行匹配
- `researcher_id` 可以作为内部唯一标识符使用
