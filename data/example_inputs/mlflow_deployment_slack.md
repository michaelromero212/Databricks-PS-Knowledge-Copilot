# MLflow Model Deployment on Databricks
> Source: #ml-engineering Slack channel — deployment runbook

## Model Registry Workflow
1. **Train & log**: Use `mlflow.log_model()` to save model artifacts, parameters, and metrics.
2. **Register**: Push to Unity Catalog Model Registry with `mlflow.register_model("runs:/<run_id>/model", "catalog.schema.model_name")`.
3. **Stage transitions**: Move models through `None → Staging → Production → Archived`.
4. **Approval gates**: Configure approval policies so only ML leads can promote to Production.

## Serving Options
| Method | Latency | Scale | Best For |
|---|---|---|---|
| Model Serving (real-time) | < 100ms | Auto-scales | APIs, real-time predictions |
| Batch inference | Minutes | Cluster-based | Nightly scoring, bulk predictions |
| Streaming inference | Seconds | Structured Streaming | Near-real-time event processing |
| Edge deployment | Varies | Device-dependent | IoT, mobile apps |

## Model Serving Setup
```python
# Deploy to a serving endpoint
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
w.serving_endpoints.create(
    name="fraud-detection-v2",
    config={
        "served_models": [{
            "model_name": "catalog.schema.fraud_model",
            "model_version": "3",
            "workload_size": "Small",
            "scale_to_zero_enabled": True
        }]
    }
)
```

## Monitoring in Production
- **Data drift**: Compare incoming feature distributions against training data baselines.
- **Model performance**: Track prediction accuracy, latency percentiles (p50, p95, p99).
- **A/B testing**: Route traffic between model versions using traffic percentage splits.
- **Alerts**: Set up Lakehouse Monitoring to alert on drift or accuracy degradation.

## Common Pitfalls
- Not versioning training data alongside models — use Delta table versions for reproducibility.
- Deploying without a shadow/canary phase — always test with <5% traffic first.
- Missing feature engineering parity between training and serving — use Feature Store for consistency.
