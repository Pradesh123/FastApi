from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = 'postgresql://waction:w%40ct10n@localhost:5432/farmer_proj'
engine = create_engine(DATABASE_URL)
session_local = sessionmaker(autoflush=False, bind=engine)
Base = declarative_base()
