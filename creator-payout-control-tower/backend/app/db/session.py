from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker

BASE_DIR=Path(__file__).resolve().parents[3]
DB_PATH=BASE_DIR/"data"/"creator_payout.db"
DB_PATH.parent.mkdir(parents=True,exist_ok=True)
engine=create_engine(f"sqlite:///{DB_PATH}",connect_args={"check_same_thread":False})
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)
Base=declarative_base()
