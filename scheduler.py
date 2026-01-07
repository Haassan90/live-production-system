import time
import asyncio
from threading import Thread

from db import SessionLocal
from base import Machine, JobQueue
from config import PIPE_SPEED
from websocket import broadcast


# =========================================
# ERP → JOB QUEUE
# =========================================
def pull_erp_work_orders(db):
    erp_jobs = fetch_work_orders()

    for wo in erp_jobs:
        exists = (
            db.query(JobQueue)
            .filter(JobQueue.work_order == wo["work_order"])
            .first()
        )

        if not exists:
            db.add(JobQueue(
                work_order=wo["work_order"],
                pipe_size=wo["pipe_size"],
                total_qty=wo["quantity"],
                completed_qty=0,
                priority=wo.get("priority", 1),
                status="pending"
            ))


# =========================================
# MAIN SCHEDULER LOOP
# =========================================
def scheduler_loop():
    while True:
        db = SessionLocal()

        try:
            # -------------------------------
            # 1️⃣ PULL ERP WORK ORDERS
            # -------------------------------
            pull_erp_work_orders(db)

            # -------------------------------
            # 2️⃣ UPDATE RUNNING JOBS
            # -------------------------------
            running_jobs = (
                db.query(JobQueue)
                .filter(JobQueue.status == "running")
                .all()
            )

            for job in running_jobs:
                speed = PIPE_SPEED.get(job.pipe_size)
                if not speed:
                    continue

                job.completed_qty += (1 / speed)
                job.remaining_seconds -= 1

                # 🔄 ERP LIVE UPDATE
                update_work_order_progress(
                    job.work_order,
                    job.completed_qty,
                    "In Progress"
                )

                # ✅ JOB COMPLETED (STEP 17.3)
                if job.remaining_seconds <= 0:
                    job.status = "completed"

                    machine = (
                        db.query(Machine)
                        .filter(Machine.id == job.assigned_machine)
                        .first()
                    )

                    if machine:
                        machine.status = "free"
                        machine.current_job_id = None

                    # 🔔 ERP FINAL UPDATE
                    update_work_order_progress(
                        job.work_order,
                        job.total_qty,
                        "Completed"
                    )

            db.commit()

            # -------------------------------
            # 3️⃣ ASSIGN NEW JOBS
            # -------------------------------
            free_machines = (
                db.query(Machine)
                .filter(Machine.status == "free")
                .all()
            )

            for machine in free_machines:
                next_job = (
                    db.query(JobQueue)
                    .filter(JobQueue.status == "pending")
                    .order_by(JobQueue.priority)
                    .first()
                )

                if not next_job:
                    break

                speed = PIPE_SPEED.get(next_job.pipe_size)
                if not speed:
                    continue

                total_seconds = next_job.total_qty * speed

                machine.status = "running"
                machine.current_job_id = next_job.id

                next_job.status = "running"
                next_job.assigned_machine = machine.id
                next_job.remaining_seconds = total_seconds

                db.commit()

        finally:
            db.close()

        # 🔔 FRONTEND LIVE UPDATE
        try:
            asyncio.run(broadcast({"type": "tick"}))
        except RuntimeError:
            pass

        time.sleep(1)


# =========================================
# START THREAD
# =========================================
def start_scheduler():
    Thread(target=scheduler_loop, daemon=True).start()
