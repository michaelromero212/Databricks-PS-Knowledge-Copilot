# Cluster Sizing & Configuration Guide
> Source: #databricks-engineering Slack channel — compiled from team discussions

## Interactive vs. Job Clusters
- **Interactive clusters** are best for development and ad-hoc analysis. Set auto-termination to 30-60 minutes to avoid idle costs.
- **Job clusters** spin up for a specific task and terminate automatically. Always prefer job clusters in production.

## Right-Sizing Recommendations
1. **Start small**: Begin with 2-4 worker nodes and scale up based on Spark UI metrics.
2. **Memory-optimized** instances (e.g., `r5.xlarge`) work best for caching-heavy workloads, complex joins, and broadcast joins.
3. **Compute-optimized** instances (e.g., `c5.xlarge`) are better for CPU-bound transformations, ML training, and ETL with minimal shuffle.
4. **Autoscaling**: Enable autoscaling with min=2, max=8 workers for variable workloads. Set `spark.databricks.aggressiveWindowDownS` to control scale-down speed.

## Spot Instances
- Use **spot instances** for fault-tolerant workloads (batch ETL, training). Savings of 60-80%.
- Avoid spot for **streaming** or **time-critical SLA** jobs — use on-demand instead.
- Set a **fallback to on-demand** to prevent job failures when spot capacity is unavailable.

## Common Mistakes
- Over-provisioning clusters "just in case" — monitor with Ganglia/Spark UI first.
- Running notebooks on all-purpose clusters in production — always migrate to job clusters.
- Not setting `spark.sql.shuffle.partitions` — default is 200, which is too high for small datasets and too low for very large ones.
