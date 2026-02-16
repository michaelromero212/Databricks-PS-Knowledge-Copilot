# Medallion Architecture Guide
> Source: Google Drive — Solutions Architecture Shared Folder

## Overview
The Medallion Architecture (Bronze → Silver → Gold) is the recommended pattern for organizing data in the Databricks Lakehouse.

## Bronze Layer (Raw)
- **Purpose**: Land raw data exactly as received from source systems.
- **Format**: Store as Delta tables, preserving original schema.
- **Metadata**: Add ingestion timestamp (`_ingest_ts`), source system name, and batch ID.
- **Retention**: Keep raw data for 90+ days for reprocessing and auditing.
- **Sources**: APIs, Kafka streams, file drops (S3/ADLS/GCS), database CDC, Slack exports, CRM dumps.

## Silver Layer (Cleaned)
- **Purpose**: Cleaned, deduplicated, and conformed data.
- **Transformations**:
  - Remove duplicates with `MERGE` or `dropDuplicates()`.
  - Standardize column names (snake_case), data types, and null handling.
  - Apply data quality rules with Delta Live Tables Expectations.
  - Join reference data (country codes, product IDs).
- **Schema**: Enforce strict schemas — reject bad records to a quarantine table.

## Gold Layer (Business)
- **Purpose**: Business-level aggregates and feature tables ready for consumption.
- **Examples**:
  - `daily_revenue_by_region` — aggregated from Silver order tables.
  - `customer_360` — unified customer view joining multiple Silver tables.
  - `ml_feature_store` — pre-computed features registered in Feature Store.
- **Consumers**: BI dashboards (Power BI, Tableau), ML models, data apps, and analysts.

## Anti-Patterns to Avoid
- ❌ Skipping Silver and going Bronze → Gold directly — creates brittle, hard-to-debug pipelines.
- ❌ Storing derived data back in Bronze — pollutes the raw integrity layer.
- ❌ No data quality layer — always add validation between Bronze → Silver.
- ❌ Over-normalizing Gold — Gold should be denormalized for fast reads and BI performance.
