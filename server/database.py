from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./raspberry_data.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DeviceStatus(Base):
    __tablename__ = "device_status"
    id = Column(Integer, primary_key=True, index=True)
    raspberry_id = Column(String, unique=True, index=True)
    wifi_status = Column(String, default="unknown")
    mem_usage = Column(String, default="0 MB")
    mem_percent = Column(Float, default=0.0)
    cpu_temp = Column(String, default="0°C")
    cpu_percent = Column(Float, default=0.0)
    net_bytes_sent = Column(Integer, default=0)
    net_bytes_recv = Column(Integer, default=0)
    net_ifaces = Column(Text, default="[]")
    gpu_temp = Column(String, default="N/A")
    gpu_load = Column(Float, default=0.0)
    last_update = Column(DateTime, default=datetime.utcnow)

class DeviceStatusHistory(Base):
    """Histórico contínuo de status do dispositivo para relatórios"""
    __tablename__ = "device_status_history"
    id = Column(Integer, primary_key=True, index=True)
    raspberry_id = Column(String, index=True)
    wifi_status = Column(String, default="unknown")
    mem_usage = Column(String, default="0 MB")
    mem_percent = Column(Float, default=0.0)
    cpu_temp = Column(String, default="0°C")
    cpu_percent = Column(Float, default=0.0)
    net_bytes_sent = Column(Integer, default=0)
    net_bytes_recv = Column(Integer, default=0)
    net_ifaces = Column(Text, default="[]")
    gpu_temp = Column(String, default="N/A")
    gpu_load = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
