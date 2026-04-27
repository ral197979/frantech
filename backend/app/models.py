import uuid
import hashlib
import json
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text, UUID, ForeignKey, Integer, Boolean, Numeric, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AuditLog(Base):
    """P0: Immutable audit log with hash-chain tamper evidence."""
    __tablename__ = "audit_logs"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = Column(UUID, nullable=True)
    organization_id = Column(UUID, nullable=False, index=True)
    action = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False, index=True)
    entity_id = Column(UUID, nullable=True)
    payload_json = Column(JSON, nullable=False)
    prev_hash = Column(Text, nullable=True)
    hash = Column(Text, nullable=False, unique=True, index=True)

    __table_args__ = (
        Index('ix_audit_org_timestamp', 'organization_id', 'timestamp'),
        Index('ix_audit_entity', 'entity_type', 'entity_id'),
    )


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    owner_id = Column(UUID, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Location(Base):
    __tablename__ = "locations"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    manager_name = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Staff(Base):
    __tablename__ = "staff"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID, ForeignKey("locations.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SOP(Base):
    __tablename__ = "sops"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID, ForeignKey("organizations.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    checklist_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ComplianceRecord(Base):
    __tablename__ = "compliance_records"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID, ForeignKey("locations.id"), nullable=False, index=True)
    sop_id = Column(UUID, ForeignKey("sops.id"), nullable=False)
    score = Column(Integer, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID, ForeignKey("locations.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="open")
    priority = Column(String, default="normal")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID, ForeignKey("locations.id"), nullable=False, index=True)
    assigned_to = Column(UUID, ForeignKey("staff.id"), nullable=True)
    title = Column(String, nullable=False)
    due_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID, ForeignKey("locations.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    revenue = Column(Numeric(12, 2), default=0)
    expenses = Column(Numeric(12, 2), default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(Base):
    """Auth user for JWT."""
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    organization_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
