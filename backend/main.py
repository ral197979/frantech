import uuid
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db, init_db
from app.models import (
    User, Organization, Location, WorkOrder, Task,
    FinancialRecord, AuditLog
)
from app.schemas import (
    LoginRequest, LoginResponse, SignupRequest,
    LocationCreate, LocationUpdate, LocationResponse,
    WorkOrderCreate, WorkOrderUpdate, WorkOrderResponse,
    TaskCreate, TaskUpdate, TaskResponse,
    FinancialRecordCreate, FinancialRecordResponse,
    AuditLogResponse, DashboardSummary, HealthResponse,
)
from app.auth import (
    create_access_token, verify_password, hash_password,
    get_user_context, UserContext
)
from app.services.audit import (
    audit_log, get_audit_logs, verify_audit_chain
)

app = FastAPI(title="Frantech", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup
@app.on_event("startup")
def startup():
    init_db()


# Health Check
@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok")


# Auth Endpoints
@app.post("/auth/signup", response_model=LoginResponse)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    """Create organization + user."""
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    org = Organization(
        id=uuid.uuid4(),
        name=req.organization_name,
        owner_id=uuid.uuid4(),
    )
    db.add(org)
    db.commit()

    user = User(
        id=uuid.uuid4(),
        email=req.email,
        hashed_password=hash_password(req.password),
        organization_id=org.id,
    )
    db.add(user)
    db.commit()

    token = create_access_token(user.id, org.id)
    return LoginResponse(access_token=token)


@app.post("/auth/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Login and get JWT token."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id, user.organization_id)
    return LoginResponse(access_token=token)


# Location Endpoints
@app.get("/locations", response_model=list[LocationResponse])
def list_locations(
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_user_context),
):
    """List all locations for organization."""
    locations = db.query(Location).filter(
        Location.organization_id == user.organization_id
    ).all()
    return locations


@app.post("/locations", response_model=LocationResponse)
def create_location(
    req: LocationCreate,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_user_context),
):
    """Create location."""
    location = Location(
        id=uuid.uuid4(),
        organization_id=user.organization_id,
        name=req.name,
        address=req.address,
        manager_name=req.manager_name,
    )
    db.add(location)
    db.commit()

    audit_log(
        db=db,
        organization_id=user.organization_id,
        action="create",
        entity_type="location",
        entity_id=location.id,
        user_id=user.user_id,
        payload=location.__dict__,
    )

    db.refresh(location)
    return location


@app.get("/locations/{location_id}", response_model=LocationResponse)
def get_location(
    location_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_user_context),
):
    """Get location by ID."""
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.organization_id == user.organization_id,
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@app.patch("/locations/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: uuid.UUID,
    req: LocationUpdate,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_user_context),
):
    """Update location."""
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.organization_id == user.organization_id,
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    update_data = req.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(location, key, value)

    db.commit()

    audit_log(
        db=db,
        organization_id=user.organization_id,
        action="update",
        entity_type="location",
        entity_id=location.id,
        user_id=user.user_id,
        payload=update_data,
    )

    db.refresh(location)
    return location


# Work Order Endpoints
@app.get("/work-orders", response_model=list[WorkOrderResponse])
def list_work_orders(
    location_id: uuid.UUID = None,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_user_context),
):
    """List work orders."""
    query = db.query(WorkOrder).join(Location).filter(
        Location.organization_id == user.organization_id
    )
    if location_id:
        query = query.filter(WorkOrder.location_id == location_id)
    return query.all()


@app.post("/work-orders", response_model=WorkOrderResponse)
def create_work_order(
    location_id: uuid.UUID,
    req: WorkOrderCreate,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_user_context),
):
    """Create work order."""
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.organization_id == user.organization_id,
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    wo = WorkOrder(
        id=uuid.uuid4(),
        location_id=location_id,
        title=req.title,
        description=req.description,
        priority=req.priority,
    )
    db.add(wo)
    db.commit()

    audit_log(
        db=db,
        organization_id=user.organization_id,
        action="create",
        entity_type="work_order",
        entity_id=wo.id,
        user_id=user.user_id,
        payload=wo.__dict__,
    )

    db.refresh(wo)
    return wo


