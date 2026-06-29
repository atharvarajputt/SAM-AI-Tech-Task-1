"""
SAM AI Technologies - Task 1: Web Scraping
Author: Atharv
Description: Scrapes book data from books.toscrape.com (a public practice site)
             and saves it as a custom dataset CSV.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://books.toscrape.com/catalogue/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SAMScraper/1.0)"
}

def get_star_rating(word):
    """Convert word-based rating to numeric."""
    mapping = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    return mapping.get(word, 0)

def scrape_books(max_pages=5):
    """Scrape book listings from books.toscrape.com."""
    all_books = []
    url = START_URL

    for page_num in range(1, max_pages + 1):
        print(f"Scraping page {page_num}...")
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            print(f"  Failed to fetch page {page_num} (status {response.status_code})")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.select("article.product_pod")

        for book in books:
            # Title
            title = book.select_one("h3 a")["title"]

            # Price
            price = book.select_one("p.price_color").text.strip().replace("Â", "").replace("£", "GBP ")

            # Star rating
            rating_class = book.select_one("p.star-rating")["class"][1]
            rating = get_star_rating(rating_class)

            # Availability
            availability = book.select_one("p.availability").text.strip()

            # Detail page URL
            detail_href = book.select_one("h3 a")["href"]
            detail_url = BASE_URL + detail_href.replace("../", "")

            all_books.append({
                "title": title,
                "price": price,
                "rating_stars": rating,
                "availability": availability,
                "detail_url": detail_url,
                "page_scraped": page_num
            })

        # Find next page link
        next_btn = soup.select_one("li.next a")
        if next_btn:
            url = BASE_URL + next_btn["href"]
        else:
            print("No more pages found.")
            break

        time.sleep(1)  # polite delay between requests

    return all_books

def save_to_csv(data, filename="books_dataset.csv"):
    """Save scraped data to CSV."""
    if not data:
        print("No data to save.")
        return

    fieldnames = ["title", "price", "rating_stars", "availability", "detail_url", "page_scraped"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"\nDataset saved: {filename} ({len(data)} records)")

def print_summary(data):
    """Print a quick summary of the dataset."""
    if not data:
        return

    avg_rating = sum(b["rating_stars"] for b in data) / len(data)
    in_stock = sum(1 for b in data if "In stock" in b["availability"])

    print("\n--- Dataset Summary ---")
    print(f"Total books scraped : {len(data)}")
    print(f"Average star rating : {avg_rating:.2f}")
    print(f"In stock            : {in_stock}")
    print(f"Out of stock        : {len(data) - in_stock}")
    print("\nSample records:")
    for book in data[:3]:
        print(f"  {book['title'][:50]:<50} | {book['price']} | {'⭐'*book['rating_stars']}")

if __name__ == "__main__":
    print("=== SAM AI Technologies — Web Scraping Task ===\n")
    books = scrape_books(max_pages=5)   # scrapes 5 pages × 20 books = 100 records
    save_to_csv(books, "/mnt/user-data/outputs/books_dataset.csv")
    print_summary(books)
