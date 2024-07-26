import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv() 

POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME")

engine = create_engine(f"postgresql+psycopg2://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB_NAME}")
engine.connect()
