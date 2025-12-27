from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import get_settings

# 설정 가져오기
settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db_session():
    """데이터베이스 세션 반환"""
    return SessionLocal()


def get_db():
    """FastAPI dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()