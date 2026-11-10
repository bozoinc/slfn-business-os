# Issue 002: CORS Configuration for Frontend-Backend Communication

## Description
Configure CORS on the backend to allow requests from the frontend at `http://localhost:3002`. Currently, OPTIONS preflight requests from the frontend are rejected.

## Acceptance Criteria
- [ ] OPTIONS request from `http://localhost:3002` to `/api/v1/auth/login` returns 200 OK
- [ ] POST login request from `http://localhost:3002` succeeds with valid credentials
- [ ] `GET /api/v1/auth/me` with Bearer token works from frontend origin
- [ ] No "Disallowed CORS origin" errors in backend logs

## Dependencies
- Issue 001 (PostgreSQL auth must work first)

## Technical Notes
- Backend `config.py` has `ALLOWED_ORIGINS` list that must include `http://localhost:3002`
- Environment variable override not working - config file must be updated directly
- Restart backend container after config change

## Status
- [ ] Todo
- [ ] In Progress
- [x] Done