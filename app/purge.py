import time

from .db.db import Database
from .db.models import Link


def purge_links() -> int:
    """
    Purge all links that are expired.

    :return: int
    """
    database = Database()

    with database.get_session() as session:
        links = session.query(Link).filter(Link.expiration_date > time.time()).all()
        for link in links:
            session.delete(link)
        session.commit()

    return len(links)


if __name__ == "__main__":
    print(f"Purged {purge_links()} links")
