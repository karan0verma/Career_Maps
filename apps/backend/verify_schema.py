from sqlalchemy import create_engine, inspect
import psycopg

engine = create_engine("postgresql+psycopg://postgres:postgres@localhost:5432/careermaps")
inspector = inspect(engine)

print("Tables:")
for table_name in inspector.get_table_names():
    print(f"- {table_name}")
    for column in inspector.get_columns(table_name):
        print(f"  {column['name']}: {column['type']}")
