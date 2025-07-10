# ATIP (Academic Talent Identification and Profiling) - Project Plan

This document outlines the features, design, and technical stack for the ATIP website MVP. The project's core concept is to rank academic researchers from a unique, entertaining perspective: "this is what AI thinks of you." All metrics are generated programmatically to offer an impartial, data-driven view.

## 🤖 Core Metrics

The ranking system is built upon several high-level metrics calculated from publication and citation data. The primary metrics are:

1.  **Adjusted Normalized Citation Impact (ANCI):** Measures citation impact, normalized by career length and adjusted for co-authorship.
2.  **Citation Acceleration:** Measures the rate of change in an author's citation trends using Compound Annual Growth Rate (CAGR) and a Linear Trend Second Derivative.
3.  **Publication Quality Index (PQI):** A comprehensive score based on a weighted average of a publication's venue quality, citation count, awards, and recency.

## ✨ Core Features & Page Design

### 1. Home Page (`/`)
* **Purpose:** To introduce the site and provide a high-level overview of the rankings.
* **Layout:**
    * A main title and a prominent, centered **author search bar** with autocomplete.
    * A three-column preview section displaying the top 3-5 researchers for each primary leaderboard: **PQI**, **ANCI**, and **Citation Acceleration**.

### 2. Leaderboard Pages (`/ranking/:metric`)
* **Purpose:** To display the full, filterable ranking for a specific metric.
* **Layout:** A full-page, sortable table with columns for Rank, Author Name, Affiliation, and relevant metric scores. Will include options to filter by affiliation or career length.

### 3. Author Profile Page (`/author/:id`)
* **Purpose:** To provide a comprehensive, data-rich profile for a single researcher.
* **Layout:**
    * **Header:** Author's name, photo, and affiliation.
    * **Metrics Dashboard:** A "card"-based UI displaying the author's scores for all key metrics (PQI, ANCI, etc.).
    * **Co-author Network Graph:** A large, interactive graph visualization. It will support zooming, panning, and clicking on nodes (co-authors) to show pop-up info.
    * **Publication List:** A paginated table of the author's papers, showing the title, year, venue, and individual paper PQI score.

## 🚀 Future Feature Considerations

These features can be added after the core MVP is complete to enhance user engagement.

* **"AI's Hot Take":** A generated one-sentence qualitative summary on each author's profile.
* **Metric Explainers:** Tooltips on each metric score that briefly explain how it's calculated.
* **"Rising Stars" Leaderboard:** A dedicated ranking for researchers with short careers but high citation acceleration.
* **Author Comparison:** A side-by-side view to compare the stats of two different authors.

## 💻 Technical Stack

* **Frontend:** **Vue.js** (using Vite for the build tool and Vue Router for page navigation).
* **Backend:** **FastAPI** (Python).
* **Database:** **SQL database** on an Ubuntu server (to be integrated post-MVP).
* **Initial Data Source:** For MVP development, the application will fetch data directly from raw **CSV files** hosted in the project's GitHub repository.
* **Development Environment:** Cursor.