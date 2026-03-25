# Data Model

## Entity Relationship

```
people ──< call_sessions >── campaigns ── hazard_events
  │              │
  │         call_turns
  │              │
  │      extracted_assessments
  │              │
  │          followups
  │              │
  └──< map_features

rag_documents ──< rag_chunks (with vector embeddings)

audit_logs (standalone)
```

## Table Descriptions

### people
Household members imported from the spreadsheet. Contains location, housing type, livelihood, vulnerability info.

### hazard_events
Disaster alert events with type, severity, signal, lead time, and geographic scope.

### campaigns
Batches of outbound calls linked to a hazard event. Tracks target count and completion.

### call_sessions
Individual call records with status, conversation stage, urgency, full transcript, and extraction JSON.

### call_turns
Individual conversation turns (agent/user) with Bengali text and optional audio URLs.

### extracted_assessments
Structured data extracted from completed calls: housing, WASH risk, vulnerability, priority, damage estimates.

### followups
Post-call actions: human callback, volunteer referral, shelter info, medical support.

### map_features
GeoJSON-ready features with denormalized data for fast map rendering and 8 thematic layer flags.

### rag_documents / rag_chunks
Ingested guideline documents chunked with metadata (hazard type, phase, priority) and vector embeddings.

### audit_logs
System action tracking for auditability.
