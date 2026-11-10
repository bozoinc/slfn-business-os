# Issue 006: Authentik SSO Integration

## Description
Integrate authentik (cloned at `~/projects/authentik`) as the OIDC identity provider for the Business OS. This replaces the current custom auth with enterprise-grade SSO, MFA, and user management.

## Acceptance Criteria
- [ ] authentik deployed and accessible (new Docker Compose service)
- [ ] OIDC client configured in authentik for Business OS
- [ ] Backend validates JWT tokens from authentik
- [ ] Frontend redirects to authentik for login
- [ ] User provisioning syncs to Business OS `contacts` table
- [ ] MFA enforced for admin users

## Dependencies
- Issue 001, 002 (PostgreSQL + CORS must work)
- authentik deployment (separate compose project)

## Technical Notes
- authentik requires PostgreSQL + Redis (can share existing or use dedicated)
- GPL license: self-host only, never embed in paid product
- Backend: replace custom JWT with authentik token validation
- Frontend: OIDC redirect flow

## Status
- [x] Todo
- [x] In Progress
- [x] Done