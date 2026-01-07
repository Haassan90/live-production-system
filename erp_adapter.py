"""
ERPNext Adapter Layer
--------------------
Ye file ERPNext se aane wale data ko
internal JobQueue format me convert karegi
"""

from db import SessionLocal
from base import JobQueue

# ERP → internal mapping
PIPE_SPEED = {
    20: 20,
    32: 20,
    33: 22,
    110: 52,
}


def erp_work_order_to_job(work_order: dict):
    """
    ERPNext work order ko
    JobQueue me convert karta hai
    """

    pipe_size = work_order["pipe_size"]
    total_qty = work_order["length_meter"]

    seconds_per_meter = PIPE_SPEED.get(pipe_size)
    if not seconds_per_meter:
        raise ValueError("Unsupported pipe size")

    db = SessionLocal()

    job = JobQueue(
        pipe_size=pipe_size,
        total_qty=total_qty,
        priority=1,
        status="Pending"
    )

    db.add(job)
    db.commit()
    db.close()

    return {
        "status": "queued",
        "pipe_size": pipe_size,
        "qty": total_qty,
        "seconds_per_meter": seconds_per_meter
    }
