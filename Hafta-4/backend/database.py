from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL bağlantı dizesi
# Format: postgresql://kullanici_adi:sifre@sunucu:port/veritabani
# Varsayılan değerler kullanılmıştır, gerekirse kendinize göre düzenleyin
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:Krdlndmr1.@localhost/sefer"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# FastAPI bağımlılığı olarak kullanılacak veritabanı oturumu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
