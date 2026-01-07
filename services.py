"""
Business logic layer
ERP / Manual / API — sab yahin se guzrega
"""

from db import SessionLocal
from base import JobQueue


def get_pending_jobs():
    db = SessionLocal()
    jobs = (
        db.query(JobQueue)
        .filter(JobQueue.status == "Pending")
        .order_by(JobQueue.priority)
        .all()
    )
    db.close()
    return jobs
