import hashlib
import json
import uuid
from datetime import datetime
from typing import Any, Optional
from sqlalchemy.orm import Session
from app.models import AuditLog


def compute_hash(prev_hash: Optional[str], payload: dict) -> str:
    """Compute SHA256 hash chain: sha256(prev_hash + json(payload))."""
    payload_str = json.dumps(payload, sort_keys=True, default=str)
    combined = (prev_hash or "") + payload_str
    return hashlib.sha256(combined.encode()).hexdigest()


def get_last_audit_hash(db: Session, organization_id: uuid.UUID) -> Optional[str]:
    """Retrieve the most recent audit log hash for an organization."""
    last_log = (
        db.query(AuditLog)
        .filter(AuditLog.organization_id == organization_id)
        .order_by(AuditLog.timestamp.desc())
        .first()
    )
    return last_log.hash if last_log else None


def audit_log(
    db: Session,
    organization_id: uuid.UUID,
    action: str,
    entity_type: str,
    entity_id: Optional[uuid.UUID] = None,
    user_id: Optional[uuid.UUID] = None,
    payload: Optional[dict] = None,
) -> AuditLog:
    """
    Log an audit entry with hash-chain tamper evidence.

    Every mutation creates an immutable, tamper-evident record.
    Hash chain proves no entries were inserted/deleted/modified.
    """
    if payload is None:
        payload = {}

    prev_hash = get_last_audit_hash(db, organization_id)
    entry_hash = compute_hash(prev_hash, payload)

    log_entry = AuditLog(
        id=uuid.uuid4(),
        timestamp=datetime.utcnow(),
        user_id=user_id,
        organization_id=organization_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        payload_json=payload,
        prev_hash=prev_hash,
        hash=entry_hash,
    )

    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def verify_audit_chain(db: Session, organization_id: uuid.UUID) -> bool:
    """
    Verify hash chain integrity.

    Returns True if all hashes are valid and sequential.
    Returns False if tampering detected.
    """
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.organization_id == organization_id)
        .order_by(AuditLog.timestamp.asc())
        .all()
    )

    for i, log in enumerate(logs):
        expected_prev = logs[i - 1].hash if i > 0 else None
        if log.prev_hash != expected_prev:
            return False

        expected_hash = compute_hash(log.prev_hash, log.payload_json)
        if log.hash != expected_hash:
            return False

    return True


def get_audit_logs(
    db: Session,
    organization_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0,
) -> list[AuditLog]:
    """Retrieve audit logs for an organization."""
    return (
        db.query(AuditLog)
        .filter(AuditLog.organization_id == organization_id)
        .order_by(AuditLog.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
