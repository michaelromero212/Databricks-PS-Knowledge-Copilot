# Auto Loader for Incremental Ingestion

Auto Loader incrementally and efficiently processes new data files as they arrive in cloud storage.

## Key Features
- **CloudFiles Source**: Use `format("cloudFiles")` to enable Auto Loader.
- **Schema Evolution**: Automatically detects and evolves schema as data changes.
- **Notification vs. Directory Listing**:
  - **File Notification**: Uses cloud queues (SQS, Event Grid) for scalability with millions of files.
  - **Directory Listing**: Simpler setup, good for smaller volumes.

## Example Code
```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/tmp/schema")
      .load("/path/to/source"))

df.writeStream.table("target_table")
```

## Best Practices
- Always define a `schemaLocation` to persist schema inference state.
- Use `trigger(availableNow=True)` for batch-like processing of streams.
