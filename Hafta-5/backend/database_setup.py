import psycopg
from database import Base, engine
import models  # Modelleri içeri aktarıyoruz ki meta verileri (metadata) kaydedilsin

def create_database():
    try:
        # PostgreSQL varsayılan veritabanına bağlanıp yeni "sefer" veritabanını oluşturuyoruz
        conn = psycopg.connect(
            user="postgres",       # Lütfen kendi PostgreSQL kullanıcı adınızla değiştirin
            password="Krdlndmr1.",   # Lütfen kendi PostgreSQL şifrenizle değiştirin
            host="localhost",
            port="5432",
            dbname="postgres",      # Başlangıç test bağlantısı için varsayılan DB
            autocommit=True
        )
        cur = conn.cursor()
        
        cur.execute('CREATE DATABASE sefer;')
        print("'sefer' veritabani basariyla olusturuldu!")
        
        cur.close()
        conn.close()
    except psycopg.errors.DuplicateDatabase:
        print("'sefer' veritabani zaten mevcut, dogrudan tablolar olusturulacak.")
    except Exception as e:
        print("Veritabani olusturulurken bir hata olustu. Sifre, kullanici adi veya port yanlis olabilir.")
        print("Hata detayı:", e)
        return False
    
    return True

def create_tables():
    try:
        # SQLAlchemy kullanarak tanımladığımız 4 tabloyu (route, stop, passenger_demand, dispatch) veritabanına işleriz
        Base.metadata.create_all(bind=engine)
        print("Tum tablolar basariyla olusturuldu!")
    except Exception as e:
        print("Tablolar olusturulurken bir hata olustu.")
        print("Hata detayı:", e)

if __name__ == "__main__":
    print("Veritabanı kurulumu başlatılıyor...")
    if create_database():
        create_tables()
    print("Kurulum tamamlandı.")
