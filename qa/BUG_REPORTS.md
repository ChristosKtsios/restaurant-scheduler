# Bug Reports – Restaurant Staff Scheduler (MVP)

## Severity guide
- **Critical**: server crash, cannot generate schedule, data corruption
- **High**: schedule violates constraints (assigns unavailable staff / exceeds max hours)
- **Medium**: incorrect validation/messages, wrong ordering, non-blocking logic issue
- **Low**: UI/text/formatting improvements (not applicable much for API-only MVP)

---

## Bug Report Template

**ID:** BR-XXX  
**Title:** (Short and clear)  
**Environment:** Windows, FastAPI local, SQLite, Swagger (/docs)  
**Endpoint/Area:** (e.g., POST /unavailability)  
**Severity / Priority:** (e.g., High / P1)

**Steps to Reproduce:**
1. ...
2. ...
3. ...

**Expected Result:**
- ...

**Actual Result:**
- ...

**Evidence:**
- Response body / status code / screenshot link

**Notes:**
- Any extra context

---

## BR-001 – Unavailability accepts invalid date range (end before start)

**ID:** BR-001  
**Title:** POST /unavailability allows end_dt earlier than start_dt  
**Environment:** Windows, FastAPI local, SQLite, Swagger (/docs)  
**Endpoint/Area:** POST `/unavailability`  
**Severity / Priority:** Medium / P2

**Steps to Reproduce:**
1. Create an employee via POST `/employees`.
2. Send POST `/unavailability` with:
   - `start_dt = 2026-01-06T14:00:00`
   - `end_dt   = 2026-01-06T08:00:00`
3. Execute the request.

**Expected Result:**
- API rejects the request with **422** (validation error), because `end_dt` must be after `start_dt`.

**Actual Result:**
- API accepts the request (201/200) and stores invalid unavailability.

**Evidence:**
- Status code + response JSON from Swagger.

**Notes:**
- Invalid time ranges can break scheduling logic and reporting.

---

## BR-002 – Requirement accepts invalid required_count (0 or negative)

**ID:** BR-002  
**Title:** POST /requirements allows required_count <= 0  
**Environment:** Windows, FastAPI local, SQLite, Swagger (/docs)  
**Endpoint/Area:** POST `/requirements`  
**Severity / Priority:** Medium / P2

**Steps to Reproduce:**
1. Send POST `/requirements` with a valid week_start/start_dt/end_dt but set `required_count = 0`.
2. Execute the request.

**Expected Result:**
- API rejects the request with **422** and a clear message that `required_count` must be >= 1.

**Actual Result:**
- API accepts the request and stores a requirement with `required_count = 0`.

**Evidence:**
- Status code + response JSON from Swagger.

**Notes:**
- This creates confusing behavior during schedule generation (shift exists but no slots to fill).
