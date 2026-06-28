# scraper.py
# Runs the scraper for all suppliers and saves results to data/prices.csv.
# Phase 1: one supplier (scrape_supplier_one) is fully built.
# To add Supplier 2: copy the scrape_supplier_one() function, rename it scrape_supplier_two(),
# update the three REPLACE values, and add scrape_supplier_two() inside main().

import requests
from bs4 import BeautifulSoup
import csv
import os
from datetime import date
from normalizer import normalize

CSV_PATH = "data/prices.csv"
CSV_HEADERS = ["date", "supplier", "raw_description", "standard_name", "category", "price", "unit"]


def save_price(supplier, raw_description, price, unit):
    """
    Normalizes the item name and appends one row to prices.csv.
    Creates the file and header row automatically on first run.
    """
    standard_name, category = normalize(raw_description)
    os.makedirs("data", exist_ok=True)
    file_exists = os.path.isfile(CSV_PATH)

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "date": str(date.today()),
            "supplier": supplier,
            "raw_description": raw_description,
            "standard_name": standard_name,
            "category": category,
            "price": price,
            "unit": unit,
        })


def scrape_supplier_one():
    """
    HOW TO FIND YOUR THREE REQUIRED VALUES:

    ① SUPPLIER_NAME — just type the supplier's business name as a plain string.

    ② URL — go to the supplier's website, navigate to their lumber or materials catalog page,
       and copy the full URL from your browser's address bar.

    ③ CSS SELECTORS — this is the only technical step:
       a. On the catalog page, right-click on any product name and choose "Inspect".
       b. Chrome opens a panel. The highlighted HTML line shows the tag and class for that element.
          Example: <h2 class="product-title">2x4x8 SPF Stud</h2>
          Your selector for that would be: "h2.product-title"
          (tag name + period + class name, no spaces)
       c. Right-click the highlighted line → Copy → Copy selector.
          Paste it to confirm, then simplify to "tag.classname" format.
       d. Repeat for the price element.
       e. Find the container that wraps EACH individual product card — the parent div of both
          the name and price. Its selector becomes PRODUCT_CONTAINER_SELECTOR.

    If the page shows "No products found" after you run it, your container selector is wrong.
    Go back to Chrome, inspect the outermost wrapper of a single product card, and retry.
    """

    # ── THREE VALUES TO REPLACE ───────────────────────────────────────────────
    SUPPLIER_NAME          = "TESCO Building Supplies"          # ① Replace
    URL                    = "https://tescobs.com/collections/spf"  # ② Replace
    PRODUCT_CONTAINER_SEL  = "product-block.product-block"                # ③a Replace
    PRODUCT_NAME_SEL       = "div.product-block__title"                 # ③b Replace
    PRODUCT_PRICE_SEL      = "span.price__current"                      # ③c Replace
    UNIT                   = "each"                            # "each", "per board", "per sheet", "per bag", "per m3"
    # ─────────────────────────────────────────────────────────────────────────

    print(f"\nScraping {SUPPLIER_NAME}...")

    headers = {
        # Identifies your scraper as a normal Chrome browser.
        # Many sites block requests that don't send this header.
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(URL, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  ERROR: Could not reach {SUPPLIER_NAME}. Reason: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    products = soup.select(PRODUCT_CONTAINER_SEL)

    if not products:
        print(f"  WARNING: No products found with selector '{PRODUCT_CONTAINER_SEL}'.")
        print(f"  Open {URL} in Chrome, right-click a product card, inspect the wrapper div, and update PRODUCT_CONTAINER_SEL.")
        return

    saved = 0
    for product in products:
        name_tag  = product.select_one(PRODUCT_NAME_SEL)
        price_tag = product.select_one(PRODUCT_PRICE_SEL)

        if not name_tag or not price_tag:
            continue

        raw_name   = name_tag.get_text(strip=True)
        price_text = price_tag.get_text(strip=True)

        # Strip everything except digits and the decimal point
        cleaned = price_text.replace("$", "").replace(",", "").replace("CAD", "").strip()

        try:
            price = float(cleaned)
        except ValueError:
            print(f"  SKIP: Could not parse price '{price_text}' for '{raw_name}'")
            continue

        save_price(SUPPLIER_NAME, raw_name, price, UNIT)
        print(f"  SAVED: {raw_name}  →  ${price:.2f}/{UNIT}")
        saved += 1

    print(f"  {saved} items saved for {SUPPLIER_NAME}.")


def main():
    print(f"=== Price Scraper — {date.today()} ===")
    scrape_supplier_one()
    # When Supplier 2 is ready, uncomment the next line:
    # scrape_supplier_two()
    print("\n=== Scrape complete ===")


if __name__ == "__main__":
    main()