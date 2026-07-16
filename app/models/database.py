from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Membuat engine SQLite. File database akan bernama physio_data.db dan diletakkan di folder utama aplikasi
engine = create_engine("sqlite:///physio_data.db", echo=False)

# SessionLocal digunakan untuk berinteraksi (menyimpan/mengambil data) dari database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class yang akan diwarisi (inherit) oleh semua komponen tabel kita
Base = declarative_base()

def init_db():
    """Fungsi ini akan dipanggil saat aplikasi pertama kali dibuka untuk membuat file .db dan tabelnya."""
    Base.metadata.create_all(bind=engine)
