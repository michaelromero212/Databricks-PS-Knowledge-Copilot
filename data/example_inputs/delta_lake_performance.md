# Delta Lake Performance Tuning

## MERGE Optimization
To optimize MERGE operations on large Delta tables:

1. **Pruning**: Ensure your MERGE condition uses partition columns to prune files.
2. **Z-Ordering**: Run `OPTIMIZE ZORDER BY (col)` on columns frequently used in the MERGE condition.
3. **Auto Optimize**: Enable Auto Optimize for automatic file compaction during writes.
4. **Shuffle**: Adjust `spark.databricks.delta.merge.repartitionBeforeWrite.enabled` to true if you have many small files.

## General Tips
- Use `VACUUM` to remove old files.
- Use `OPTIMIZE` regularly to compact small files.
