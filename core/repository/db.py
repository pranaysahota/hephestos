from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from core.model.models import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://pranaysahota:@localhost/cross_sell")

engine = create_engine(DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
