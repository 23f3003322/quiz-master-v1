from flask import Flask,render_template
from config import Config
from database import db
from models import *  # Import models
from controllers import register_blueprints
from utils.auth_utils import create_admin

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Register blueprints
    register_blueprints(app)

    return app

app = create_app()

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
        create_admin()  # Ensure admin exists

    app.run(debug=True)
