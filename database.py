from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 2. Создаем "движок" (Engine)
# connect_args={"check_same_thread": False} нужен только для SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Создаем фабрику сессий. Через эти сессии мы будем делать запросы.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Базовый класс для всех моделей (таблиц)
Base = declarative_base()

# Функция для получения сессии БД (её мы будем использовать в FastAPI через Depends)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()