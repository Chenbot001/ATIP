# TODO 0603

## Infrastructure Setup
- Establish and configure the database server environment. **DONE**

## Categorization

### Data Acquisition for Model Training:
- Utilize ACL 2025 paper track information to train a classification model. **DONE**
- Run classifier on prior papers. 
- Retrieve paper abstracts from arXiv as needed to enhance model performance and data richness. 

### Model Validation:
- Parse and test the trained categorization model using the test set from ACL 2025 paper data (~30%). **DONE**

## Paper Information Table
- Data from ACL Anthology 
- **Data Schema:** 
    - `papers table`: paper_id, title, abstract, venue, year, award, tracks **DONE**

## Researcher Information Table
- **Researcher Identification:** OpenReview.net IDs as a primary identifier 
- Hybrid parsing method, data from both Google Scholar and OpenReview.net 
- **Data Schema:** 
    - `researchers table`: researcher_id, first_name, last_name, current_affiliation, affiliation_history 

## Other Relational Tables:
- **Authorship:** Researcher_id - paper_id 
- **Citations:** Paper_id – paper_id 

---

## By 0607
- Sample data of researcher and paper tables ready as csv 
- Track categorization model tested