# AI Researcher Network

## Project Overview

The AI Researcher Network project aims to develop an AI-driven platform for analyzing research papers and researcher information to provide valuable insights about AI and interdisciplinary research. The platform will help organizations and teams quickly identify appropriate researchers for collaborative AI projects, product development, and other research scenarios.

## Vision and Goals

This platform will serve as a comprehensive tool for:

1. **Researcher Discovery and Matching**: Find the most suitable researchers for specific AI projects based on their expertise, publication history, and research focus
2. **Research Trend Analysis**: Identify emerging trends and patterns in AI and interdisciplinary research
3. **Collaboration Network Mapping**: Visualize and analyze collaboration networks among researchers
4. **Thematic Classification**: Automatically categorize research papers into relevant themes and topics
5. **Contextual Recommendations**: Suggest potential collaborators, related research, and interdisciplinary connections

## Current Development Status

The project is currently in the data analysis, classification, and retrieval stage, focused on NLP related research. Key components that have been developed include:

### Data Collection and Processing
- Gathering research paper data from the ACL Anthology and other academic repositories
- Extracting and structuring paper metadata (titles, abstracts, authors, affiliations)
- Creating structured datasets for researcher and paper information

### Classification Systems
- Implementation of a SciBERT-based theme classifier for categorizing research papers
- Fine-tuning of models to handle the complexity of academic research topics
- Creation of a weighted loss function to address class imbalance in research paper themes

### Analysis Tools
- Track distribution analysis for understanding research topic popularity
- Author network analysis for identifying key researchers and their relationships
- Visualization tools for presenting research trends and connections

### Latest Changes
- Integrated DashScope API for improved classification and prediction
- Added functionality to save confusion matrix as PNG and classification report as TXT
- Enhanced scripts for automated extraction of researcher information and paper metadata
- Improved database schema for future AWS deployment

## Future Development Roadmap

### Near Term (1-3 months)
- Complete the data analysis and classification system
- Deploy the initial database to AWS
- Develop and test data retrieval APIs
- Begin work on basic front-end components

### Medium Term (3-6 months)
- Implement the full database infrastructure
- Develop the platform UI design and user interaction flows
- Create advanced search and recommendation features
- Begin testing with real-world use cases

### Long Term (6+ months)
- Launch the complete platform with all core features
- Integrate with other academic databases and repositories
- Incorporate continuous learning mechanisms to improve recommendations
- Develop specialized tools for different research domains

## Technical Stack

- **Data Processing**: Python, pandas, NumPy
- **Machine Learning**: PyTorch, scikit-learn, Transformers, HuggingFace
- **Data Storage**: AWS RDS (planned)
- **Visualization**: Matplotlib, Seaborn
- **Future Front-end**: To be determined (likely React or Vue.js)

## Getting Started

### Prerequisites
```
numpy
pandas
torch
scikit-learn
transformers
datasets
tensorboard
```

### Installation
1. Clone this repository
2. Install required packages: `pip install -r requirements.txt`
3. Run data collection scripts to populate local datasets

## Contributors
- Eric Chen
- Wenxuan Zhu

## License
[License information to be added]
