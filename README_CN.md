# AI 研究人员网络

## 项目概览

AI 研究人员网络项目旨在开发一个人工智能驱动的平台，用于分析研究论文和研究人员信息，从而提供有关 AI 和跨学科研究的有价值见解。该平台将帮助组织和团队快速为协作 AI 项目、产品开发和其他研究场景找到合适的研究人员。

## 目标

该平台将成为以下方面的综合工具：

1. **研究人员发现与匹配**：根据专业知识、出版历史和研究重点，为特定 AI 项目寻找最合适的研究人员
2. **研究趋势分析**：识别 AI 和跨学科研究中的新兴趋势和模式
3. **协作网络映射**：可视化并分析研究人员之间的协作网络
4. **主题分类**：自动将研究论文分类为相关主题和话题
5. **上下文推荐**：推荐潜在合作者、相关研究和跨学科联系

## 当前开发状态

该项目目前处于数据分析、分类和检索阶段，专注于 NLP 相关研究。已开发的关键组件包括：

### 数据收集和处理
- 从 ACL Anthology 和其他学术存储库收集研究论文数据
- 提取和构建论文元数据（标题、摘要、作者、机构）
- 为研究人员和论文信息创建结构化数据集

### 分类系统
- 实现基于 SciBERT 的主题分类器，用于对研究论文进行分类
- 微调模型以处理学术研究主题的复杂性
- 创建加权损失函数，解决研究论文主题中的类别不平衡问题

### 分析工具
- 论文方向分布分析，了解研究主题流行度
- 作者网络分析，识别关键研究人员及其关系
- 用于展示研究趋势和联系的可视化工具

### 最新变更
- 添加了改进的 SciBERT 微调，用于 NLP 研究论文方向分类
- 开发了加权损失函数，处理研究主题分类中的不平衡数据
- 实现了全面的分类性能评估指标
- 创建了用于展示方向分布和研究趋势的可视化工具
- 添加了用于自动提取研究人员信息和论文元数据的脚本
- 增强了用于未来 AWS 部署的数据库架构

## 未来开发路线图

### 近期（1-3个月）
- 完成数据分析和分类系统
- 将初始数据库部署到 AWS
- 开发和测试数据检索 API
- 开始基本前端组件的工作

### 中期（3-6个月）
- 实现完整的数据库基础架构
- 开发平台 UI 设计和用户交互流程
- 创建高级搜索和推荐功能
- 开始使用实际案例进行测试

### 长期（6个月以上）
- 推出具有所有核心功能的完整平台
- 与其他学术数据库和资源库集成
- 纳入持续学习机制以改进推荐
- 为不同研究领域开发专门工具

## 技术栈

- **数据处理**：Python、pandas、NumPy
- **机器学习**：PyTorch、scikit-learn、Transformers、HuggingFace
- **数据存储**：AWS RDS（计划中）
- **可视化**：Matplotlib、Seaborn
- **未来前端**：待定（可能是 React 或 Vue.js）

## 开始使用

### 前提条件
```
numpy
pandas
torch
scikit-learn
transformers
datasets
tensorboard
```

### 安装
1. 克隆此仓库
2. 安装所需包：`pip install -r requirements.txt`
3. 运行数据收集脚本以填充本地数据集

## 项目结构
```
AI_Researcher_Network/
├── data/
│   ├── acl_collections.txt
│   ├── ACL25 Accepted Paper with Track Info.csv
│   ├── ACL25_ThemeData.csv
│   ├── Conference Submission Topics.xlsx
│   ├── NLP_topics.csv
│   └── papers_data.csv
├── scripts/
│   ├── anthology_test.py
│   ├── dedupe_topics.py
│   ├── paper_table.py
│   ├── researcher_table.py
│   ├── scholarly_test.py
│   ├── serpapi_test.py
│   ├── Theme_Classifier.py
│   └── track_distribution.py
├── visualizations/
│   ├── confusion_matrix.png
│   ├── eric_xing_network.png
│   └── track_distribution.png
├── prompt.md
├── requirements.txt
├── test.py
└── README.md
```

## 贡献者
- 陈湘林
- 朱文轩

## 许可证
[许可证信息待添加]
