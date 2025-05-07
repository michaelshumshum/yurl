import sys
from getpass import getpass
from hashlib import sha256

from app.util import random_string

from .db.db import Database
from .db.models import User


def new_user(username: str, password: str) -> bool:
    """
    Creates a new user in the database and return the API key.
    :param username: str

    :return: str
    """

    db = Database()
    db.create_tables()

    # check if user already exists
    with db.get_session() as session:
        user = session.query(User).filter_by(username=username).first()
        if user is not None:
            return False

    # create new user
    with db.get_session() as session:
        salt = random_string()
        password = sha256((password + salt).encode()).hexdigest()
        user = User(username=username, password=password, salt=salt)
        session.add(user)
        session.commit()

    return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        username = input("Enter username: ")
        password = getpass("Enter password: ")
        if not username:
            print("Username cannot be empty")
            sys.exit(1)
        if not password:
            print("Password cannot be empty")
    else:
        username = sys.argv[1]
        password = sys.argv[2]
    if new_user(username, password):
        print("User already exists")
        sys.exit(1)
    print(f"User created with username: {username}")
