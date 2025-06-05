from acl_anthology import Anthology

def search_collection():
    collection = anthology.get("2024.acl")
    all_unique_authors = set()
    total_papers = 0
    
    print(f"Analyzing collection: {collection.id}\n")
    
    for volume in collection.volumes():
        volume_papers = 0
        volume_unique_authors = set()
        
        for paper in volume.papers():
            volume_papers += 1
            total_papers += 1
            for author in paper.authors:
                researcher = author.name
                volume_unique_authors.add(researcher)
                all_unique_authors.add(researcher)
        
        print(f"Volume: {volume.title}")
        print(f"  Number of papers: {volume_papers}")
        print(f"  Number of unique authors: {len(volume_unique_authors)}\n")

    print(f"Total {total_papers} papers and {len(all_unique_authors)} unique authors across all volumes in collection {collection.id}")

 
if __name__ == "__main__":

    try:
        anthology = Anthology.from_repo()
    except:
        try:
            anthology = Anthology()
        except:
            print("Could not initialize anthology. Make sure the data is available.")
            import sys
            sys.exit(1)

    search_collection()



