import os
from contextlib import contextmanager
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()


class Database:
    session: Optional[Session]

    def __init__(self):
        self.engine = create_engine(os.getenv("DB_URL", ""))
        self.connection = self.engine.connect()
        self.session = None

    def create_tables(self):
        Base.metadata.create_all(self.engine, checkfirst=True)

    def drop_tables(self):
        Base.metadata.drop_all(self.engine)

    def close(self):
        self.connection.close()

    @contextmanager
    def get_session(self):
        if not self.session:
            self.session = Session(self.engine)
        try:
            yield self.session
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        finally:
            self.session.close()
            self.session = None