# Task Endpoints
@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(
    location_id: uuid.UUID = None,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_user_context),
):
    """List tasks."""
    query = db.query(Task).join(Location).filter(
        Location.organization_id == user.organization_id
    )
    if location_id:
        query = query.filter(Task.location_id == location_id)
    return query.all()


@app.post("/tasks", response_model=TaskResponse)
def create_task(
    location_id: uuid.UUID,
    req: TaskCreate,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_user_context),
):
    """Create task."""
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.organization_id == user.organization_id,
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    task = Task(
        id=uuid.uuid4(),
        location_id=location_id,
        title=req.title,
        assigned_to=req.assigned_to,
        due_date=req.due_date,
    )
    db.add(task)
    db.commit()

    audit_log(
        db=db,
        organization_id=user.organization_id,
        action="create",
        entity_type="task",
        entity_id=task.id,
        user_id=user.user_id,
        payload=task.__dict__,
    )

    db.refresh(task)
    return task


# Financial Endpoints
@app.get("/financials/{location_id}", response_model=list[FinancialRecordResponse])
def get_location_financials(
    location_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_user_context),
):
    """Get financials for location."""
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.organization_id == user.organization_id,
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    records = db.query(FinancialRecord).filter(
        FinancialRecord.location_id == location_id
    ).order_by(FinancialRecord.date.desc()).all()
    return records


@app.post("/financials/{location_id}", response_model=FinancialRecordResponse)
def create_financial_record(
    location_id: uuid.UUID,
    req: FinancialRecordCreate,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_user_context),
):
    """Create financial record."""
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.organization_id == user.organization_id,
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    record = FinancialRecord(
        id=uuid.uuid4(),
        location_id=location_id,
        date=req.date,
        revenue=req.revenue,
        expenses=req.expenses,
        notes=req.notes,
    )
    db.add(record)
    db.commit()

    audit_log(
        db=db,
        organization_id=user.organization_id,
        action="create",
        entity_type="financial_record",
        entity_id=record.id,
        user_id=user.user_id,
        payload=record.__dict__,
    )

    db.refresh(record)
    return record


# Audit Endpoints
@app.get("/audit-logs", response_model=list[AuditLogResponse])
def list_audit_logs(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_user_context),
):
    """Get audit logs for organization."""
    logs = get_audit_logs(db, user.organization_id, limit, offset)
    return logs


@app.get("/audit-logs/verify")
def verify_audit(
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_user_context),
):
    """Verify audit chain integrity."""
    is_valid = verify_audit_chain(db, user.organization_id)
    return {"valid": is_valid}


# Dashboard
@app.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    user: UserContext = Depends(get_user_context),
):
    """Get dashboard summary."""
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_locations = db.query(func.count(Location.id)).filter(
        Location.organization_id == user.organization_id
    ).scalar() or 0

    active_issues = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.status.in_(["open", "in_progress"]),
    ).scalar() or 0

    # Avg compliance score (placeholder)
    compliance_score_avg = 85.0

    # Monthly financial summary
    monthly_revenue = db.query(func.sum(FinancialRecord.revenue)).filter(
        FinancialRecord.date >= month_start,
    ).scalar() or 0

    monthly_expenses = db.query(func.sum(FinancialRecord.expenses)).filter(
        FinancialRecord.date >= month_start,
    ).scalar() or 0

    # Flagged locations (low compliance or high issues)
    flagged = db.query(Location).filter(
        Location.organization_id == user.organization_id,
        Location.status == "active",
    ).limit(5).all()

    return DashboardSummary(
        total_locations=total_locations,
        active_issues=active_issues,
        compliance_score_avg=compliance_score_avg,
        monthly_revenue=float(monthly_revenue),
        monthly_expenses=float(monthly_expenses),
        flagged_locations=flagged,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
