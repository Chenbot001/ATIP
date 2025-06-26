# Project Status and Next Steps

## Completed Tasks (DONE)

* **Infrastructure Setup:**
    * Established connection with database server environment.
* **Data Tables:**
    * Created `paper_data` table with ACL, NAACL, EMNLP past paper data from anthology
        - data schema: `paper_id`, `title`, `abstract`, `venue`, `year`, `tracks`
    * Created `paper - award(s)` relationship table with past paper data
    * Created `researcher_profile` table based on past paper authors
        - data schema: `author_id`(custom), `first_name`, `last_name`, `openreview_id`(incomplete), `google_scholar_id`(incomplete), `current_affiliation`, `email`(incomplete)
* **Categorization Model:**
    * Tested TF-IDF, SciBERT finetuning, prompt engineering classifiacation methods on ACL 2025 official track data.
    * Ran newest classification model on `paper_data` ~40% accuracy

---

## TODO

### **Week 1: Database Setup and Data Aggregation (June 23 - June 29)**

* **Monday - Tuesday:**
    * **Task:** Parse and populate the `researcher_profile` table with data from Google Scholar and OpenReview.net.
    * **Goal:** Create a comprehensive list of researcher profiles, filling in the crucial missing information.

* **Wednesday - Saturday:**
    * **Task:** Create and begin populating the relational tables.
        * **`Authorship` Table:** Link `author_id` to `paper_id`, indicating first authors and corresponding authors.
        * **`Citations` Table:** Create paper-to-paper citation links (`paper_id` to `paper_id`).
    * **Goal:** Establish the core relationships between papers and researchers to support MVP features.

* **Sunday:**
    * **Task:** Set up the cloud database environment.
    * **Task:** Import all available data from the CSV files (`paper_data`, `paper - award(s)`, `researcher_profile`) into the cloud database.
    * **Goal:** Have the initial database structure and existing data in place for immediate use.

### **Week 2: Classification Model Refinement (June 30 - July 6)**

* **Monday - Wednesday:**
    * **Task:** Enhance the ACL 2025 training set by retrieving paper abstracts from arXiv.
    * **Goal:** Collect the necessary semantic information to improve the model.

* **Thursday - Saturday:**
    * **Task:** Finetune the SciBERT classification model with the newly enhanced dataset.
    * **Goal:** Obtain a highly efficient classification model with a target accuracy of ~90%.

* **Sunday:**
    * **Task:** Run the newly finetuned classifier on the `paper_data` and update the `tracks` column in the database.
    * **Goal:** Update the existing paper entries with high-accuracy classification data.

---

## Product

* **Vision:** Not just see who is impactful in the field, but also find the right person to work with

* **Milestone:** Have a MVP ready by mid-July.

* **Features:**
    * **Researcher & Paper Analytics**: Provide a full profile for any author. This includes their citation metrics and trends, a timeline of their publications, their most impactful papers, and an analysis of how their research topics have evolved over time.
    * **Topic & Trend Discovery**: For any given research track, automatically identify seminal or foundational papers based on citation velocity and centrality within that specific topic. Analyze publication and citation data to reveal emerging research trends and hot topics, as well as topics that are becoming less active.
    * **Collaboration & Network Analysis**: Identify institutional or personal cooperation patterns. Create a graph visualization of the academic network to show how institutions and individual researchers collaborate. Offer a "collaboration suggestion" feature to identify potential co-authors who work on similar problems but are not in the user's immediate network.
    * **Interactive Visualization Dashboard**: An automated and query-driven dashboard will serve as the primary interface for all features. Users can query a researcher, a topic, or an institution, and the dashboard will dynamically generate all relevant analytics, network graphs, and trend analyses.