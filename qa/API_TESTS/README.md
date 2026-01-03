# API Testing – Restaurant Staff Scheduler (MVP)

This folder contains API testing assets (Postman collection, environments, notes).

## 1. Base URL
- Local: `http://127.0.0.1:8000`

## 2. Recommended tool
- Postman (collections + environments + basic tests)

## 3. Endpoints to cover (minimum)
### Employees
- `POST /employees`
- `GET /employees`

### Unavailability
- `POST /unavailability`
- `GET /unavailability`
- `GET /unavailability?employee_id={id}`

### Requirements
- `POST /requirements`
- `GET /requirements?week_start=YYYY-MM-DD`

### Schedule
- `POST /schedule/generate?week_start=YYYY-MM-DD`
- `GET /schedule?week_start=YYYY-MM-DD`

## 4. Suggested Postman tests (Assertions)
Add these in the “Tests” tab for each request:

### A) Status code checks
- Create endpoints should return **200/201**
- Invalid payloads should return **422**
- Non-existing employee_id should return **404** (if validated)

### B) Response shape checks (examples)
For create employee:
- response has `id`
- response `full_name` equals input

For generate schedule:
- response has `week_start`
- response has `assignments` array

## 5. Minimal collection checklist
Create a Postman collection named:
**Restaurant Scheduler – API Tests**

Include requests:
1. Create employee (valid)
2. Create employee (invalid max_hours_per_week=0)
3. Create unavailability (valid)
4. Create unavailability (invalid end before start)
5. Create requirement (valid)
6. Create requirement (invalid required_count=0)
7. Generate schedule (week_start)
8. Get schedule (week_start)

## 6. Test data notes
Use a consistent week_start for tests, e.g.:
- `2026-01-05` (Monday)

Example roles:
- `waiter`, `bar`, `kitchen` (or `staff`)
