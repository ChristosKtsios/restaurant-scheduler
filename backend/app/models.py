from typing import Optional, List
from datetime import datetime, date
from sqlmodel import SQLModel, Field


# -----------------------
# DB Tables
# -----------------------
class Employee(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    role: str = "staff"              # waiter / bar / kitchen
    max_hours_per_week: int = 40     # hours


class Unavailability(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(index=True)
    start_dt: datetime
    end_dt: datetime


class ShiftRequirement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    week_start: date = Field(index=True)  # typically Monday
    role: str = "staff"
    start_dt: datetime
    end_dt: datetime
    required_count: int = 1


class ShiftAssignment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    week_start: date = Field(index=True)
    requirement_id: int = Field(index=True)
    employee_id: int = Field(index=True)


# -----------------------
# API Schemas (Request/Response)
# (για να μην στέλνει ο client id)
# -----------------------
class EmployeeCreate(SQLModel):
    full_name: str
    role: str = "staff"
    max_hours_per_week: int = 40


class UnavailabilityCreate(SQLModel):
    employee_id: int
    start_dt: datetime
    end_dt: datetime


class ShiftRequirementCreate(SQLModel):
    week_start: date
    role: str = "staff"
    start_dt: datetime
    end_dt: datetime
    required_count: int = 1


class AssignmentRead(SQLModel):
    requirement_id: int
    employee_id: Optional[int] = None
    employee_name: Optional[str] = None
    status: str  # "assigned" | "unfilled"


class GenerateScheduleResponse(SQLModel):
    week_start: str
    assignments: List[AssignmentRead]
