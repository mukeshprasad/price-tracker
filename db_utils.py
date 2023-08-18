from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from constants import DB_URL


class DBUtils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_db_session():
        engine = create_engine(DB_URL)
        session = sessionmaker(engine)()
        return session
