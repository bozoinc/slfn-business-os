# Issue 005: Document Intake Pipeline with PDF Processing

## Description
Build a document intake pipeline that uses `pdf-inspector` to extract structured data from uploaded PDFs (business plans, financial statements, contracts) and stores extracted content for the guidance engine.

## Acceptance Criteria
- [ ] `POST /api/v1/documents/upload` - Accept PDF upload, return document ID
- [ ] `GET /api/v1/documents/{doc_id}/extracted` - Return extracted text/structure
- [ ] `GET /api/v1/documents` - List uploaded documents
- [ ] Background processing with Redis queue (pdf-inspector extraction)
- [ ] Store extracted content in `documents` table (id, filename, extracted_text, metadata, created_at)
- [ ] Integration with guidance engine (attach documents to phases/checklists)

## Dependencies
- Issue 001, 002, 004 (infrastructure + guidance engine)

## Technical Notes
- pdf-inspector v0.2.6 available at `~/venvs/pdf`
- Use Redis (port 6380) for task queue
- Consider MinIO (port 9002) for file storage
- Add alembic migration for `documents` table

## Status
- [x] Todo
- [x] In Progress
- [x] Done