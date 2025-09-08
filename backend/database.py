import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get the absolute path to the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the database URL using this absolute path for reliability
SQLALCHEMY_DATABASE_URL = "sqlite:///" + os.path.join(BASE_DIR, "sql_app.db")

# Create the SQLAlchemy engine, adding the crucial 'timeout' argument
# This prevents 'database is locked' errors during busy operations.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 15}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
