"""
Synthetic data generator for the retail sales pipeline challenge.

Generates 5 CSVs in the same directory as this script:
  customers.csv, products.csv, stores.csv, orders.csv, order_items.csv

The data intentionally contains realistic data-quality issues so that DBT
staging/cleaning models have something to handle. Issues are summarised at
the bottom of this file.

Usage:
    python landing/generate_data.py [--seed 42]

No third-party dependencies. Python 3.8+.
"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

N_CUSTOMERS = 500
N_PRODUCTS = 100
N_STORES = 20
N_ORDERS = 5_000
AVG_ITEMS_PER_ORDER = 3.5  # target ~15,000 order_items rows

OUTPUT_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Reference name pools (stdlib-only, no faker dependency)
# ---------------------------------------------------------------------------

FIRST_NAMES = [
    "Alex", "Sam", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery",
    "Quinn", "Skyler", "Drew", "Cameron", "Hayden", "Reese", "Rowan", "Sage",
    "Emerson", "Finley", "Harper", "Jamie", "Kai", "Logan", "Micah", "Noel",
    "Parker", "River", "Shay", "Toby", "Wren", "Zion", "Priya", "Wei",
    "Olu", "Mateo", "Aisha", "Yuki", "Ingrid", "Hiro", "Lena", "Diego",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
]

CITIES = {
    "USA": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
            "Philadelphia", "Seattle", "Denver", "Boston", "Austin"],
    "UK": ["London", "Manchester", "Birmingham", "Leeds", "Glasgow",
           "Edinburgh", "Bristol", "Liverpool"],
    "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"],
    "Germany": ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne"],
    "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
}

# Deliberate inconsistent representations of the same country (DQ issue).
COUNTRY_VARIANTS = {
    "USA": ["USA", "usa", "U.S.A.", "United States", "us"],
    "UK": ["UK", "United Kingdom", "uk", "U.K."],
    "Canada": ["Canada", "canada", "CA"],
    "Germany": ["Germany", "germany", "DE", "Deutschland"],
    "Australia": ["Australia", "australia", "AU"],
}

PRODUCT_CATEGORIES = {
    "Electronics": ["Audio", "Computers", "Mobile", "TV & Video"],
    "Home & Kitchen": ["Cookware", "Appliances", "Furniture", "Decor"],
    "Apparel": ["Mens", "Womens", "Kids", "Footwear"],
    "Sports": ["Outdoor", "Fitness", "Team Sports", "Cycling"],
    "Beauty": ["Skincare", "Haircare", "Makeup", "Fragrance"],
    "Books": ["Fiction", "Non-fiction", "Children", "Reference"],
}

PRODUCT_ADJECTIVES = ["Pro", "Ultra", "Lite", "Max", "Mini", "Classic",
                      "Deluxe", "Eco", "Smart", "Plus"]
PRODUCT_NOUNS = ["Widget", "Gadget", "Kit", "Set", "Bundle", "Edition",
                 "Series", "Model", "Pack", "Tool"]

STORE_NAME_PREFIXES = ["Downtown", "Westside", "Eastgate", "Northpark",
                       "Southbridge", "Riverside", "Hilltop", "Lakeview",
                       "Sunset", "Harbor", "Midtown", "Central", "Old Town",
                       "Uptown", "Bayfront", "Marketplace", "Plaza",
                       "Crossroads", "Greenfield", "Highland"]

REGIONS_BY_COUNTRY = {
    "USA": ["Northeast", "Southeast", "Midwest", "Southwest", "West"],
    "UK": ["England", "Scotland", "Wales"],
    "Canada": ["East", "Central", "West"],
    "Germany": ["North", "South", "East", "West"],
    "Australia": ["NSW", "VIC", "QLD", "WA", "SA"],
}

ORDER_STATUSES_CANONICAL = ["completed", "pending", "cancelled", "shipped",
                            "returned"]
# Same statuses with deliberate casing/spelling variation (DQ issue).
ORDER_STATUS_VARIANTS = [
    "completed", "Completed", "COMPLETED", "complete",
    "pending", "Pending", "PENDING",
    "cancelled", "Cancelled", "canceled", "CANCELLED",
    "shipped", "Shipped", "SHIPPED",
    "returned", "Returned",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def random_date(start: date, end: date) -> date:
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def maybe(prob: float) -> bool:
    return random.random() < prob


def write_csv(filename: str, header: list[str], rows: list[list]) -> None:
    path = OUTPUT_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"  wrote {len(rows):>6} rows -> {path.name}")


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

def generate_customers() -> list[list]:
    rows = []
    used_ids = set()
    for i in range(1, N_CUSTOMERS + 1):
        cid = i
        # ~0.4% true duplicate IDs (DQ issue) — repeat a previous id.
        if used_ids and maybe(0.004):
            cid = random.choice(list(used_ids))
        used_ids.add(cid)

        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        # ~3% have leading/trailing whitespace (DQ issue).
        if maybe(0.03):
            name = f"  {name} "

        country = random.choice(list(CITIES.keys()))
        city = random.choice(CITIES[country])
        country_str = random.choice(COUNTRY_VARIANTS[country])

        # Email construction with some DQ issues.
        email = f"{first.lower()}.{last.lower()}{cid}@example.com"
        if maybe(0.05):
            email = ""  # missing email
        elif maybe(0.02):
            email = email.replace("@", "")  # malformed: missing @
        elif maybe(0.02):
            email = email.upper()  # casing inconsistency

        # signup_date — some are null, some use a non-ISO format.
        signup = random_date(date(2018, 1, 1), date(2024, 12, 31))
        if maybe(0.02):
            signup_str = ""
        elif maybe(0.05):
            signup_str = signup.strftime("%m/%d/%Y")  # US format mixed in
        else:
            signup_str = signup.isoformat()

        rows.append([cid, name, email, city, country_str, signup_str])
    return rows


def generate_products() -> list[list]:
    rows = []
    for i in range(1, N_PRODUCTS + 1):
        category = random.choice(list(PRODUCT_CATEGORIES.keys()))
        sub_category = random.choice(PRODUCT_CATEGORIES[category])
        name = (f"{random.choice(PRODUCT_ADJECTIVES)} "
                f"{sub_category} {random.choice(PRODUCT_NOUNS)} "
                f"{random.randint(100, 999)}")

        unit_cost = round(random.uniform(2.0, 400.0), 2)
        # Markup: usually 20%-150%
        markup = random.uniform(1.2, 2.5)
        unit_price = round(unit_cost * markup, 2)

        # DQ: ~3% negative margin (cost > price).
        if maybe(0.03):
            unit_price = round(unit_cost * random.uniform(0.5, 0.95), 2)
        # DQ: ~1% negative price.
        if maybe(0.01):
            unit_price = -abs(unit_price)
        # DQ: ~2% missing category.
        cat_out = "" if maybe(0.02) else category
        # DQ: ~1% missing unit_cost.
        cost_out = "" if maybe(0.01) else unit_cost

        rows.append([i, name, cat_out, sub_category, cost_out, unit_price])
    return rows


def generate_stores() -> list[list]:
    rows = []
    countries = list(CITIES.keys())
    for i in range(1, N_STORES + 1):
        country = random.choice(countries)
        region = random.choice(REGIONS_BY_COUNTRY[country])
        city = random.choice(CITIES[country])
        name = f"{random.choice(STORE_NAME_PREFIXES)} {city}"
        country_str = random.choice(COUNTRY_VARIANTS[country])
        opened = random_date(date(2005, 1, 1), date(2023, 6, 30))
        # DQ: one store missing opened_date.
        opened_str = "" if i == 7 else opened.isoformat()
        rows.append([i, name, region, country_str, opened_str])
    return rows


def generate_orders(customer_ids: list[int],
                    store_ids: list[int]) -> list[list]:
    rows = []
    used_order_ids = set()
    for i in range(1, N_ORDERS + 1):
        oid = i
        # DQ: ~0.1% duplicate order IDs.
        if used_order_ids and maybe(0.001):
            oid = random.choice(list(used_order_ids))
        used_order_ids.add(oid)

        # DQ: ~2% orphan customer reference.
        if maybe(0.02):
            cust = random.randint(99_000, 99_999)
        else:
            cust = random.choice(customer_ids)

        # DQ: ~1% orphan store reference.
        if maybe(0.01):
            store = random.randint(900, 999)
        else:
            store = random.choice(store_ids)

        order_dt = random_date(date(2023, 1, 1), date(2025, 12, 31))
        # DQ: ~0.5% impossible future date (typo year).
        if maybe(0.005):
            order_dt = order_dt.replace(year=2099)
        order_str = order_dt.isoformat()

        # DQ: status with inconsistent casing / occasional null.
        if maybe(0.02):
            status = ""
        else:
            status = random.choice(ORDER_STATUS_VARIANTS)

        rows.append([oid, cust, store, order_str, status])
    return rows


def generate_order_items(order_ids: list[int],
                         product_ids: list[int]) -> list[list]:
    rows = []
    for oid in order_ids:
        # Each order gets 1..6 line items (mean ~3).
        n_items = max(1, int(random.gauss(AVG_ITEMS_PER_ORDER, 1.2)))
        # Track product_ids used on this order so we can deliberately create
        # the odd duplicate line later.
        seen_products: list[int] = []
        for _ in range(n_items):
            # DQ: ~1% orphan product reference.
            if maybe(0.01):
                pid = random.randint(9_000, 9_999)
            else:
                pid = random.choice(product_ids)

            qty = random.randint(1, 5)
            # DQ: ~1% zero or negative quantity.
            if maybe(0.01):
                qty = random.choice([0, -1, -2])

            # discount_pct usually 0.0 - 0.4 as a decimal.
            discount = round(random.choice(
                [0.0, 0.0, 0.0, 0.05, 0.10, 0.15, 0.20, 0.30]
            ), 2)
            # DQ: ~3% mistakenly stored as a percent (e.g. 25 instead of 0.25).
            if maybe(0.03):
                discount = float(random.randint(5, 40))
            # DQ: ~0.5% absurd discount > 100%.
            if maybe(0.005):
                discount = round(random.uniform(1.5, 3.0), 2)

            rows.append([oid, pid, qty, discount])
            seen_products.append(pid)

        # DQ: ~0.3% chance of producing a duplicate (order_id, product_id) row.
        if seen_products and maybe(0.003):
            rows.append([oid,
                         random.choice(seen_products),
                         random.randint(1, 3),
                         0.0])
    return rows


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42,
                        help="random seed (default: 42)")
    args = parser.parse_args()
    random.seed(args.seed)

    print(f"Generating CSVs in {OUTPUT_DIR} (seed={args.seed})")

    customers = generate_customers()
    products = generate_products()
    stores = generate_stores()

    customer_ids = [row[0] for row in customers]
    product_ids = [row[0] for row in products]
    store_ids = [row[0] for row in stores]

    orders = generate_orders(customer_ids, store_ids)
    order_ids = [row[0] for row in orders]
    order_items = generate_order_items(order_ids, product_ids)

    write_csv("customers.csv",
              ["customer_id", "name", "email", "city", "country",
               "signup_date"],
              customers)
    write_csv("products.csv",
              ["product_id", "name", "category", "sub_category",
               "unit_cost", "unit_price"],
              products)
    write_csv("stores.csv",
              ["store_id", "name", "region", "country", "opened_date"],
              stores)
    write_csv("orders.csv",
              ["order_id", "customer_id", "store_id", "order_date", "status"],
              orders)
    write_csv("order_items.csv",
              ["order_id", "product_id", "quantity", "discount_pct"],
              order_items)

    print("Done.")


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Data quality issues intentionally seeded (handle in DBT staging):
# ---------------------------------------------------------------------------
# customers.csv
#   - rare duplicate customer_id
#   - missing or malformed emails (no @, uppercased, empty)
#   - inconsistent country casing ("USA", "usa", "U.S.A.", "United States")
#   - mixed signup_date formats (ISO + US m/d/Y) and some blanks
#   - leading/trailing whitespace in names
# products.csv
#   - some unit_cost > unit_price (negative margin)
#   - occasional negative unit_price
#   - missing category and unit_cost
# stores.csv
#   - inconsistent country casing
#   - one store missing opened_date (store_id = 7)
# orders.csv
#   - rare duplicate order_id
#   - orphan customer_id / store_id references
#   - status with mixed casing/spelling and some blanks
#   - rare impossible future dates (year 2099)
# order_items.csv
#   - orphan product_id references
#   - zero or negative quantities
#   - discount_pct stored as decimal AND occasionally as a percent (25 vs 0.25)
#   - absurd discounts > 100%
#   - rare duplicate (order_id, product_id) lines
# ---------------------------------------------------------------------------
