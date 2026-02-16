# Migrating from Hive to Delta Lake
> Source: Email digest — Data Platform Team weekly summary

## Why Migrate?
- **ACID transactions**: Delta provides full ACID support — no more corrupted reads during writes.
- **Time travel**: Query previous versions with `SELECT * FROM table VERSION AS OF 5`.
- **Performance**: Z-Ordering and data skipping deliver 10-100x faster queries vs. Hive.
- **Schema enforcement**: Delta rejects writes that don't match the table schema, preventing data quality issues.

## Migration Steps
1. **In-place conversion** (fastest, no data copy):
   ```sql
   CONVERT TO DELTA parquet.`/path/to/hive/table`
   PARTITIONED BY (date STRING)
   ```

2. **CTAS migration** (for restructuring):
   ```sql
   CREATE TABLE delta_table
   USING DELTA
   LOCATION '/new/path'
   AS SELECT * FROM hive_table
   ```

3. **Incremental migration** with Auto Loader:
   - Point Auto Loader at Hive's underlying storage.
   - Stream new files into a Delta table.
   - Backfill historical data with a batch job.

## Post-Migration Checklist
- [ ] Run `OPTIMIZE` to compact small files from Hive.
- [ ] Apply `ZORDER BY` on frequently queried columns.
- [ ] Enable Change Data Feed if downstream consumers need CDC.
- [ ] Update all downstream jobs to read from Delta tables.
- [ ] Set `VACUUM` schedule (weekly) to clean up old files.
- [ ] Validate row counts: `SELECT COUNT(*) FROM hive_table` vs. `delta_table`.
