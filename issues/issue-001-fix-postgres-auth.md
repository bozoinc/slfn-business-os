# Issue 001: Fix PostgreSQL Authentication Failure

## Description
Resolve the PostgreSQL password authentication failure that blocks the backend API. The database is accessible at `localhost:5433` with user `slfn` and password `slfn-pass`, but the backend container cannot connect.

## Acceptance Criteria
- [ ] Backend container connects to PostgreSQL successfully
- [ ] Alembic migrations run without error
- [ ] Application can query the database (verified via `/docs` endpoint)
- [ ] No "Internal Server Error" on auth endpoints

## Dependencies
- None (blocker for all other work)

## Technical Notes
- Current `.env` has `DATABASE_URL=postgresql://slfn:***@db:5432/slfn_business_os` (Docker internal)
- Host machine uses `localhost:5433` (mapped port)
- Container networking needs to use `db:5432` (service name)
- Verify `alembic.ini` has correct `script_location = .` and `sqlalchemy.url`

## Status
- [ ] Todo
- [ ] In Progress
- [x] Done