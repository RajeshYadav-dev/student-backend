from sqlmodel import create_engine,Session,SQLModel
from src.config import Config


# DATABASE_URL = "sqlite:///database.db"
# connect_args = {"check_same_thread": False}
engine = create_engine(url=Config.DATABASE_URL,echo=True)


def init_database():
  print("*******************INSIDE init_database****************")
  # SQLModel.metadata.drop_all(engine)
  SQLModel.metadata.create_all(engine)
  
def get_session():
  print("*******************INSIDE GetSession****************")
  with Session(engine) as session:
    yield session 