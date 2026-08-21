# Issue 007: Architecture Documentation with archify-mapper

## Description
Use the archify-mapper skill (already installed) to generate interactive architecture diagrams for the Business OS system. Document current state and planned integrations.

## Acceptance Criteria
- [ ] Architecture diagram: Current system (frontend, backend, DB, Redis, MinIO)
- [ ] Architecture diagram: Target state (add authentik, airllm, pdf-inspector, Aether)
- [ ] Diagram: Data flow for guidance engine + document intake
- [ ] Diagram: Auth flow with authentik OIDC
- [ ] Export as SVG/HTML for vault embedding
- [ ] Add to vault at `Projects/SLFN Business OS/architecture/`

## Dependencies
- Issue 001-006 (system components defined)

## Technical Notes
- archify-mapper skill available with `references/areas.md`
- Use interactive validated diagrams
- Update as system evolves

## Status
- [x] Todo
- [x] In Progress
- [x] Done