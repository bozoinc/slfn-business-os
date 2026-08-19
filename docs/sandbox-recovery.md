# Sandbox Deployment Recovery Model

## Overview
This document describes the sandbox deployment recovery model for SLFN Business OS development. All development happens in isolated sandboxes (feature branches) with automatic rollback capability on failure.

## Git Workflow

### Branch Naming Convention
- Feature branches: `feature/<issue-id>-<short-description>`
- Fix branches: `fix/<issue-id>-<short-description>`
- Refactor branches: `refactor/<description>`
- Test branches: `test/<description>`

Examples:
- `feature/004-guidance-engine-phases`
- `fix/002-cors-origin-validation`
- `refactor/auth-service-extraction`

### Commit Convention
Follow Conventional Commits specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `test`: Adding/updating tests
- `docs`: Documentation changes
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

Examples:
```
feat(guidance): add phase model and checklists API
fix(cors): allow localhost:3002 origin in allowed list
refactor(auth): extract password hashing to service
test(guidance): add unit tests for phase progression
docs: add sandbox recovery model documentation
chore(deps): update bcrypt to 4.0.1
```

### Pre-Destructive Operation Protocol
Before ANY destructive operation (rebase, force push, merge with conflicts, large refactor):

```bash
git tag rollback-pre-$(date +%Y%m%d-%H%M) HEAD
```

This creates a timestamped rollback point. List tags with `git tag -l`.

### Rollback Procedure
If something goes wrong:

```bash
# List available rollback points
git tag -l "rollback-pre-*"

# Reset to specific rollback point (HARD - destroys uncommitted work)
git reset --hard rollback-pre-20260819-143022

# Or soft reset (keeps changes uncommitted)
git reset --soft rollback-pre-20260819-143022

# Delete rollback tag after successful operation
git tag -d rollback-pre-20260819-143022
```

## Feature Branch Lifecycle

### 1. Create Branch
```bash
git checkout main
git pull origin main
git checkout -b feature/004-guidance-engine-phases
```

### 2. Develop
- Make small, focused commits
- Push regularly: `git push -u origin feature/004-guidance-engine-phases`
- Run tests before each push

### 3. Pre-Merge Checklist
- [ ] All tests pass
- [ ] Code review approved (Hermes code reviewer)
- [ ] No merge conflicts with main
- [ ] Rollback tag created: `git tag rollback-pre-$(date +%Y%m%d-%H%M) HEAD`

### 4. Merge
```bash
git checkout main
git pull origin main
git merge --no-ff feature/004-guidance-engine-phases
git push origin main
```

### 5. Cleanup
```bash
git branch -d feature/004-guidance-engine-phases
git push origin --delete feature/004-guidance-engine-phases
# Delete rollback tag after confirming merge success
git tag -d rollback-pre-20260819-143022
```

## Automated Rollback Script

See `scripts/rollback.sh` for the automated rollback utility.

## Integration with Hermes Agent

When Hermes implements an issue:
1. Creates feature branch
2. Implements changes with conventional commits
3. Runs tests
4. Requests code review
5. On approval: creates rollback tag, merges to main
6. Cleans up branch and rollback tag

## Emergency Procedures

### Database Migration Rollback
If alembic migration fails:
```bash
# Inside backend container
alembic downgrade -1
```

### Docker Container Recovery
```bash
# Restart all services
docker-compose restart

# Full rebuild if needed
docker-compose down -v
docker-compose up -d --build
```

### Complete Environment Reset
```bash
# Nuclear option - destroys all data
docker system prune -af --volumes
git reset --hard rollback-pre-<timestamp>
docker-compose up -d --build
```

## Verification Checklist

Before marking any issue "Done":
- [ ] Feature branch created with correct naming
- [ ] Conventional commits used throughout
- [ ] Pre-merge rollback tag created
- [ ] All tests pass (backend + frontend)
- [ ] Code review completed
- [ ] Merged to main via --no-ff
- [ ] Branch and rollback tag cleaned up
- [ ] Deployment verified (services healthy)