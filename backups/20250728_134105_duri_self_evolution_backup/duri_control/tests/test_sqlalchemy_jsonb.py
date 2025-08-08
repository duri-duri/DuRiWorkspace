from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from duri_control.app.models.memory import MemoryEntry

engine = create_engine("postgresql://duri:duri@duri-postgres:5432/duri")
Session = sessionmaker(bind=engine)
session = Session()

query = session.query(MemoryEntry).filter(MemoryEntry.tags.contains(['test']))
print(query.statement) 