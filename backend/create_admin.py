from werkzeug.security import generate_password_hash
from app import create_app
from extensions import db
from models import User
import os

app = create_app()

with app.app_context():
    # Ensure tables exist
    db.create_all()

    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace("sqlite:///", "")
    print("Using DB:", db_path)

    admin_email = "admin@gmail.com"
    admin = User.query.filter_by(email=admin_email).first()

    if admin:
        admin.password = generate_password_hash("admin123")
        db.session.commit()
        print("Admin already exists — password updated")
    else:
        admin = User(
            email=admin_email,
            password=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin created successfully")
