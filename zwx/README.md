# ACL 论文作者与机构爬取工具

这个工具使用 ACL-anthology Python 库爬取 ACL 会议论文的作者和所属机构信息，并进行去重处理。

## 功能特点

- 爬取指定会议（默认为 ACL 2024）的所有论文信息
- 提取每篇论文的作者和所属机构
- 对作者和机构进行去重处理
- 生成三个CSV文件：
  - `acl2024_authors.csv`: 包含所有独特作者及其所属机构
  - `acl2024_affiliations.csv`: 包含所有独特机构列表
  - `acl2024_papers.csv`: 包含所有论文的详细信息（ID、标题、作者、机构）
- 提供统计信息（论文数量、作者数量、机构数量等）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

直接运行脚本即可：

```bash
python acl_authors_affiliations.py
```

默认会爬取 ACL 2024 会议的论文信息。如果需要修改为其他会议，请编辑脚本中的 `main()` 函数，更改 `get_authors_and_affiliations()` 函数的参数。

## 输出文件

所有输出文件将保存在 `./output` 目录下：

- `acl2024_authors.csv`: 作者及其所属机构
- `acl2024_affiliations.csv`: 所有独特机构列表
- `acl2024_papers.csv`: 论文详细信息

## 注意事项

- 首次运行时，ACL-anthology 库可能需要下载数据，这可能需要一些时间
- 爬取大型会议的所有论文可能需要较长时间，请耐心等待
- 如果遇到网络问题，脚本会继续处理已获取的数据