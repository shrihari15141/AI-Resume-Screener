from __future__ import annotations

from flask_jwt_extended import get_jwt_identity

from extensions import db
from models import User


DEFAULT_USER_EMAIL = "recruiter@example.com"
DEFAULT_USER_NAME = "Demo Recruiter"


def default_user() -> User:
    existing_user = User.query.order_by(User.id.asc()).first()
    if existing_user:
        return existing_user

    user = User.query.filter_by(email=DEFAULT_USER_EMAIL).first()
    if user:
        return user

    user = User(username=DEFAULT_USER_NAME, email=DEFAULT_USER_EMAIL)
    user.set_password("local-no-login")
    db.session.add(user)
    db.session.commit()
    return user


def current_user() -> User:
    identity = get_jwt_identity()
    if identity:
        user = db.session.get(User, int(identity))
        if user:
            return user
    return default_user()


def current_user_id() -> int:
    return current_user().id
