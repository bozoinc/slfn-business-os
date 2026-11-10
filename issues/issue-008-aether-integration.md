# Issue 008: Aether Integration for Local AI Inference

## Description
Integrate Aether (hybrid local inference system at `~/projects/aether`) as the AI backend for the Business OS guidance engine. Aether provides intelligent model routing, caching, and pipeline folding.

## Acceptance Criteria
- [ ] Aether dashboard accessible (port 8502)
- [ ] Business OS backend calls Aether orchestrator for AI tasks
- [ ] Model routing: guidance generation → appropriate local model
- [ ] Caching reduces redundant inference calls
- [ ] Fallback to Nexus AI agents if Aether unavailable
- [ ] Documented integration in `docs/aether-integration.md`

## Dependencies
- Issue 004 (guidance engine exists to consume AI)
- Aether running (independent project)

## Technical Notes
- Aether stack: Dashboard(8502) → Orchestrator → Llama-Server(8000) → Models
- Redis cache at 6379 (shared or dedicated)
- API contract: POST `/orchestrate` with task type and context

## Status
- [ ] Todo
- [ ] In Progress
- [ ] Done