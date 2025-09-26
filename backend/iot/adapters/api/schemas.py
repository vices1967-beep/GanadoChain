# backend/iot/api/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class SensorDataInput(BaseModel):
    """Esquema para entrada de datos de sensores"""
    device_id: str
    auth_token: str
    data_type: str
    raw_data: Dict[str, Any]
    timestamp: datetime
    accuracy: Optional[float] = None
    battery_level: Optional[int] = None

class DeviceRegistrationInput(BaseModel):
    """Esquema para registro de dispositivos"""
    device_id: str
    serial_number: str
    device_type: str
    auth_token: str
    public_key: str
    manufacturer: str
    model: str

class GatewayHeartbeatInput(BaseModel):
    """Esquema para heartbeat de gateway"""
    gateway_id: str
    auth_token: str
    connected_devices: list
    system_metrics: Dict[str, Any]