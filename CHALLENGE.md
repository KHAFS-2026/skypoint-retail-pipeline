# AI Coding Challenge: End-to-End Data Pipeline with DBT & Power BI

## 1. Objective

Build an end-to-end data pipeline using **Claude Code** (or another AI coding assistant of your choice) as your primary development tool. You will ingest raw CSV files from a landing zone, transform them into a clean dimensional model using DBT, and surface insights through a Power BI semantic model and report.

The challenge is scoped to be completable in **2–3 hours**.

We are evaluating not only the working pipeline but also your judgement, your data modelling decisions, your use of the AI tool, and the clarity of your documentation.

---

## 2. Use Case: Retail Sales Analytics

A mid-sized retail company drops daily sales exports as CSV files into a landing folder. The analytics team needs a reliable pipeline that:

1. Picks up raw CSVs from the landing zone
2. Loads them into a database
3. Transforms them into a clean star schema using DBT
4. Powers a Power BI report that answers questions like:
   - What are total sales by store, category, and month?
   - Who are the top 10 customers by revenue?
   - Which products have the highest and lowest margins?
   - How does sales performance trend over time?

---

## 3. Provided Inputs

You will work with the following CSV files in a `landing/` directory. You may either use the dataset we provide or generate your own synthetic data — if you generate it, include the generator script in your repo so the data is reproducible.

| File | Description | Approx. Rows |
|------|-------------|--------------|
| `customers.csv` | Customer master (id, name, email, city, country, signup_date) | ~500 |
| `products.csv` | Product catalogue (id, name, category, sub_category, unit_cost, unit_price) | ~100 |
| `stores.csv` | Store master (id, name, region, country, opened_date) | ~20 |
| `orders.csv` | Order header (id, customer_id, store_id, order_date, status) | ~5,000 |
| `order_items.csv` | Order line items (order_id, product_id, quantity, discount_pct) | ~15,000 |

The files contain some realistic data quality issues. Part of the challenge is deciding how to handle them.

---

## 4. What You Need to Build

### Pipeline
- **Landing zone:** A folder containing the raw CSV files
- **Database:** Your choice (PostgreSQL and DuckDB both work well with DBT)
- **Loader:** A mechanism that reads CSVs from the landing zone and lands them in a `raw` schema
- **Transformations:** A DBT project that turns the raw data into a usable dimensional model
- **BI layer:** A Power BI Desktop file (`.pbix`) connecting to the transformed data, with a semantic model and a one-page report

### Dockerisation (Mandatory for the data pipeline)

The database, loader, and DBT must run inside Docker.

- Use Docker Compose to orchestrate the services
- The pipeline must run end-to-end with a **single command**:
  ```
  docker compose up --build
  ```
  This should: start the database, load the CSVs from `landing/` into the `raw` schema, then run the DBT transformations and tests.
- Persistent data must survive container restarts
- No manual setup beyond what is documented in the README

> **Note on Power BI:** Power BI Desktop is a Windows application and runs outside Docker. The `.pbix` file should connect to the database exposed from the Docker stack. Document the connection details in the README.

### Power BI Deliverable
- A semantic model with relationships
- DAX measures that answer the business questions above
- A one-page report with multiple visuals
- The `.pbix` file committed to the repo
- Screenshots embedded in the README (so assessors can see the output without opening the file)

---

## 5. Submission

- Push your solution to a **GitHub repository** (public or shared with the assessors)
- Share the repo link before the submission deadline

Suggested folder structure (you are free to deviate):

```
├── landing/                  # raw CSVs (or a generator script)
├── loader/                   # loader script(s)
├── dbt_project/              # your DBT project
├── powerbi/
│   ├── retail_sales.pbix
│   └── screenshots/
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 6. README Requirements

Your `README.md` is a critical part of the submission. It must include:

**a) Project Overview** — what the pipeline does and the business questions it answers.

**b) Architecture Diagram or Description** — how the landing zone, loader, database, DBT, and Power BI fit together.

**c) How to Run**
```
git clone <your-repo-url>
cd <project-folder>
docker compose up --build
```
Document expected output and runtime.

**d) How to Connect Power BI** — exact host, port, database, username, and password to use from Power BI Desktop.

**e) Data Model Description** — a brief walkthrough of your dimensional model: the fact table grain, each dimension, and any noteworthy business logic.

**f) DAX Measures** — list the measures you implemented and what each one answers.

**g) Tech Stack** — frameworks, libraries, and versions.

**h) Screenshots** — at least 2 screenshots of the Power BI report.

**i) Known Limitations** — anything incomplete or intentionally scoped out.

---

## 7. Important Notes

- The assessor will clone your repo on a fresh machine and run `docker compose up --build`. The pipeline must complete successfully without any additional setup.
- The Power BI file must open and refresh against the dockerised database with the connection details in the README.
- You may use any open-source DBT packages — document any non-trivial dependencies.
- Sample data must be synthetic. Do not use any real customer or transactional data.
- If you encounter limitations or rough edges with the AI coding tool, note them — your feedback on the tool is also valuable.

---

## 8. Suggested Time Allocation (~2.5 hours)

- Data + Docker + database setup — 30 min
- Loader + raw schema — 20 min
- DBT models — 45 min
- DBT tests + documentation — 20 min
- Power BI semantic model + measures + report — 30 min
- README + screenshots + commit cleanup — 15 min

Good luck.
