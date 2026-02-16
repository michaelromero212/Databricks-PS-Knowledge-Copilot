# Databricks Workflows Best Practices
> Source: Confluence — DevOps & Platform Engineering Wiki

## Job vs. Task Orchestration
- **Single-task jobs**: Simple ETL pipelines with one notebook. Use for straightforward batch processing.
- **Multi-task jobs**: Orchestrate complex DAGs with dependencies between notebooks, Python scripts, dbt tasks, and SQL queries — all in one workflow.
- **Avoid** external orchestrators (Airflow, Prefect) unless you have existing investments. Databricks Workflows provides native integration, monitoring, and cost tracking.

## Design Patterns
1. **Medallion Pipeline as a Workflow**:
   - Task 1: Bronze ingestion (Auto Loader)
   - Task 2: Silver transformation (depends on Task 1)
   - Task 3: Gold aggregation (depends on Task 2)
   - Task 4: Data quality checks (depends on Task 3)

2. **Fan-out / Fan-in**: Run independent tasks in parallel, then aggregate results.
   ```
   [Ingest Region A] ──┐
   [Ingest Region B] ──┼── [Merge All Regions] → [Build Reports]
   [Ingest Region C] ──┘
   ```

3. **Conditional execution**: Use `IF/ELSE` task conditions to handle success/failure branches.

## Parameterization
- Use **job parameters** to pass runtime values (dates, environments, file paths).
- Access in notebooks with `dbutils.widgets.get("param_name")`.
- Use `{{job.start_time.iso_date}}` for dynamic date parameters.

## Monitoring & Alerting
- Configure email/Slack/webhook notifications for `on_failure`, `on_success`, and `on_duration_threshold`.
- Set **SLA alerts** if a job exceeds expected duration (e.g., 2x average runtime).
- Use the **Runs API** (`/api/2.1/jobs/runs/list`) to build custom dashboards for job health.
