# Data Files Setup

Place your CSV files in this directory for the ATIP application to load them.

## Required Files

The following CSV files should be placed in this directory:

- `author_profiles.csv` - Author profile information
- `paper_info.csv` - Paper information
- `authorships.csv` - Author-paper relationships
- `top100_pqi.csv` - Top 100 authors by PQI score
- `top100_anci.csv` - Top 100 authors by ANCI score
- `top100_accel.csv` - Top 100 authors by ACCEL score

## File Structure

Your CSV files should be placed directly in this directory:

```
public/data/
├── author_profiles.csv
├── paper_info.csv
├── authorships.csv
├── top100_pqi.csv
├── top100_anci.csv
└── top100_accel.csv
```

## Expected Column Names

### author_profiles.csv
- `id` or `author_id` - Unique author identifier
- `name` or `author_name` - Author's full name
- `affiliation` - Author's institution/organization
- `pqi_score` - Paper Quality Index score
- `anci_score` - Academic Network Citation Index score
- `accel_score` - Academic Excellence score
- `h_index` - H-index value
- `citations` or `citation_count` - Total citation count

### paper_info.csv
- `id` or `paper_id` - Unique paper identifier
- `title` or `paper_title` - Paper title
- `venue` or `journal` - Publication venue
- `year` - Publication year
- `citations` or `citation_count` - Citation count
- `url` - Paper URL (optional)

### authorships.csv
- `id` or `authorship_id` - Unique authorship identifier
- `author_id` - Author identifier
- `paper_id` - Paper identifier

### top100_*.csv files
- `id` or `author_id` - Unique author identifier
- `name` or `author_name` - Author's full name
- `affiliation` - Author's institution/organization
- `pqi_score` - PQI score (for top100_pqi.csv)
- `anci_score` - ANCI score (for top100_anci.csv)
- `accel_score` - ACCEL score (for top100_accel.csv)

## Notes

- The application will automatically detect and use the appropriate column names
- Missing data will be displayed as "N/A"
- The application caches CSV data after first load for better performance 