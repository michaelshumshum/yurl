import time
from hashlib import sha256

from shortuuid import ShortUUID
from sqlalchemy import Column, ForeignKey, Integer, String

from .db import Base


class User(Base):
    """
    User model.
    """

    __tablename__ = "users"
    username = Column(String(32), unique=True, primary_key=True)
    password = Column(String(64), nullable=False)
    salt = Column(String(16), nullable=False)

    def check_password(self, password: str) -> bool:
        """
        Checks if the given password matches the user's password.

        :param password: str
        :return: bool
        """
        return self.password == sha256((password + self.salt).encode()).hexdigest()


class Link(Base):
    """
    Link model.
    """

    __tablename__ = "links"
    id = Column(
        String(6), primary_key=True, default=lambda: ShortUUID().random(length=6)
    )
    url = Column(String(2048), nullable=False)
    user = Column(String, ForeignKey("users.username"), nullable=False)
    creation_date = Column(Integer, nullable=False, default=lambda: int(time.time()))
    expiration_date = Column(Integer, nullable=False)

    def as_dict(self):
        """
        Returns the link as a dictionary, excluding the user field.

        :return: dict
        """
        return {
            "id": self.id,
            "url": self.url,
            "creation_date": self.creation_date,
            "expiration_date": self.expiration_date,
        }
