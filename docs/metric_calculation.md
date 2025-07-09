# ATIP Metric Calculation Documentation

This document details how each high-level metric in the ATIP (Academic Talent Identification and Profiling) system is derived from the available data sources.

## Data Sources

The metrics are calculated using the following primary data sources:

- **`paper_info.csv`**: Contains paper metadata including `corpus_id`, `venue`, `year`, `citation_count`, `acl_id`
- **`authorships.csv`**: Links authors to papers via `author_id` and `paper_id`
- **`author_profiles.csv`**: Contains author information including `author_id`, `first_name`, `last_name`
- **`author_citation_metrics.csv`**: Contains yearly citation data for authors
- **`paper_awards.csv`**: Contains award information for papers
- **`venue_tiers.csv`**: Maps venues to quality tiers (A, B, C, D)

## High-Level Metrics

### Career Length (Y)

**Purpose**: Measures the duration of an author's research career.

**Calculation**:
```
Career Length = 2025 - First Publication Year + 1
```

**Data Requirements**:
- `authorships.csv`: To find all papers by the author
- `paper_info.csv`: To get publication years

**Process**:
1. Find all `paper_id`s associated with the author from `authorships.csv`
2. Look up publication years for these papers in `paper_info.csv`
3. Calculate: `2025 - min(publication_years) + 1`
4. Return 0 if no papers found

**Example**: If an author's first paper was published in 2010, their career length would be 16 years (2025 - 2010 + 1).

---

### 2. Adjusted Normalized Citation Impact (ANCI)

**Purpose**: Measures citation impact normalized by career length and adjusted for co-authorship.

**Calculation**:
```
ANCI = Σ(Fractional Citations) / (Number of Papers × √Career Length)
```

Where:
- **Fractional Citations** = `citation_count / number_of_authors` for each paper
- **Career Length** = Years since first publication

**Data Requirements**:
- `authorships.csv`: To find author's papers and count co-authors
- `paper_info.csv`: To get citation counts and publication years
- Career length (calculated separately)

**Process**:
1. Find all papers by the author
2. For each paper:
   - Count total authors using `authorships.csv`
   - Calculate fractional citations: `citation_count / author_count`
3. Sum all fractional citations
4. Divide by: `(number_of_papers × √career_length)`

**Co-authorship Adjustment**: This metric accounts for the fact that citations are shared among co-authors, providing a fair comparison between single-author and multi-author papers.

---

### 3. Citation Acceleration Metrics

**Purpose**: Measures the rate of change in citation patterns over time.

**Two Components**:

#### 3.1 Compound Annual Growth Rate (CAGR)

**Calculation**:
```
CAGR = (c_t / c_{t-n})^(1/n) - 1
```

Where:
- `c_t` = citations in current year (2024) + 1
- `c_{t-n}` = citations n years ago + 1
- `n` = min(3, career_length - 1)

**Data Requirements**:
- `author_citation_metrics.csv`: Contains yearly citation data
- Career length

**Process**:
1. Parse yearly citation data from `citations_by_year` column
2. Calculate citations for current year (2024) and n years ago
3. Apply CAGR formula with smoothing factor (k=1)

#### 3.2 Linear Trend Second Derivative

**Calculation**:
```
Linear Trend = (β_current - β_previous) / w
```

Where:
- `β_current` = slope of citations in current window (2023-2024)
- `β_previous` = slope of citations in previous window (2021-2022)
- `w` = window size (2 years)

**Data Requirements**:
- `author_citation_metrics.csv`: Contains yearly citation data
- Career length ≥ 6 years (minimum requirement)

**Process**:
1. Calculate linear regression slopes for two 2-year windows
2. Take the difference and divide by window size
3. Returns 0.0 if career length < 6 years

---

### 4. Publication Quality Index (PQI)

**Purpose**: Comprehensive measure of publication quality considering venue, citations, awards, and recency.

**Calculation**:
```
PQI = 0.40 × Venue Score + 0.30 × Citation Score + 0.20 × Award Score + 0.10 × Recency Score
```

#### 4.1 Venue Score

**Calculation**:
```
Venue Score = Base Tier Score × Track Weight
```

**Base Tier Scores**:
- Tier A: 4.0
- Tier B: 3.0
- Tier C: 2.0
- Tier D: 1.0

**Track Weights**:
- Main/Long: 1.0
- Short: 0.8
- Findings: 0.7
- Industry: 0.6
- SRW: 0.5
- Demo: 0.4
- Tutorials: 0.2

**Data Requirements**:
- `paper_info.csv`: Contains `venue` and `acl_id`
- `venue_tiers.csv`: Maps venues to tiers

**Process**:
1. Look up venue tier from `venue_tiers.csv`
2. Determine track from `acl_id` using keyword matching or digit codes
3. Multiply base tier score by track weight

#### 4.2 Citation Score

**Calculation**:
```
Citation Score = log(citation_count + 1)
```

**Data Requirements**:
- `paper_info.csv`: Contains `citation_count`

**Process**:
- Apply natural logarithm to citation count with smoothing (+1)

#### 4.3 Award Score

**Calculation**:
```
Award Score = max(award_points) / MAX_AWARD_POINTS
```

**Award Point Values**:
- Best Overall Paper/Test-of-Time: 5.0
- Best Paper Runner-Up/Outstanding Paper: 4.0
- Area Chair/SAC Award/Best Short Paper: 3.0
- Honorable Mention/Reproduction Award: 2.0
- Best Demo Paper/Specific Contribution: 1.0

**Data Requirements**:
- `paper_awards.csv`: Contains award information

**Process**:
1. Find all awards for the paper
2. Look up point values for each award
3. Take the maximum point value
4. Normalize by dividing by 5.0 (MAX_AWARD_POINTS)

#### 4.4 Recency Score

**Calculation**:
```
Recency Score = 1 / (1 + age)
```

Where `age = 2025 - publication_year`

**Data Requirements**:
- `paper_info.csv`: Contains `year`

**Process**:
- Calculate paper age and apply inverse relationship
- Recent papers get higher scores

#### 4.5 Author PQI

**Calculation**:
```
Author PQI = mean(PQI_scores for all author's papers)
```

**Data Requirements**:
- All PQI component data sources
- `authorships.csv`: To find all papers by the author

**Process**:
1. Calculate PQI for each paper by the author
2. Return the arithmetic mean of all paper PQI scores

---

## Metric Relationships and Dependencies

### Primary Dependencies
- **Career Length**: Required for ANCI and Citation Acceleration calculations
- **Paper-Author Mapping**: All metrics depend on accurate author-paper relationships
- **Citation Data**: Required for ANCI, Citation Acceleration, and PQI citation component

### Data Quality Considerations
- Missing citation data results in NaN values for acceleration metrics
- Unranked venues default to Tier D in PQI calculations
- Papers without awards receive 0.0 award scores
- Career length of 0 prevents calculation of ANCI and acceleration metrics

### Normalization and Fairness
- **ANCI**: Normalized by career length and adjusted for co-authorship
- **PQI**: Combines multiple factors with weighted averaging
- **Citation Acceleration**: Uses smoothing factors to handle edge cases
- **Award Scoring**: Normalized to prevent single awards from dominating

## Implementation Notes

- All calculations use 2025 as the current year reference point
- Career length includes the current year (hence +1 in calculation)
- Citation acceleration requires minimum career length thresholds
- PQI weights can be adjusted in the `PQI_WEIGHTS` dictionary
- Award weights and venue tiers are configurable constants 