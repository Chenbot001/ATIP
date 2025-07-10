# ATIP - Academic Talent Identification and Profiling

A modern, data-centric Vue 3 application for ranking and profiling academic researchers based on programmatically calculated metrics.

## 🚀 Features

- **Modern UI**: Clean, minimalist design with light theme
- **Researcher Rankings**: View top researchers by PQI, ANCI, and ACCEL metrics
- **Author Profiles**: Detailed profiles with metrics, co-author networks, and publications
- **Interactive Graphs**: Co-author network visualization using Cytoscape.js
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Data-Driven**: Loads and parses CSV data at runtime

## 🛠️ Tech Stack

- **Framework**: Vue 3 (Composition API with `<script setup>`)
- **Build Tool**: Vite
- **Routing**: Vue Router
- **Graph Visualization**: Cytoscape.js
- **CSV Parsing**: Papa Parse
- **Styling**: Plain CSS with CSS Variables

## 📦 Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd website
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up your data files:**
   - Copy your CSV files to the `public/data/` directory
   - See `public/data/README.md` for required file structure

4. **Start the development server:**
   ```bash
   npm run dev
   ```

5. **Open your browser:**
   Navigate to `http://localhost:3000`

## 📁 Project Structure

```
website/
├── public/
│   └── data/                    # CSV data files
│       ├── author_profiles.csv  # 56K+ author profiles with metrics
│       ├── paper_info.csv       # 28K+ papers with metadata
│       ├── authorships.csv      # 133K+ author-paper relationships
│       ├── top100_pqi.csv       # Top 100 PQI rankings
│       ├── top100_anci.csv      # Top 100 ANCI rankings
│       ├── top100_accel.csv     # Top 100 ACCEL rankings
│       ├── README.md            # Data file documentation
│       └── data_structure_analysis.txt
├── src/
│   ├── assets/
│   │   └── main.css             # Global styles and CSS variables
│   ├── components/              # Reusable Vue components
│   │   ├── AuthorMetricCard.vue
│   │   ├── CoauthorGraph.vue
│   │   ├── LeaderboardPreview.vue
│   │   ├── PublicationsTable.vue
│   │   └── TheHeader.vue
│   ├── router/
│   │   └── index.js             # Vue Router configuration
│   ├── services/
│   │   └── dataLoader.js        # CSV data loading and caching
│   ├── views/                   # Page components
│   │   ├── AuthorProfileView.vue
│   │   ├── HomeView.vue
│   │   └── RankingView.vue
│   ├── App.vue                  # Root component
│   └── main.js                  # Application entry point
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## 🎨 Design System

The application uses a consistent light theme with the following color palette:

- **Background**: `#F9F9F9` (Soft off-white)
- **Surface**: `#FFFFFF` (Pure white for cards)
- **Primary**: `#3B82F6` (Modern blue)
- **Text Primary**: `#1F2937` (Dark gray)
- **Text Secondary**: `#6B7280` (Lighter gray)
- **Border**: `#E5E7EB` (Subtle border color)

## 📊 Data Requirements

The application expects the following CSV files in `public/data/`:

- `author_profiles.csv` (2.9MB) - 56K+ author profiles with metrics (PQI, ANCI, ACCEL, H-index, citations)
- `paper_info.csv` (29MB) - 28K+ papers with metadata (title, venue, year, citations, DOI, etc.)
- `authorships.csv` (16MB) - 133K+ author-paper relationships with authorship details
- `top100_pqi.csv` (3.6KB) - Top 100 PQI rankings with additional metrics
- `top100_anci.csv` (3.8KB) - Top 100 ANCI rankings with additional metrics  
- `top100_accel.csv` (3.6KB) - Top 100 ACCEL rankings with additional metrics

### Data Scale
- **Total Authors**: 56,290 researchers
- **Total Papers**: 28,082 publications
- **Total Authorships**: 133,456 author-paper relationships
- **Coverage**: ACL anthology papers with comprehensive citation and collaboration data

See `public/data/README.md` for detailed file structure and column specifications.

## 🚀 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## 📱 Responsive Design

The application is fully responsive and optimized for:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (< 768px)

## 🔧 Customization

### Adding New Metrics
1. Add your metric data to the CSV files
2. Update the data loader service to include the new metric
3. Add the metric to the AuthorMetricCard components
4. Update the ranking views if needed

### Styling Changes
- Global styles are in `src/assets/main.css`
- Component-specific styles use `<style scoped>`
- CSS variables are defined in the `:root` selector

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the ATIP academic research platform.

## 🆘 Support

For issues or questions:
1. Check the data file setup in `public/data/README.md`
2. Ensure all required CSV files are present
3. Check browser console for error messages
4. Verify CSV column names match expected format 