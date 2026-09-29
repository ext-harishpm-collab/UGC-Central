# Phase 20 - Reference master routes

Reference imports are now mounted in the FastAPI application:
- POST /api/reference/contract/import
- POST /api/reference/pan/import
- POST /api/reference/compliance/import
- GET /api/reference/author/{author_id}

Rows retain source file, source sheet and source row. Missing/ambiguous values are reviewable and are not silently inferred.
