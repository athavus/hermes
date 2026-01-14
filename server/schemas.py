from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import json

class DeviceStatusResponse(BaseModel):
    raspberry_id: str
    wifi_status: str
    mem_usage: str
    mem_percent: float
    cpu_temp: str
    cpu_percent: float
    spi_buses: int
    i2c_buses: int
    usb_devices_count: int
    net_bytes_sent: int
    net_bytes_recv: int
    net_ifaces: List[str]
    gpu_temp: str
    gpu_load: float
    last_update: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        data = obj.__dict__.copy()
        data['net_ifaces'] = json.loads(data.get('net_ifaces', '[]'))
        return cls(**data)

class DeviceStatusHistoryResponse(BaseModel):
    id: int
    raspberry_id: str
    wifi_status: str
    mem_usage: str
    cpu_temp: str
    cpu_percent: float
    spi_buses: int
    i2c_buses: int
    usb_devices_count: int
    net_bytes_sent: int
    net_bytes_recv: int
    net_ifaces: List[str]
    gpu_temp: str
    gpu_load: float
    timestamp: datetime

    class Config:
        from_attributes = True


