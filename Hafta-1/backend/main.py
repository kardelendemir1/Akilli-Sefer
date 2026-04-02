from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

import models
import schemas
from database import engine, get_db

# Uygulama başlarken veritabanı tablolarını yoksa oluşturur
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Otobüs Kart Sistemi ve Anlık Sefer API")

@app.get("/")
def read_root():
    return {
        "message": "Otobüs Kartı Sistemi ve Anlık Sefer API Çalışıyor! API dökümantasyonunu görmek için /docs adresine gidebilirsiniz."
    }

@app.post("/api/setup-test-data")
def setup_test_data(db: Session = Depends(get_db)):
    """
    Sistemi kullanmaya başlamadan önce test edebilmeniz için varsayılan bir otobüs hattı ve durak ekler.
    """
    route = db.query(models.Route).filter(models.Route.name == "500T Tuzla-Şifa").first()
    if not route:
        route = models.Route(name="500T Tuzla-Şifa", threshold=20)
        db.add(route)
        db.commit()
        db.refresh(route)
        
    stop = db.query(models.Stop).filter(models.Stop.name == "Cevizlibağ").first()
    if not stop:
        stop = models.Stop(name="Cevizlibağ", route_id=route.id)
        db.add(stop)
        db.commit()
        db.refresh(stop)

    return {"message": "Test verileri (Hat ve Durak) başarıyla eklendi.", "route_id": route.id, "stop_id": stop.id}

@app.post("/api/tap-card", response_model=schemas.PassengerDemandResponse)
def tap_card(demand: schemas.PassengerDemandCreate, db: Session = Depends(get_db)):
    """
    Yolcunun otobüs kartını okutarak sisteme kayıt olduğu uç nokta.
    """
    # 1. Durağın veritabanında var olup olmadığını kontrol et
    stop = db.query(models.Stop).filter(models.Stop.id == demand.stop_id).first()
    if not stop:
        raise HTTPException(status_code=404, detail="Durak bulunamadı. Lütfen geçerli bir durak ID girin. (Önce /api/setup-test-data endpoint'ini çalıştırabilirsiniz)")

    # 2. Yolcu talebini (Kart okutmayı) veritabanına kaydet
    new_demand = models.PassengerDemand(
        stop_id=demand.stop_id,
        card_id=demand.card_id,  # Otobüs kartı numarası
        status="waiting",        # Şimdilik bekliyor statüsünde
        timestamp=datetime.utcnow()
    )
    db.add(new_demand)
    db.commit()
    db.refresh(new_demand)

    # İlerleyecek aşamalarda eşik(threshold) kontrolü algoritması buraya eklenecektir.

    return new_demand

@app.get("/api/demands", response_model=list[schemas.PassengerDemandResponse])
def get_demands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Raporlama için tüm kart okutma kayıtlarını listeler.
    """
    demands = db.query(models.PassengerDemand).offset(skip).limit(limit).all()
    return demands
