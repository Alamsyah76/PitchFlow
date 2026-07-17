# Safe Migration Report

Date: 2026-05-26

## Status

PASS for static migration safety checks. Live Supabase/PostgreSQL migration execution remains required before production deployment.

## Findings From Audit

`backend/migrations/002_align_architecture_stack.sql` previously used destructive `DROP TABLE` operations against `contents`, `vector_store`, `documents`, and `users` after creating backups. That was unsafe for production because failed or partial backfill could still result in table loss.

## Remediation

The migration was rewritten as a non-destructive legacy alignment migration:

- Creates the pgvector extension with `CREATE EXTENSION IF NOT EXISTS vector`.
- Renames incompatible legacy tables to timestamped backup tables instead of dropping them.
- Aborts if a target backup table already exists.
- Creates the required architecture tables with `CREATE TABLE IF NOT EXISTS`.
- Creates pgvector and ownership indexes with `CREATE INDEX IF NOT EXISTS`.
- Enables RLS for the required tables.
- Creates RLS policies only when they do not already exist.

## Destructive Pattern Check

The hardening migration test scans all SQL migration files and rejects:

- `DROP TABLE`
- `DROP SCHEMA`
- `DROP DATABASE`

Current result: no destructive patterns found.

## Data Preservation

Legacy data is preserved in backup tables when incompatible table shapes are detected:

- `legacy_contents_backup_20260526`
- `legacy_vector_store_backup_20260526`
- `legacy_documents_backup_20260526`
- `legacy_users_backup_20260526`

No automatic data backfill is performed in this hardening sprint. That is intentional: automatic backfill would require field-level mapping decisions outside the bootability/security scope.

## Remaining Production Work

- Run migrations against a Supabase/PostgreSQL staging database.
- Verify backups and new aligned tables after migration.
- Create a controlled backfill plan if legacy production data must be retained in active tables.
- Confirm `auth.users` foreign key behavior in the target Supabase project.
