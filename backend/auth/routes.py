
from flask import Blueprint, request, jsonify
from models import User
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# ----------- REGISTER ROUTE -----------
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json(force=True)  # ensure JSON is parsed

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not all([name, email, password]):
            return jsonify({"message": "All fields are required"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already exists"}), 400

        # Hash password
        hashed_pw = generate_password_hash(password)

        # Create user with role 'user'
        user = User(name=name, email=email, password=hashed_pw, role="user")
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        print("Register Error:", e)
        return jsonify({"message": "Internal Server Error"}), 500

# ----------- LOGIN ROUTE -----------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 401

    if not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid email or password"}), 401

    token = create_access_token(identity={"id": user.id, "role": user.role})
    return jsonify({"access_token": token, "role": user.role}), 200
