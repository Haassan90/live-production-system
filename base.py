from sqlalchemy import Column, Integer, String, Float, ForeignKey
from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)  # manager / operator


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True)
    name = Column(String)
    status = Column(String)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    pipe_size = Column(Integer)
    total_qty = Column(Float)
    completed_qty = Column(Float, default=0)
    seconds_per_meter = Column(Float)
    status = Column(String)
    machine_id = Column(Integer, ForeignKey("machines.id"))


class JobQueue(Base):
    __tablename__ = "job_queue"

    id = Column(Integer, primary_key=True, index=True)
    work_order = Column(String, nullable=True) 
    pipe_size = Column(Integer)
    total_qty = Column(Float)
    priority = Column(Integer, default=1)
    status = Column(String, default="Pending")
