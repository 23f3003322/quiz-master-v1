from werkzeug.security import generate_password_hash
from models.user import User
from database import db
import os

def create_admin():
    """Create an admin user if not exists."""
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin_user = User(
            username=os.getenv("ADMIN_USERNAME"),
            password=generate_password_hash(os.getenv("ADMIN_PASSWORD"), method="pbkdf2:sha256"),
            fullName=os.getenv("ADMIN_FULLNAME"),
            qualification=os.getenv("ADMIN_QUALIFICATION"),
            DOB=os.getenv("ADMIN_DOB"),
            role="admin"
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists.")