import pandas as pd
import json
import ast
from collections import defaultdict, Counter
import logging
from datetime import datetime
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/author_citations.log'),
        logging.StreamHandler()
    ]
)

class AuthorYearlyCitationsExtractor:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.researchers = None
        self.authorships = None
        self.citations = None
        self.papers = None
        
    def load_data(self):
        """Load all required CSV files"""
        logging.info("Loading data files...")
        
        try:
            # Load researcher profiles
            self.researchers = pd.read_csv(f'{self.data_dir}/researcher_profiles.csv')
            logging.info(f"Loaded {len(self.researchers)} researcher profiles")
            
            # Load authorships
            self.authorships = pd.read_csv(f'{self.data_dir}/authorships.csv')
            logging.info(f"Loaded {len(self.authorships)} authorship records")
            
            # Load citation edges
            self.citations = pd.read_csv(f'{self.data_dir}/citation_edges.csv')
            logging.info(f"Loaded {len(self.citations)} citation edges")
            
            # Load paper info
            self.papers = pd.read_csv(f'{self.data_dir}/paper_info.csv')
            logging.info(f"Loaded {len(self.papers)} paper records")
            
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            raise
    
    def create_paper_id_mapping(self):
        """Create mapping between different paper ID formats"""
        logging.info("Creating paper ID mapping...")
        
        # Create a mapping from paper_info IDs to paper_id used in authorships
        paper_mapping = {}
        
        # Check if papers data is loaded
        if self.papers is None:
            raise ValueError("Paper data not loaded. Call load_data() first.")
        
        # Map corpus_id to paper_id (they seem to be the same based on the data examination)
        for _, row in self.papers.iterrows():
            corpus_id = row['corpus_id']
            s2_id = row['s2_id']
            acl_id = row['acl_id']
            year = row['year']
            
            # Store all possible mappings
            if pd.notna(corpus_id):
                paper_mapping[corpus_id] = {
                    'corpus_id': corpus_id,
                    's2_id': s2_id,
                    'acl_id': acl_id,
                    'year': year
                }
            
            if pd.notna(s2_id):
                paper_mapping[s2_id] = {
                    'corpus_id': corpus_id,
                    's2_id': s2_id,
                    'acl_id': acl_id,
                    'year': year
                }
                
            if pd.notna(acl_id):
                paper_mapping[acl_id] = {
                    'corpus_id': corpus_id,
                    's2_id': s2_id,
                    'acl_id': acl_id,
                    'year': year
                }
        
        logging.info(f"Created mapping for {len(paper_mapping)} unique papers")
        return paper_mapping
    
    def get_author_papers(self, author_id):
        """Get all papers for a given author"""
        if self.authorships is None:
            raise ValueError("Authorships data not loaded. Call load_data() first.")
        author_papers = self.authorships[self.authorships['researcher_id'] == author_id]
        return author_papers['paper_id'].unique().tolist()
    
    def get_paper_citations_by_year(self, paper_id, paper_mapping):
        """Get citations for a paper, grouped by year of citing papers"""
        if self.citations is None:
            raise ValueError("Citations data not loaded. Call load_data() first.")
        
        # Find papers that cite this paper
        citing_papers = self.citations[self.citations['cited_paper_id'] == paper_id]['citing_paper_id'].unique()
        
        yearly_citations = defaultdict(int)
        
        for citing_paper_id in citing_papers:
            # Try to find the citing paper in our mapping
            if citing_paper_id in paper_mapping:
                citing_year = paper_mapping[citing_paper_id]['year']
                if pd.notna(citing_year) and citing_year > 0:
                    yearly_citations[int(citing_year)] += 1
        
        return dict(yearly_citations)
    
    def get_author_yearly_citations(self, author_id, paper_mapping):
        """Get yearly citation counts for an author"""
        # Get all papers by this author
        author_papers = self.get_author_papers(author_id)
        
        # Aggregate citations by year across all papers
        yearly_citations = defaultdict(int)
        
        for paper_id in author_papers:
            paper_citations = self.get_paper_citations_by_year(paper_id, paper_mapping)
            for year, count in paper_citations.items():
                yearly_citations[year] += count
        
        return dict(yearly_citations)
    
    def extract_author_data(self):
        """Extract author data and their yearly citations"""
        logging.info("Starting author data extraction...")
        
        # Create paper ID mapping
        paper_mapping = self.create_paper_id_mapping()
        
        # Initialize results
        results = []
        if self.researchers is None:
            raise ValueError("Researchers data not loaded. Call load_data() first.")
        total_authors = len(self.researchers)
        
        for idx, (_, author) in enumerate(self.researchers.iterrows()):
            if idx % 1000 == 0:
                logging.info(f"Processing author {idx + 1}/{total_authors}")
            
            try:
                author_id = author['researcher_id']
                first_name = author['first_name'] if pd.notna(author['first_name']) else ''
                last_name = author['last_name'] if pd.notna(author['last_name']) else ''
                
                # Create full name
                full_name = f"{first_name} {last_name}".strip()
                if not full_name:
                    full_name = f"Author_{author_id}"
                
                # Get yearly citations
                yearly_citations = self.get_author_yearly_citations(author_id, paper_mapping)
                
                # Sort by year
                yearly_citations_sorted = dict(sorted(yearly_citations.items()))
                
                # Convert to JSON string for CSV storage
                yearly_citations_json = json.dumps(yearly_citations_sorted)
                
                results.append({
                    'author_id': author_id,
                    'name': full_name,
                    'yearly_citations': yearly_citations_json
                })
                
            except Exception as e:
                logging.error(f"Error processing author {author_id}: {e}")
                continue
        
        logging.info(f"Successfully processed {len(results)} authors")
        return results
    
    def save_results(self, results, output_file='data/author_yearly_citations.csv'):
        """Save results to CSV file"""
        logging.info(f"Saving results to {output_file}")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Convert to DataFrame and save
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False)
        
        logging.info(f"Saved {len(df)} author records to {output_file}")
        
        # Print some statistics
        total_citations = 0
        authors_with_citations = 0
        
        for _, row in df.iterrows():
            yearly_citations = json.loads(row['yearly_citations'])
            author_total = sum(yearly_citations.values())
            if author_total > 0:
                authors_with_citations += 1
                total_citations += author_total
        
        logging.info(f"Total citations across all authors: {total_citations}")
        logging.info(f"Authors with at least one citation: {authors_with_citations}")
        
        return df
    
    def run(self, output_file='data/author_yearly_citations.csv'):
        """Run the complete extraction process"""
        logging.info("Starting author yearly citations extraction...")
        
        try:
            # Load data
            self.load_data()
            
            # Extract author data
            results = self.extract_author_data()
            
            # Save results
            df = self.save_results(results, output_file)
            
            logging.info("Extraction completed successfully!")
            return df
            
        except Exception as e:
            logging.error(f"Error in extraction process: {e}")
            raise

def main():
    """Main function"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Initialize extractor
    extractor = AuthorYearlyCitationsExtractor()
    
    # Run extraction
    try:
        df = extractor.run()
        print(f"\nExtraction completed! Results saved to data/author_yearly_citations.csv")
        print(f"Total authors processed: {len(df)}")
        
        # Show sample results
        print("\nSample results:")
        for i, (_, row) in enumerate(df.head(5).iterrows()):
            yearly_citations = json.loads(row['yearly_citations'])
            print(f"{row['name']} (ID: {row['author_id']}): {yearly_citations}")
            
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Main execution error: {e}")

if __name__ == "__main__":
    main() 