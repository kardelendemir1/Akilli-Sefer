from fastapi import WebSocket
from typing import List
import json

class ConnectionManager:
    """
    Tüm canlı (WebSocket) bağlantılarını yöneten merkezi sınıf mimarisi.
    Böylece projedeki "Anlık Yolcu Bilgisi" tek bir elden dağıtılabilir.
    """
    def __init__(self):
        # Sisteme bağlı olan (Admin paneline giren) tüm tarayıcıların açık soketleri
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Yeni bir kullanıcı bağlandığında onu havuza ekle."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Kullanıcı tarayıcıyı kapattığında veya bağlantı koptuğunda onu havuzdan sil."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_demand_update(self, message_data: dict):
        """
        Duraklarda bir kart okunduğunda veya eşik algoritması devreye girdiğinde,
        mevcut tüm izleyicilere (yöneticilere) aynı anda güncel durumu stringe (JSON) çevirip yollar.
        """
        text_message = json.dumps(message_data)
        for connection in self.active_connections:
            try:
                await connection.send_text(text_message)
            except Exception:
                # Olası bir ölü bağlantı hatasını görmezden gel, disconnect() daha sonra temizleyecektir.
                pass

# Proje boyunca tek bir bellek üzerinden yayın yapabilmek için (Singleton)
manager = ConnectionManager()
