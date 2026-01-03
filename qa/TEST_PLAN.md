# Test Plan – Restaurant Staff Scheduler (MVP)

## 1. Objective
Verify that the Restaurant Staff Scheduler MVP correctly:
- Stores employees, unavailability, and shift requirements
- Generates a weekly schedule that respects constraints (unavailability, max weekly hours, minimum rest)

## 2. Scope
### In scope
- Employees: create/list
- Unavailability: create/list
- Shift requirements: create/list (per week_start)
- Schedule generation: generate/list assignments
- API validations and error handling

### Out of scope (for MVP)
- Authentication/authorization
- UI/Frontend testing
- Notifications, exporting (PDF/CSV)
- Advanced optimization (perfect fairness, preferences, seniority rules)

## 3. Test Types
- Smoke testing (critical paths)
- Regression testing (core flows after changes)
- API testing (status codes, payload validation, edge cases)

## 4. Test Environment
- OS: Windows
- Backend: FastAPI + Uvicorn
- DB: SQLite
- Tools: Swagger (/docs), Postman (optional)

## 5. Entry / Exit Criteria
### Entry
- API server runs locally and /docs is reachable
- Database tables are created on startup

### Exit
- All smoke tests pass
- No Critical/High severity defects open for MVP features
- Core schedule constraints verified via API responses

## 6. Risks
- Missing validations (e.g., end_dt <= start_dt)
- Incorrect overlap logic for unavailability
- Scheduling fairness not guaranteed (simple heuristic)
- No database constraints for employee_id references (handled at API level)

## 7. Severity Definitions
- Critical: crashes, cannot generate schedule, data corruption
- High: schedule violates constraints (assigns unavailable staff, exceeds max hours)
- Medium: incorrect validation/messages, minor logic issues
- Low: formatting, non-blocking improvements

## 8. Test Data (Example)
- Roles: waiter, bar, kitchen (or “staff”)
- 2–5 employees per role
- 10–20 requirements per week
- Multiple unavailability intervals per employee

## 9. Deliverables
- TEST_CASES.csv
- BUG_REPORTS.md
- (Optional) Postman collection under qa/API_TESTS
