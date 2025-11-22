# Unity Catalog Best Practices

## Overview
Unity Catalog provides a unified governance solution for all data and AI assets including files, tables, and machine learning models in your lakehouse.

## Key Recommendations

1. **Single Metastore**: Use a single metastore per region to simplify management.
2. **Catalog Structure**: Organize data into a 3-level namespace: `catalog.schema.table`.
   - Use catalogs for broad domains (e.g., `prod`, `dev`, `sandbox`).
   - Use schemas for specific projects or teams.
3. **Managed vs. External Tables**: Prefer managed tables for better performance and simplified administration. Use external tables when you need to access data from other tools directly.
4. **Identity Federation**: Configure SCIM provisioning to sync users and groups from your IdP (e.g., Azure AD, Okta) to Databricks.

## Security
- Grant permissions at the group level, not user level.
- Use `GRANT USAGE ON CATALOG` to allow traversal.
