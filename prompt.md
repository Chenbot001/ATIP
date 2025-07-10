Generate a complete Vue 3 project named "ATIP" using Vite. The project is an academic talent identification and profiling website designed to rank researchers with a modern, simplistic, and data-centric UI.

---

### ## 1. Project Overview

* **Project Name:** ATIP (Academic Talent Identification and Profiling)
* **Core Concept:** A sleek, modern website that displays rankings of academic researchers based on programmatically calculated metrics. The vibe is "what an AI thinks of you," so the design should be clean, digital, and intuitive.
* **Theme:** **Light mode by default.**

---

### ## 2. Core Technologies

* **Framework:** Vue 3 (using the Composition API with `<script setup>`).
* **Build Tool:** Vite.
* **Routing:** Vue Router.
* **Graph Visualization:** Cytoscape.js.
* **CSV Parsing:** Papa Parse.
* **Styling:** Plain CSS within Vue's `<style scoped>` tags. No CSS frameworks like Tailwind or Bootstrap are needed.

---

### ## 3. Data Handling (IMPORTANT)

For this initial build, the application will load and parse local CSV files at runtime. **We will not connect to a backend API.**

1.  **Project Setup:**
    * Create a directory named `public/data` in the project root. The user will be instructed to place all their local CSV files (e.g., `authorships.csv`, `paper_info.csv`, `author_profiles.csv`, etc.) into this directory.
    * Add the `papaparse` library to the project: `npm install papaparse`.

2.  **Data Loading Service:**
    * Create a new file at `src/services/dataLoader.js`. This service will be responsible for fetching, parsing, and providing access to the data from the CSV files.
    * The service should export functions to get specific data, for example, `getAuthors()`, `getPapers()`, etc.
    * These functions will use the `fetch` API to get a CSV file from the `/data/` URL (e.g., `fetch('/data/author_profiles.csv')`) and then use `Papa.parse` to convert the CSV text into an array of JavaScript objects.
    * **Crucially, the service should cache the parsed data in a local variable** so that the CSV files are only fetched and parsed once when the application first loads, not every time a component requests data.

3.  **Component Data Usage:**
    * All Vue components that need data (e.g., `RankingView`, `AuthorProfileView`) should import and use the functions from `src/services/dataLoader.js` to retrieve the necessary information.

---

### ## 4. Project Structure & Components

Please generate the following file structure and boilerplate code for each component.

* **`src/router/index.js`**: Configure the following routes:
    * `path: '/'`, component: `HomeView`
    * `path: '/ranking/:metric'`, component: `RankingView`, props: true
    * `path: '/author/:id'`, component: `AuthorProfileView`, props: true

* **`src/views/HomeView.vue`**: The landing page.
    * **Layout:** A central title like "ATIP" with a subtitle. A prominent, wide search bar component below it. Below that, a 3-column layout using CSS Grid, each column containing a `LeaderboardPreview` component.
    * **Functionality:** Use the data loader service to get the data from `top100_pqi.csv`, `top100_anci.csv`, and `top100_accel.csv` to populate the three `LeaderboardPreview` components.

* **`src/views/RankingView.vue`**: The full leaderboard page.
    * **Layout:** A full-page table displaying ranked authors.
    * **Functionality:** Accepts a `:metric` route parameter ('pqi', 'anci', 'accel'). It should use the data loader service to fetch data from the corresponding `top100_...csv` file and display the results. Columns should be: `Rank`, `Name`, and the relevant score.

* **`src/views/AuthorProfileView.vue`**: The detailed author page.
    * **Layout:**
        1.  **Header Section:** Large author name, affiliation, and a circular profile picture.
        2.  **Metrics Dashboard:** A grid of `AuthorMetricCard` components.
        3.  **Co-author Graph:** A large section containing the `CoauthorGraph` component.
        4.  **Publications:** A `PublicationsTable` component at the bottom.
    * **Functionality:** Accepts an `:id` route parameter. Use the data loader service to find the author's data in `author_profiles.csv` and their papers in `authorships.csv` to populate the page.

* **`src/components/`**: Create these reusable components:
    * **`TheHeader.vue`**: A simple top navigation bar with the site title "ATIP".
    * **`LeaderboardPreview.vue`**: A card component that shows the top 3-5 authors for a given metric.
    * **`AuthorMetricCard.vue`**: A small card that displays a metric's name (e.g., "PQI") and its value.
    * **`CoauthorGraph.vue`**: Accepts an `authorId` prop. Use the data loader to find co-authors from `authorships.csv` and render a network graph with Cytoscape.js.
    * **`PublicationsTable.vue`**: Accepts a list of paper objects as a prop and renders a table.

---

### ## 5. Design & Styling Requirements

* **Main CSS File (`src/assets/main.css`):**
    * Import a font from Google Fonts, e.g., `Inter` or `Poppins`.
    * Define CSS variables for the **light theme color palette**:
        ```css
        :root {
          --background: #F9F9F9;      /* Soft off-white background */
          --surface: #FFFFFF;         /* Pure white for cards and surfaces */
          --primary: #3B82F6;         /* A modern blue for links, buttons */
          --text-primary: #1F2937;    /* Dark gray for primary text */
          --text-secondary: #6B7280; /* Lighter gray for secondary text */
          --border-color: #E5E7EB;   /* Subtle border color */
        }
        ```
    * Set the `background-color` of the `body` to `var(--background)` and `color` to `var(--text-primary)`.
* **Component Styles:** All component-specific styles should be in `<style scoped>` tags. Use Flexbox and Grid for layouts. Ensure consistent padding and spacing.
* **Cards:** All card-like components (`LeaderboardPreview`, `AuthorMetricCard`) should have a background color of `var(--surface)`, rounded corners (`border-radius: 8px;`), and a subtle border (`border: 1px solid var(--border-color);`) to distinguish them from the background.
* **Responsiveness:** Use media queries to ensure the layout is usable on mobile devices.