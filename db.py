from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./production.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def calculate_remaining_time(job):
    remaining = job.total_qty - job.completed_qty
    seconds = remaining * job.seconds_per_meter

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)

    return f"{hours}h {minutes}m"
