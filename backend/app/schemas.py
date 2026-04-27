import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# Auth
class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SignupRequest(BaseModel):
    email: str
    password: str
    organization_name: str


# Organization
class OrganizationCreate(BaseModel):
    name: str


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Location
class LocationCreate(BaseModel):
    name: str
    address: Optional[str] = None
    manager_name: Optional[str] = None


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    manager_name: Optional[str] = None
    status: Optional[str] = None


class LocationResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    address: Optional[str]
    manager_name: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# WorkOrder
class WorkOrderCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "normal"


class WorkOrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class WorkOrderResponse(BaseModel):
    id: uuid.UUID
    location_id: uuid.UUID
    title: str
    description: Optional[str]
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Task
class TaskCreate(BaseModel):
    title: str
    assigned_to: Optional[uuid.UUID] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    assigned_to: Optional[uuid.UUID] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None


class TaskResponse(BaseModel):
    id: uuid.UUID
    location_id: uuid.UUID
    assigned_to: Optional[uuid.UUID]
    title: str
    due_date: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Financial
class FinancialRecordCreate(BaseModel):
    date: datetime
    revenue: Optional[float] = 0
    expenses: Optional[float] = 0
    notes: Optional[str] = None


class FinancialRecordResponse(BaseModel):
    id: uuid.UUID
    location_id: uuid.UUID
    date: datetime
    revenue: float
    expenses: float
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Audit
class AuditLogResponse(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    user_id: Optional[uuid.UUID]
    organization_id: uuid.UUID
    action: str
    entity_type: str
    entity_id: Optional[uuid.UUID]
    payload_json: dict
    prev_hash: Optional[str]
    hash: str

    class Config:
        from_attributes = True


# Dashboard
class DashboardSummary(BaseModel):
    total_locations: int
    active_issues: int
    compliance_score_avg: float
    monthly_revenue: float
    monthly_expenses: float
    flagged_locations: List[LocationResponse]


# Health
class HealthResponse(BaseModel):
    status: str
