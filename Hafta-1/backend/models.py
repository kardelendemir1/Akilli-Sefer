from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Route(Base):
    __tablename__ = "route"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    threshold = Column(Integer, default=20)
    
    stops = relationship("Stop", back_populates="route")

class Stop(Base):
    __tablename__ = "stop"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("route.id"))
    name = Column(String, index=True)

    route = relationship("Route", back_populates="stops")
    demands = relationship("PassengerDemand", back_populates="stop")

class PassengerDemand(Base):
    __tablename__ = "passenger_demand"

    id = Column(Integer, primary_key=True, index=True)
    stop_id = Column(Integer, ForeignKey("stop.id"))
    card_id = Column(String, index=True) # Yolcunun Otobüs Kartı Numarası veya ID'si
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="waiting") # 'waiting' (bekliyor) veya 'boarded' (bindi)

    stop = relationship("Stop", back_populates="demands")

class Dispatch(Base):
    __tablename__ = "dispatch"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("route.id"))
    scheduled_time = Column(DateTime, default=datetime.utcnow)
    is_extra = Column(Boolean, default=False)
