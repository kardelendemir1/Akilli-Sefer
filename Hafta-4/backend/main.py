from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from datetime import datetime

import models
import schemas
from database import engine, get_db
import ai_service
from websocket_manager import manager
import auth


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
def tap_card(demand: schemas.PassengerDemandCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Yolcunun otobüs kartını okutarak sisteme kayıt olduğu uç nokta.
    Canlı WebSocket yayını burada tetiklenir.
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

    # 3. İlerleyecek aşamalarda eşik(threshold) kontrolü algoritması buraya eklenecektir.

    # 4. YENİ EKLENEN WEBSOCKET CANLI YAYINI:
    # O durağa özel anlık bekleyen yolcu sayısını bul (Dashboard için)
    waiting_count = db.query(models.PassengerDemand).filter(
        models.PassengerDemand.stop_id == demand.stop_id,
        models.PassengerDemand.status == "waiting"
    ).count()

    ws_message = {
        "event": "new_tap",
        "stop_id": demand.stop_id,
        "waiting_count": waiting_count,
        "timestamp": str(new_demand.timestamp),
        "message": f"Durak ID {demand.stop_id}'de yeni hareket, bekleyen sayısı: {waiting_count}"
    }
    
    # Asenkron websocket yayın işlemini Background (Arka Plan) tetikleyiciye devret
    background_tasks.add_task(manager.broadcast_demand_update, ws_message)

    return new_demand

@app.get("/api/demands", response_model=list[schemas.PassengerDemandResponse])
def get_demands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Raporlama için tüm kart okutma kayıtlarını listeler.
    """
    demands = db.query(models.PassengerDemand).offset(skip).limit(limit).all()
    return demands

@app.post("/api/auth/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="E-posta zaten kayıtlı")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login", response_model=schemas.Token)
def login_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="E-posta numarası veya şifre yanlış")
    
    access_token = auth.create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/admin/chat", response_model=schemas.AdminChatResponse)
def admin_chat(request: schemas.AdminChatRequest, db: Session = Depends(get_db)):
    """
    Yönetici paneli için Gemini altyapılı asistan uç noktası.
    """
    # 1. Sistemin mevcut istatistiklerini hesapla
    total_routes = db.query(models.Route).count()
    total_stops = db.query(models.Stop).count()
    total_waiting = db.query(models.PassengerDemand).filter(models.PassengerDemand.status == "waiting").count()
    
    # İleride dispatch tablosuna bağladığımızda ekstra sefer sayısını da ölçeceğiz
    stats = {
        "total_routes": total_routes,
        "total_stops": total_stops,
        "total_waiting": total_waiting,
        "extra_dispatch_count": 0 
    }
    
    # 2. Gemini modeline sor ve yanıtı al
    reply_text = ai_service.get_admin_assistant_reply(request.message, stats)
    
    return schemas.AdminChatResponse(reply=reply_text)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Vite/React gibi modern frontend yapılarının (Örn Yönetici Paneli) 
    anlık veri akışına canlı abone olacağı yer.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Client'tan bir sinyal bekle
            data = await websocket.receive_text()
            # Şu anki iskelet mimarisinde sadece bağlantıyı açık tutmaya fayda sağlıyor
            # İleride yönetim panelinden admin "ek sefer onayı" yollarsa bu data ile işlenebilir.
    except WebSocketDisconnect:
        manager.disconnect(websocket)

