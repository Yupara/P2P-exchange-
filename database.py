import os
from sqlalchemy import create_engine

database_url = os.getenv("DATABASE_URL", "sqlite:///p2p.db")  # Фallback на SQLite
engine = create_engine(database_url)
