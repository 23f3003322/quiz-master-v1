import os
from flask import Flask
from application.database import db
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

app = None

load_dotenv()

def create_app():
    app = Flask(__name__) 
    app.debug = True
    app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///quizdb.sqlite3"
    db.init_app(app)
    app.app_context().push()#runtime error, brings everything under context of flask application
    return app

app = create_app()
from application.controllers import *

def create_admin ():
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin_user = User(
                username=os.getenv('ADMIN_USERNAME'),
                password=generate_password_hash(os.getenv('ADMIN_PASSWORD'), method='pbkdf2:sha256'),  # Secure password hashing
                fullName= os.getenv('ADMIN_FULLNAME'),
                qualification = os.getenv('ADMIN_QUALIFICATION'),
                DOB = os.getenv("ADMIN_DOB"),
                role='admin'

            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
        create_admin()  
    app.run(debug=True)