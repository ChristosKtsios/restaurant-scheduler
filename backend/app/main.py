from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .db import init_db, get_session
from .models import (
    Employee,
    EmployeeCreate,
    Unavailability,
    UnavailabilityCreate,
    ShiftRequirement,
    ShiftRequirementCreate,
    ShiftAssignment,
    GenerateScheduleResponse,
)
from .scheduler import generate_schedule

app = FastAPI(title="Restaurant Staff Scheduler")

# Για το frontend αργότερα (Vite default port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


# -----------------------
# Helpers / Validations
# -----------------------
def ensure_start_before_end(start, end, what: str):
    if end <= start:
        raise HTTPException(status_code=422, detail=f"{what}: end_dt must be after start_dt")


def get_employee_or_404(session: Session, employee_id: int) -> Employee:
    emp = session.get(Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


# -----------------------
# Employees
# -----------------------
@app.post("/employees", response_model=Employee)
def create_employee(payload: EmployeeCreate, session: Session = Depends(get_session)):
    if payload.max_hours_per_week <= 0:
        raise HTTPException(status_code=422, detail="max_hours_per_week must be > 0")

    emp = Employee(**payload.model_dump())
    session.add(emp)
    session.commit()
    session.refresh(emp)
    return emp


@app.get("/employees", response_model=List[Employee])
def list_employees(session: Session = Depends(get_session)):
    return session.exec(select(Employee).order_by(Employee.id)).all()


# -----------------------
# Unavailability
# -----------------------
@app.post("/unavailability", response_model=Unavailability)
def add_unavailability(payload: UnavailabilityCreate, session: Session = Depends(get_session)):
    get_employee_or_404(session, payload.employee_id)
    ensure_start_before_end(payload.start_dt, payload.end_dt, "Unavailability")

    u = Unavailability(**payload.model_dump())
    session.add(u)
    session.commit()
    session.refresh(u)
    return u


@app.get("/unavailability", response_model=List[Unavailability])
def list_unavailability(
    employee_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    q = select(Unavailability)
    if employee_id is not None:
        q = q.where(Unavailability.employee_id == employee_id)
    return session.exec(q.order_by(Unavailability.start_dt)).all()


# -----------------------
# Shift requirements
# -----------------------
@app.post("/requirements", response_model=ShiftRequirement)
def add_requirement(payload: ShiftRequirementCreate, session: Session = Depends(get_session)):
    ensure_start_before_end(payload.start_dt, payload.end_dt, "Requirement")
    if payload.required_count <= 0:
        raise HTTPException(status_code=422, detail="required_count must be >= 1")

    r = ShiftRequirement(**payload.model_dump())
    session.add(r)
    session.commit()
    session.refresh(r)
    return r


@app.get("/requirements", response_model=List[ShiftRequirement])
def list_requirements(week_start: date, session: Session = Depends(get_session)):
    return session.exec(
        select(ShiftRequirement)
        .where(ShiftRequirement.week_start == week_start)
        .order_by(ShiftRequirement.start_dt)
    ).all()


# -----------------------
# Schedule
# -----------------------
@app.post("/schedule/generate", response_model=GenerateScheduleResponse)
def generate(week_start: date, session: Session = Depends(get_session)):
    # Αν δεν υπάρχουν requirements, δώσε καθαρό μήνυμα
    req_count = session.exec(
        select(ShiftRequirement).where(ShiftRequirement.week_start == week_start)
    ).all()
    if not req_count:
        return {"week_start": str(week_start), "assignments": []}

    return generate_schedule(session, week_start=week_start)


@app.get("/schedule", response_model=List[ShiftAssignment])
def get_schedule(week_start: date, session: Session = Depends(get_session)):
    return session.exec(
        select(ShiftAssignment)
        .where(ShiftAssignment.week_start == week_start)
        .order_by(ShiftAssignment.id)
    ).all()
