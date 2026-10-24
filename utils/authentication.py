from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash

import os
import smtplib

from email.message import EmailMessage
from flask import request, jsonify, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from models import db, User



auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    existing = User.query.filter(
        db.or_(
            User.username == username,
            User.email == email
            )

    ).first()

    if existing:
        return jsonify({"error": "Username or email already exists"}), 409

    user = User(username=username, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    session.clear()
    session["user_id"] = user.id
    session["username"] = user.username

    return jsonify({
        "message": "Account created successfully",
        "user_id": user.id,
        "username": user.username
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or request.form

    login_id = (
        data.get('user_id')
        or data.get('email')
        or data.get('login_id')
        or ''
    ).strip()

    password = data.get("password", ' ')

    if not login_id or not password:
        return jsonify({"error": "Email/Username and password are required"}), 400

    user = None


    if login_id.isdigit():
        user = db.session.get(User, int(login_id))

    if user is None:
        user = User.query.filter_by(email=login_id).first()

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['username'] = user.username

        return jsonify({
            'message': 'Login successful',
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        }), 200

    return jsonify({
        'message': 'Invalid User ID/Email or password'
    }), 401


@auth_bp.route("/me")
def me():
    if "user_id" not in session:
        return jsonify({"error": "Please log in first"}), 401

    return jsonify({
        "user_id": session["user_id"],
        "username": session["username"]
    })


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})




def create_reset_serializer():
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )


def send_reset_email(email, reset_url):
    message = EmailMessage()
    message["Subject"] = "Reset Your Image Gallery Password"
    message["From"] = os.environ["MAIL_USERNAME"]
    message["To"] = email

    message.set_content(
        f"Click this link to reset your password:\n{reset_url}\n\n"
        "This link expires in 15 minutes."
    )

    with smtplib.SMTP_SSL(
        os.environ.get("MAIL_SERVER", "smtp.gmail.com"),
        int(os.environ.get("MAIL_PORT", "465"))
    ) as server:
        server.login(
            os.environ["MAIL_USERNAME"],
            os.environ["MAIL_APP_PASSWORD"]
        )
        server.send_message(message)


@auth_bp.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"message": "Enter your email address."}), 400

    user = User.query.filter_by(email=email).first()

    if user:
        try:
            token = create_reset_serializer().dumps(
                email,
                salt="password-reset"
            )

            base_url = os.environ.get(
                "APP_BASE_URL",
                request.url_root.rstrip("/")
            )

            reset_url = f"{base_url}/?reset_token={token}"
            send_reset_email(email, reset_url)

        except Exception:
            current_app.logger.exception("Password reset email failed")
            return jsonify({
                "message": "Email failed. Check your email configuration."
            }), 500

    return jsonify({
        "message": "If the account exists, a reset link will be sent."
    }), 200


@auth_bp.route("/api/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json(silent=True) or {}
    token = data.get("token", "")
    password = data.get("password", "")

    if not token or not password:
        return jsonify({"message": "Token and password are required."}), 400

    if len(password) < 8:
        return jsonify({
            "message": "Password must contain at least 8 characters."
        }), 400

    try:
        email = create_reset_serializer().loads(
            token,
            salt="password-reset",
            max_age=900
        )
    except SignatureExpired:
        return jsonify({"message": "Reset link expired. Request another."}), 400
    except BadSignature:
        return jsonify({"message": "Invalid reset link."}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "Account not found."}), 400

    user.set_password(password)
    db.session.commit()

    return jsonify({
        "message": "Password reset successfully. You can now log in."
    }), 200

