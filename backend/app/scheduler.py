from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple, Optional

from sqlmodel import Session, select

from .models import Employee, Unavailability, ShiftRequirement, ShiftAssignment


@dataclass
class Candidate:
    employee: Employee
    assigned_minutes: int


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def minutes_between(start: datetime, end: datetime) -> int:
    return int((end - start).total_seconds() // 60)


def generate_schedule(
    session: Session,
    week_start: date,
    min_rest_hours: int = 10,
) -> Dict:
    employees = session.exec(select(Employee)).all()

    reqs = session.exec(
        select(ShiftRequirement)
        .where(ShiftRequirement.week_start == week_start)
        .order_by(ShiftRequirement.start_dt)
    ).all()

    unavs = session.exec(select(Unavailability)).all()

    # Clear previous schedule for this week
    prev = session.exec(
        select(ShiftAssignment).where(ShiftAssignment.week_start == week_start)
    ).all()
    for a in prev:
        session.delete(a)
    session.commit()

    # Unavailability grouped by employee
    unav_by_emp: Dict[int, List[Tuple[datetime, datetime]]] = {}
    for u in unavs:
        unav_by_emp.setdefault(u.employee_id, []).append((u.start_dt, u.end_dt))

    assigned_minutes: Dict[int, int] = {e.id: 0 for e in employees if e.id is not None}
    last_shift_end: Dict[int, datetime] = {}

    out: List[Dict] = []

    for req in reqs:
        shift_len = minutes_between(req.start_dt, req.end_dt)
        role_candidates = [e for e in employees if e.role == req.role]

        for _slot in range(req.required_count):
            viable: List[Candidate] = []

            for e in role_candidates:
                if e.id is None:
                    continue

                # Max hours per week
                if assigned_minutes[e.id] + shift_len > e.max_hours_per_week * 60:
                    continue

                # Unavailability overlap
                blocked = False
                for (s, t) in unav_by_emp.get(e.id, []):
                    if overlaps(req.start_dt, req.end_dt, s, t):
                        blocked = True
                        break
                if blocked:
                    continue

                # Minimum rest between shifts
                if e.id in last_shift_end:
                    if req.start_dt < last_shift_end[e.id] + timedelta(hours=min_rest_hours):
                        continue

                viable.append(Candidate(employee=e, assigned_minutes=assigned_minutes[e.id]))

            if not viable:
                out.append({"requirement_id": req.id, "status": "unfilled"})
                continue

            # Choose least-loaded employee (simple fairness)
            viable.sort(key=lambda c: (c.assigned_minutes, c.employee.id))
            chosen = viable[0].employee

            assignment = ShiftAssignment(
                week_start=week_start,
                requirement_id=req.id,
                employee_id=chosen.id,
            )
            session.add(assignment)
            session.commit()

            assigned_minutes[chosen.id] += shift_len
            last_shift_end[chosen.id] = req.end_dt

            out.append(
                {
                    "requirement_id": req.id,
                    "employee_id": chosen.id,
                    "employee_name": chosen.full_name,
                    "status": "assigned",
                }
            )

    return {"week_start": str(week_start), "assignments": out}
