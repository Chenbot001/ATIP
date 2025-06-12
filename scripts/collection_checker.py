from acl_anthology import Anthology

def search_collection(collection_id):
    collection = anthology.get(collection_id)
    if len(collection) == 0:
        print(f"Collection {collection_id} not found.")
        return False
    elif len(collection) > 1:
        return True
    # all_unique_authors = set()
    # total_papers = 0
    
    # print(f"Analyzing collection: {collection.id}\n")
    
    # for volume in collection.volumes():
    #     volume_papers = 0
    #     volume_unique_authors = set()
        
    #     for paper in volume.papers():
    #         volume_papers += 1
    #         total_papers += 1
    #         for author in paper.authors:
    #             researcher = author.name
    #             volume_unique_authors.add(researcher)
    #             all_unique_authors.add(researcher)
        
    #     print(f"Volume: {volume.title}")
    #     print(f"  Number of papers: {volume_papers}")
    #     print(f"  Number of unique authors: {len(volume_unique_authors)}\n")

    # print(f"Total {total_papers} papers and unique authors across all volumes in collection {collection.id}: {len(all_unique_authors)}")

 
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

    inv_col = []

    with open("c:\\Users\\ssr\\EJC\\AI_Researcher_Network\\data\\acl_collections.txt", "r") as file:
        collection_ids = [line.strip() for line in file]

    for collection_id in collection_ids:
        result = search_collection(collection_id)
        if result is False:
            inv_col.append(collection_id)

    if inv_col:
        print("\nInvalid collections:")
        for col in inv_col:
            print(f" {col}")
    else:
        print("\nAll collections are valid.")

