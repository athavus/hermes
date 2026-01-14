from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from consumer import start_consumer_thread
from shared import received_messages
from database import (
    get_db, init_db, DeviceStatus, DeviceStatusHistory, SessionLocal
)
from schemas import (
    DeviceStatusResponse, DeviceStatusHistoryResponse
)
import csv
import io
import zipfile

# Inicializar banco de dados
init_db()

# Iniciar consumer do RabbitMQ em thread separada
start_consumer_thread()

app = FastAPI(
    title="Raspberry Pi 5 IoT Telemetry API",
    description="API para monitoramento de telemetria de cluster Raspberry Pi",
    version="1.0.0"
)

# CORS configurado para máxima compatibilidade em desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "*" # Fallback
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== DEVICE STATUS ENDPOINTS ====================

@app.get("/api/devices/status", response_model=List[DeviceStatusResponse], tags=["Device Status"])
def get_all_devices_status(db: Session = Depends(get_db)):
    devices = db.query(DeviceStatus).all()
    return [DeviceStatusResponse.from_orm(device) for device in devices]

@app.get("/api/devices/{raspberry_id}/status", response_model=DeviceStatusResponse, tags=["Device Status"])
def get_device_status(raspberry_id: str, db: Session = Depends(get_db)):
    device = db.query(DeviceStatus).filter(DeviceStatus.raspberry_id == raspberry_id).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Dispositivo não encontrado")
    
    return DeviceStatusResponse.from_orm(device)

@app.get("/api/devices/{raspberry_id}/status/history", response_model=List[DeviceStatusHistoryResponse], tags=["Device Status"])
def get_device_status_history(
    raspberry_id: str,
    hours: int = Query(24, le=720),
    limit: int = Query(500, le=5000),
    db: Session = Depends(get_db)
):
    since = datetime.utcnow() - timedelta(hours=hours)
    rows = db.query(DeviceStatusHistory).filter(
        DeviceStatusHistory.raspberry_id == raspberry_id,
        DeviceStatusHistory.timestamp >= since
    ).order_by(DeviceStatusHistory.timestamp.desc()).limit(limit).all()
    return rows

# ==================== REAL-TIME DATA ENDPOINTS ====================

@app.get("/api/data/realtime", tags=["Real-time Data"])
def get_realtime_data(limit: int = Query(50, le=200)):
    if received_messages:
        return {
            "count": len(received_messages),
            "data": received_messages[-limit:]
        }
    
    return {
        "count": 0,
        "data": []
    }

@app.post("/api/data", tags=["Real-time Data"])
def post_data(data: dict):
    received_messages.append(data)
    return {"status": "received", "data": data}

# ==================== EXPORT ENDPOINTS ====================

@app.get("/api/export/db.zip", tags=["Export"])
def export_database_zip(db: Session = Depends(get_db)):
    """Exporta todas as tabelas em CSV dentro de um ZIP único."""
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        # Device Status (current)
        rows = db.query(DeviceStatus).order_by(DeviceStatus.last_update.desc()).all()
        buffer = io.StringIO(); writer = csv.writer(buffer)
        writer.writerow(["id","raspberry_id","wifi_status","mem_usage","cpu_temp","cpu_percent","net_bytes_sent","net_bytes_recv","net_ifaces","last_update"]) 
        for r in rows:
            writer.writerow([r.id, r.raspberry_id, r.wifi_status, r.mem_usage, r.cpu_temp, r.cpu_percent, r.net_bytes_sent, r.net_bytes_recv, r.net_ifaces, r.last_update.isoformat()])
        zf.writestr("device_status.csv", buffer.getvalue())

        # Device Status History
        rows = db.query(DeviceStatusHistory).order_by(DeviceStatusHistory.timestamp.desc()).all()
        buffer = io.StringIO(); writer = csv.writer(buffer)
        writer.writerow(["id","raspberry_id","wifi_status","mem_usage","cpu_temp","cpu_percent","net_bytes_sent","net_bytes_recv","net_ifaces","timestamp"]) 
        for r in rows:
            writer.writerow([r.id, r.raspberry_id, r.wifi_status, r.mem_usage, r.cpu_temp, r.cpu_percent, r.net_bytes_sent, r.net_bytes_recv, r.net_ifaces, r.timestamp.isoformat()])
        zf.writestr("device_status_history.csv", buffer.getvalue())

    mem.seek(0)
    return StreamingResponse(mem, media_type="application/zip", headers={
        "Content-Disposition": "attachment; filename=raspberry_telemetry_export.zip"
    })

# ==================== HEALTH CHECK ENDPOINTS ====================

@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "online",
        "service": "Raspberry Pi 5 IoT Telemetry",
        "version": "1.0.0",
        "features": [
            "Device Health Monitoring",
            "RabbitMQ Messaging",
            "Historical Data Storage"
        ]
    }

@app.get("/health", tags=["Health Check"])
def health_check(db: Session = Depends(get_db)):
    health_status = {
        "api": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        db.execute("SELECT 1")
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
    
    health_status["rabbitmq_consumer"] = "running"
    
    try:
        device_count = db.query(DeviceStatus).count()
        health_status["registered_devices"] = device_count
    except:
        health_status["registered_devices"] = "unknown"
    
    return health_status

@app.get("/api/stats", tags=["Health Check"])
def get_stats(db: Session = Depends(get_db)):
    try:
        total_devices = db.query(DeviceStatus).count()
        
        return {
            "total_devices": total_devices,
            "realtime_messages": len(received_messages),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
def shutdown_event():
    print("Desligando API...")



