# SLFN Business OS — Issue Backlog (Ordered by Dependency)

## Dependency Graph
```
001 ──┬── 002 ──┬── 003 ──┬── 004 ──┬── 005
      │         │         │         ├── 008
      │         │         ├── 006
      │         └── 007
      └── (blocker for all)
```

## Issue List

| ID | Title | Priority | Est. Sessions | Status |
|----|-------|----------|---------------|--------|
| 001 | Fix PostgreSQL Authentication Failure | BLOCKER | 1 | ✅ DONE |
| 002 | CORS Configuration for Frontend-Backend | BLOCKER | 1 | ✅ DONE |
| 003 | Sandbox Deployment Recovery Model | HIGH | 1 | ✅ DONE |
| 004 | Business OS Core Guidance Engine | HIGH | 3-4 | 📋 TODO |
| 005 | Document Intake Pipeline with PDF Processing | MEDIUM | 2-3 | 📋 TODO |
| 006 | Authentik SSO Integration | HIGH | 3-4 | 📋 TODO |
| 007 | Architecture Documentation with archify-mapper | MEDIUM | 1-2 | 📋 TODO |
| 008 | Aether Integration for Local AI Inference | MEDIUM | 2-3 | 📋 TODO |

## Next Action
Run `/implement issue-003-sandbox-recovery.md` to establish the development workflow foundation.

## Notes
- Issues 001 & 002 are complete (verified working)
- Issue 003 establishes the workflow for all subsequent work
- Issues 004-008 can be parallelized after 003 (different developers)
- Issue 006 (authentik) requires separate deployment
- Issues 007 & 008 depend on 004 but can start documentation/design early