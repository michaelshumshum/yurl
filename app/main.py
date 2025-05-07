import datetime
import time
from urllib.parse import unquote

from flask import (
    Flask,
    Response,
    abort,
    g,
    make_response,
    redirect,
    render_template,
    request,
)

from . import config
from .auth.auth import AuthProvider
from .config import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    ALLOW_REGISTRATION,
    LINK_EXPIRY,
    MAX_LINK_EXPIRY,
    SESSION_EXPIRY,
)
from .db.db import Database
from .db.models import Link, User
from .new_user import new_user

app = Flask(__name__)

database = Database()
database.create_tables()

auth_provider = AuthProvider()

# create admin user if it doesn't exist
with database.get_session() as session:
    new_user(ADMIN_USERNAME, ADMIN_PASSWORD)


@app.route("/", methods=["GET"])
@auth_provider.authorization(deny=False)
def index():
    if g.get("username", None):
        with database.get_session() as session:
            links = session.query(Link).filter(Link.user == g.username).all()
            print(links)
            return render_template(
                "dashboard.html",
                links=links,
                datetime=datetime.datetime,
                timedelta=datetime.timedelta,
                config=config,
            )
    else:
        return render_template("login.html")


@app.route("/authenticate", methods=["POST"])
def authenticate():
    """
    Authenticates a user and saves the session token in the response headers.

    :return: dict
    """

    data = request.json
    if not data:
        return {"error": "invalid request"}, 400

    username = data.get("username")
    password = data.get("password")

    if username == "" or username is None:
        return {"error": "invalid credentials"}, 400

    if password == "" or password is None:
        return {"error": "invalid credentials"}, 400

    with database.get_session() as session:
        user = session.query(User).filter_by(username=username).first()

        if user is None or not user.check_password(password):
            return {"error": "invalid credentials"}, 400

        session = auth_provider.create_session(user)

    # set the user's session ID in the response headers
    response = make_response({"session": session.token}, 200)
    response.set_cookie(
        "session",
        session.token,
        expires=datetime.datetime.now() + datetime.timedelta(seconds=SESSION_EXPIRY),
    )

    return response


@app.route("/deauthenticate", methods=["POST"])
@auth_provider.authorization(deny=False)
def deauthenticate():
    if g.username:
        response = Response(status=200)
        response.set_cookie("session", "", 0)
        return response
    return Response(status=200)


@app.route("/register", methods=["POST"])
@auth_provider.authorization(deny=False)
def register():
    if not ALLOW_REGISTRATION and request.args.get("user", None) != "admin":
        abort(403)

    data = request.json
    if not data:
        return {"error": "invalid request"}, 400

    username = data.get("username")
    password = data.get("password")

    if username == "" or username is None:
        return {"error": "invalid credentials"}, 400

    if password == "" or password is None:
        return {"error": "invalid credentials"}, 400

    if new_user(username, password):
        return {"message": f"user '{username}' created"}, 201
    else:
        return {"error": "user already exists"}, 409


@app.route("/<string:id>", methods=["GET"])
def get_link(id: str):
    """
    Redirects to the url associated with the given id.

    :param id: str
    :return: dict
    """
    with database.get_session() as session:
        print(id)
        link = session.query(Link).filter(Link.id == id).first()

        if link is None:
            abort(404)

        if link.expiration_date < time.time():
            # delete the link
            with database.get_session() as session:
                session.delete(link)
            abort(410)

        # redirect to the url
        return redirect(link.url)


@app.route("/new/<path:url>", methods=["POST"])
@auth_provider.authorization(deny=True)
def create_link(url: str):
    """
    Creates a new link.

    :param url: str
    :return: dict
    """

    url = unquote(url)

    # ensure url starts with a schema, e.g. https, http, or even ws
    if len(url.split("://")) != 2:
        return {"error": "invalid url"}, 400

    # get the expiration time from query params
    # if not provided, use the default value from env

    expires = request.args.get("expires")
    if expires is not None:
        expires = int(expires)
        if (
            expires > MAX_LINK_EXPIRY and MAX_LINK_EXPIRY > 0
        ):  # if MAX_LINK_EXPIRY is 0, ignore the check, meaning no limit to expiration time
            return {"error": "expiration time too long"}, 400
        if (
            expires == 0
        ):  # if expires is 0, set it to infinity, which means never expire
            expiration_date = float("inf")
        else:
            expiration_date = time.time() + int(expires)
    else:
        expiration_date = time.time() + LINK_EXPIRY

    with database.get_session() as session:
        link = Link(
            url=url,
            user=g.username,
            expiration_date=expiration_date,
        )
        session.add(link)
        session.commit()

        return link.as_dict(), 201


# error handlers
@app.errorhandler(400)
def bad_request(error):
    return {"error": "bad request"}, 400


@app.errorhandler(401)
def unauthorized(error):
    return {"error": "unauthorized"}, 401


@app.errorhandler(403)
def forbidden(error):
    return {"error": "forbidden"}, 403


@app.errorhandler(404)
def not_found(error):
    return {"error": "not found"}, 404


@app.errorhandler(405)
def method_not_allowed(error):
    return {"error": "method not allowed"}, 405


@app.errorhandler(410)
def gone(error):
    return {"error": "gone"}, 410


@app.errorhandler(500)
def internal_server_error(error):
    return {"error": "internal server error"}, 500
