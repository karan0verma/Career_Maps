from sqlalchemy import inspect
from src.db.session import engine

inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'Tables: {tables}')

if 'crawl_history' in tables:
    columns = [c['name'] for c in inspector.get_columns('crawl_history')]
    print(f'crawl_history columns: {columns}')
    
if 'company_ats_history' in tables:
    print('company_ats_history is PRESENT')
else:
    print('company_ats_history is MISSING')

if 'company_sources' in tables:
    print('company_sources is PRESENT')
else:
    print('company_sources is MISSING')
