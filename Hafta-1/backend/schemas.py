from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# API İstek ve Yanıt Şemaları (Veri Doğrulama için)

class PassengerDemandCreate(BaseModel):
    stop_id: int
    card_id: str

class PassengerDemandResponse(BaseModel):
    id: int
    stop_id: int
    card_id: str
    timestamp: datetime
    status: str

    class Config:
        from_attributes = True

class RouteBase(BaseModel):
    name: str
    threshold: int

class StopBase(BaseModel):
    route_id: int
    name: str
