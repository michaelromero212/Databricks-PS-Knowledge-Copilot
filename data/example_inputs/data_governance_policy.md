# Data Governance & Compliance Policy
> Source: Google Drive — Data Engineering Team Shared Folder (PDF export)

## Classification Levels
All data stored in the Databricks lakehouse must be classified:
- **Public**: Non-sensitive data, open to all workspace users.
- **Internal**: Business data restricted to authenticated employees.
- **Confidential**: PII, financial records, and health data requiring encryption and access audits.
- **Restricted**: Regulated data (HIPAA, SOX, GDPR) requiring row-level security and data masking.

## Access Control with Unity Catalog
1. **Three-level namespace**: `catalog.schema.table` enables fine-grained permissions.
2. **Grant model**: Use `GRANT SELECT ON TABLE catalog.schema.table TO group_name`.
3. **Row-level security**: Apply row filters using `CREATE FUNCTION` and `ALTER TABLE ... SET ROW FILTER`.
4. **Column masking**: Mask sensitive columns with `ALTER TABLE ... ALTER COLUMN ... SET MASK`.
5. **Data lineage**: Unity Catalog automatically tracks column-level lineage across notebooks and jobs.

## Audit & Compliance
- Enable **audit logging** on all workspaces — logs are stored in the account's system tables.
- Query `system.access.audit` for who accessed what data and when.
- Set up **alerts** for unusual access patterns (e.g., bulk exports of Confidential tables).
- Retain audit logs for minimum 7 years for SOX compliance.

## PII Handling
- Never store raw PII in Bronze tables — apply tokenization or hashing at ingestion.
- Use Delta Sharing for secure external data sharing without data copies.
- Run automated PII scanning using custom UDFs or partner tools like Privacera.
