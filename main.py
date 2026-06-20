from crawler.crawler import fetch_page, load_urls_from_file
from engine.link_engine import generate_link_suggestions
from report import save_csv_report


URLS_FILE = "urls.txt"
OUTPUT_FILE = "output/internal_link_suggestions.csv"


def main():
    print("Internal Link Suggestion Tool")
    print("----------------------------------------")

    urls = load_urls_from_file(URLS_FILE)

    if not urls:
        print("No URLs found.")
        print(f"Please add URLs to {URLS_FILE}")
        return

    print(f"Loaded {len(urls)} URLs.")

    pages = []

    for url in urls:
        print(f"Crawling: {url}")

        page_data = fetch_page(url)

        if page_data:
            pages.append(page_data)

    print("----------------------------------------")
    print(f"Successfully crawled {len(pages)} pages.")

    if len(pages) < 2:
        print("Not enough pages to analyze.")
        return

    print("Analyzing content similarity...")

    suggestions_df = generate_link_suggestions(
        pages=pages,
        similarity_threshold=0.05,
        max_suggestions_per_page=5
    )

    save_csv_report(suggestions_df, OUTPUT_FILE)

    print("Done.")


if __name__ == "__main__":
    main()
