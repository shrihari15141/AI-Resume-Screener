from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required
from pydantic import ValidationError

from auth_context import current_user
from extensions import db
from models import User
from utils.validators import LoginPayload, RegisterPayload


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    try:
        payload = RegisterPayload.model_validate(request.get_json() or {})
    except ValidationError as exc:
        return jsonify({"message": "Invalid registration details.", "errors": exc.errors()}), 400

    if User.query.filter_by(email=payload.email.lower()).first():
        return jsonify({"message": "An account with this email already exists."}), 409

    user = User(username=payload.username, email=payload.email.lower())
    user.set_password(payload.password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"user": user.to_dict(), "access_token": token}), 201


@auth_bp.post("/login")
def login():
    try:
        payload = LoginPayload.model_validate(request.get_json() or {})
    except ValidationError as exc:
        return jsonify({"message": "Invalid login details.", "errors": exc.errors()}), 400

    user = User.query.filter_by(email=payload.email.lower()).first()
    if not user or not user.check_password(payload.password):
        return jsonify({"message": "Invalid email or password."}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"user": user.to_dict(), "access_token": token})


@auth_bp.post("/logout")
@jwt_required(optional=True)
def logout():
    return jsonify({"message": "Logged out."})


@auth_bp.get("/me")
@jwt_required(optional=True)
def me():
    return jsonify({"user": current_user().to_dict()})
