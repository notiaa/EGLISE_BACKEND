from sqlmodel import SQLModel, create_engine, Session
from core.config import DATABASE_URL

# Créer l'engine
engine = create_engine(DATABASE_URL)

# Définir Base pour Alembic
Base = SQLModel.metadata  # Alembic a besoin de target_metadata

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
