# Photon Engine Overview

Photon is a high-performance query engine for Databricks, written in C++ to speed up SQL and DataFrame workloads.

## When to Use Photon
- **SQL Workloads**: Highly effective for BI queries, aggregations, and joins.
- **Large Scale ETL**: Speeds up heavy transformations and writes to Delta tables.
- **Complex Logic**: Benefits queries with complex regex, JSON parsing, or subqueries.

## Limitations
- Photon does not support UDFs (User Defined Functions) in Java/Scala/Python directly; it falls back to the JVM for those parts of the query.
- Not all Spark operators are vectorized yet, though coverage is extensive.

## Enabling Photon
Select the "Photon" checkbox when configuring your cluster or use a Databricks SQL Warehouse which has Photon enabled by default.
