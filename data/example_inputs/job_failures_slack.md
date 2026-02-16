# Troubleshooting Common Job Failures
> Source: #databricks-support Slack channel — pinned troubleshooting guide

## OutOfMemoryError
**Symptoms**: `java.lang.OutOfMemoryError: Java heap space` or driver/executor OOM kills.
**Root Causes & Fixes**:
- **Large collects**: Never use `.collect()` on large DataFrames. Use `.take(n)` or write to a table.
- **Broadcast too large**: If broadcast join exceeds `spark.sql.autoBroadcastJoinThreshold` (10MB default), increase it or disable with `-1`.
- **Skewed partitions**: One partition has far more data than others. Fix with `SKEW JOIN` hint or salting keys.
- **Driver OOM**: Increase driver memory with `spark.driver.memory` or avoid driver-side operations.

## Job Hangs / Stuck Stages
**Symptoms**: Job shows running but no task progress for 10+ minutes.
**Root Causes & Fixes**:
- **Shuffle spill**: Too many partitions writing to disk. Increase executor memory or reduce `spark.sql.shuffle.partitions`.
- **Data skew**: One task processes 100x more data. Check Spark UI → Stages → Task Duration distribution.
- **External dependencies**: Jobs waiting on external APIs or database locks. Add timeouts to all external calls.

## FileNotFoundException / Delta Conflicts
**Symptoms**: `FileNotFoundException` during reads or `ConcurrentAppendException` during writes.
**Root Causes & Fixes**:
- **VACUUM ran too aggressively**: Default retention is 7 days. Never set below `168 hours` without understanding downstream readers.
- **Concurrent writes**: Use Delta's `MERGE` with proper conditions or enable write conflict resolution with `delta.enableChangeDataFeed`.
- **Time travel expired**: If querying historical versions, ensure retention covers your query window.

## Best Practice: Alerting
- Set up **webhook notifications** on job failures to Slack/PagerDuty.
- Use `dbutils.notebook.exit("status")` to pass structured exit codes.
- Always configure **retry policies**: 2-3 retries with exponential backoff for transient failures.
