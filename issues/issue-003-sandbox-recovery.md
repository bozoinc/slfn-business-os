# Issue 003: Sandbox Deployment Recovery Model

## Description
Implement the sandbox deployment recovery model as specified in ADR-001. All development must happen in isolated sandboxes with automatic rollback capability on failure.

## Acceptance Criteria
- [ ] Git workflow with `git tag rollback-pre-$(date +%Y%m%d-%H%M) HEAD` before destructive operations
- [ ] Feature branches for each issue (short-lived, trunk-based)
- [ ] Automated rollback script that reverts to tagged state
- [ ] Documentation in `docs/sandbox-recovery.md`

## Dependencies
- Issue 001, 002 (infrastructure stable)

## Technical Notes
- Trunk-based development: short-lived branches, always-mergeable main
- Conventional commits: feat:, fix:, refactor:, test:, docs:, chore:
- Pre-destructive tag: `git tag rollback-pre-$(date +%Y%m%d-%H%M) HEAD`

## Status
- [ ] Todo
- [x] In Progress
- [x] Done