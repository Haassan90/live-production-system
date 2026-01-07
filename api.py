from fastapi import FastAPI
from db import SessionLocal
from base import Machine, JobQueue
from config import PIPE_SPEED

app = FastAPI()


# ===============================
# UTILITY
# ===============================
def format_eta(seconds: int) -> str:
    if seconds is None or seconds <= 0:
        return "0h 0m"

    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h}h {m}m"


# ===============================
# DASHBOARD SUMMARY
# ===============================
@app.get("/api/dashboard")
def dashboard():
    db = SessionLocal()
    try:
        machines = db.query(Machine).all()
        data = {}

        for m in machines:
            loc = m.location
            if loc not in data:
                data[loc] = {
                    "total": 0,
                    "running": 0,
                    "free": 0
                }

            data[loc]["total"] += 1
            if m.status == "running":
                data[loc]["running"] += 1
            else:
                data[loc]["free"] += 1

        return data
    finally:
        db.close()


# ===============================
# MACHINES + JOB CARDS
# ===============================
@app.get("/api/machines")
def get_machines():
    db = SessionLocal()
    try:
        result = {}

        machines = db.query(Machine).all()

        for m in machines:
            loc = m.location
            if loc not in result:
                result[loc] = []

            job_data = None

            if m.current_job_id:
                job = db.query(JobQueue)\
                        .filter(JobQueue.id == m.current_job_id)\
                        .first()

                if job:
                    job_data = {
                        "work_order": f"WO-{job.id}",
                        "size": job.pipe_size,
                        "total_qty": job.total_qty,
                        "completed_qty": round(job.completed_qty, 2),
                        "remaining_time": format_eta(job.remaining_seconds)
                    }

            result[loc].append({
                "id": m.id,
                "name": m.name,
                "status": m.status,
                "job": job_data
            })

        return result
    finally:
        db.close()


# ===============================
# JOB QUEUE (DEBUG / TEST)
# ===============================
@app.get("/api/jobs")
def get_jobs():
    db = SessionLocal()
    try:
        jobs = db.query(JobQueue).all()
        return [
            {
                "id": j.id,
                "pipe_size": j.pipe_size,
                "total_qty": j.total_qty,
                "completed_qty": round(j.completed_qty, 2),
                "status": j.status,
                "priority": j.priority,
                "assigned_machine": j.assigned_machine,
                "remaining_time": format_eta(j.remaining_seconds)
            }
            for j in jobs
        ]
    finally:
        db.close()
from fastapi import Header

@app.post("/api/erp/work-order")
def receive_work_order(
    data: dict,
    authorization: str = Header(None)
):
    # simple token check (later improve)
    if authorization != "Bearer ERP_SECRET":
        return {"error": "Unauthorized"}

    db = SessionLocal()
    try:
        job = JobQueue(
            pipe_size=data["pipe_size"],
            total_qty=data["qty"],
            completed_qty=0,
            status="pending",
            priority=data.get("priority", 1),
            location=data["location"]
        )
        db.add(job)
        db.commit()

        return {"status": "ok", "job_id": job.id}
    finally:
        db.close()
