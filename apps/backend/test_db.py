import sqlalchemy
from sqlalchemy import create_engine
import psycopg

urls = [
    "postgresql+psycopg://user:password@localhost:5432/career_maps",
    "postgresql+psycopg://postgres:postgres@localhost:5432/careermaps",
    "postgresql+psycopg://postgres:postgres@localhost:5432/postgres",
    "postgresql+psycopg://postgres:@localhost:5432/postgres",
]

for url in urls:
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            print(f"Success: {url}")
            break
    except Exception as e:
        print(f"Failed: {url} - {e}")
