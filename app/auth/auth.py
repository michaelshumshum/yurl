import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, TypeVar

from flask import abort, g, request
from flask.typing import RouteCallable

from app.config import SESSION_EXPIRY
from app.db.models import User
from app.util import random_string

T_route = TypeVar("T_route", bound=RouteCallable)

logger = logging.getLogger(__name__)


class AuthSession:
    _user: User
    _username: str
    _token: str
    expires_at: datetime

    def __init__(self, user: User):
        self._user = user
        self._username = user.username
        self._token = random_string(32)
        self.expires_at = datetime.utcnow() + timedelta(seconds=SESSION_EXPIRY)

    @property
    def user(self):
        return self._user

    @property
    def username(self):
        return self._username

    @property
    def token(self):
        return self._token

    @property
    def expired(self):
        return datetime.utcnow() > self.expires_at

    def __str__(self):
        return f"AuthSession(user={self.user}, token={self.token}, expires_at={self.expires_at})"

    def __repr__(self):
        return self.__str__()


class AuthProvider:
    sessions: dict[str, AuthSession]

    def __init__(self):
        self.sessions = {}

    def create_session(
        self,
        user: User,
    ) -> AuthSession:
        session = AuthSession(user=user)
        self.sessions[session.token] = session
        return session

    def get_session(self, token: str) -> AuthSession | None:
        session = self.sessions.get(token)
        if session and session.expired:
            self.delete_session(token)
            session = None
        return session

    def delete_session(self, token: str):
        self.sessions.pop(token, None)

    def purge_expired_sessions(self):
        for token, session in list(self.sessions.items()):
            if session.expired:
                self.delete_session(token)

    def authorization(self, deny: bool = False) -> Callable[[T_route], T_route]:
        """
        Decorator for routes that require authentication.

        If the user is authenticated, the session is stored in `g.username`, which represents the currently logged in user's username.
        """

        def decorator(func: T_route) -> T_route:
            @wraps(func)
            def wrapper(*args, **kwargs):
                session_token = request.cookies.get("session")
                if session_token:
                    session = self.get_session(session_token)
                    if session:
                        g.username = session.username
                        logger.info(g.username)
                        return func(*args, **kwargs)
                    elif deny:
                        abort(403)
                elif deny:
                    abort(403)
                return func(*args, **kwargs)

            return wrapper  # type: ignore

        return decorator
