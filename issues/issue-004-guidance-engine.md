# Issue 004: Business OS Core Guidance Engine

## Description
Build the core guidance engine that provides structured checklists, progression paths, and actionable guidance for scaling from solo entrepreneur to Fortune 500 company. This is the heart of the Business OS.

## Acceptance Criteria
- [ ] RESTful API endpoints for guidance content:
  - `GET /api/v1/guidance/phases` - List all business growth phases
  - `GET /api/v1/guidance/phases/{phase_id}` - Get phase details with checklists
  - `GET /api/v1/guidance/checklists` - Get all checklists
  - `POST /api/v1/guidance/progress` - Record user progress
  - `GET /api/v1/guidance/progress` - Get user's progress
- [ ] Phase model: Foundation → Growth → Scale → Enterprise → Fortune 500
- [ ] Each phase has: objectives, checklists, milestones, resources
- [ ] Data persisted in PostgreSQL (new tables: `phases`, `checklists`, `milestones`, `user_progress`)
- [ ] Pydantic schemas for all request/response models

## Dependencies
- Issue 001, 002, 003 (infrastructure)

## Technical Notes
- Use airllm for generating contextual guidance content
- Follow existing patterns in `app/api/routes/` and `app/db/models/`
- Add alembic migration for new tables

## Status
- [x] Todo
- [x] In Progress
- [x] Done