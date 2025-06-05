import csv
from collections import Counter

def count_papers_by_acceptance(file_path):
    acceptance_counts = Counter()

    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            acceptance_counts[row['Accepted To']] += 1

    return acceptance_counts

def save_main_and_find_papers(file_path, output_file):
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        fieldnames = csv_reader.fieldnames if csv_reader.fieldnames else []
        
        with open(output_file, mode='w', encoding='utf-8', newline='') as out_csv:
            csv_writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
            csv_writer.writeheader()
            for row in csv_reader:
                if row['Accepted To'] in ['MAIN', 'FIND']:
                    csv_writer.writerow(row)

def get_unique_track_themes(file_path):
    unique_themes = set()

    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            unique_themes.add(row['Track Theme'])

    return sorted(unique_themes)

if __name__ == "__main__":
    # file_path = "ACL25 Accepted Paper with Track Info.csv"
    # output_file = "ACL25_ThemeData.csv"

    # acceptance_counts = count_papers_by_acceptance(file_path)
    # for acceptance, count in acceptance_counts.items():
    #     print(f"Number of papers accepted to {acceptance}: {count}")

    # save_main_and_find_papers(file_path, output_file)
    # print(f"Papers accepted to MAIN and FIND have been saved to {output_file}.")

    unique_themes = get_unique_track_themes(file_path="ACL25_ThemeData.csv")
    print("Unique Track Themes:")
    for theme in unique_themes:
        print(f"- {theme}")
    print(f"Number of themes: {len(unique_themes)}")