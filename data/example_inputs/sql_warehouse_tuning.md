# Databricks SQL Warehouse Tuning
> Source: Confluence — Platform Engineering Knowledge Base

## Warehouse Types
- **Classic**: Standard compute, good for general BI queries.
- **Pro**: Adds support for Unity Catalog governance, query federation, and predictive I/O.
- **Serverless**: Instant start, auto-scales, zero management. Best for most use cases — start here unless you need custom Spark configs.

## Sizing Guidelines
| Warehouse Size | vCPUs | Memory | Best For |
|---|---|---|---|
| 2X-Small | 4 | 16 GB | Light dashboards, < 10 concurrent users |
| Small | 8 | 32 GB | Standard BI, 10-25 concurrent users |
| Medium | 16 | 64 GB | Complex queries, 25-50 concurrent users |
| Large | 32 | 128 GB | Heavy analytics, 50+ concurrent users |

## Query Performance Tips
1. **Use Photon**: Ensure Photon is enabled — it accelerates SQL queries 2-8x for aggregations and joins.
2. **Materialized Views**: Pre-compute expensive aggregations with `CREATE MATERIALIZED VIEW`.
3. **Liquid Clustering**: Replace static partitioning with `CLUSTER BY (col)` for automatic data layout optimization.
4. **Result Caching**: SQL Warehouses cache results automatically. Identical queries return in milliseconds.
5. **Query Profile**: Use the Query Profile tab to identify bottlenecks — look for skewed partitions and excessive spilling.

## Cost Optimization
- Enable **auto-stop** (10-15 min) to avoid idle charges.
- Use **scaling policies** with min=1, max=3 clusters for burst capacity.
- Schedule warehouses to start/stop during business hours using Workflows.
