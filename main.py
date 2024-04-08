from flask import Flask
from flask_login import LoginManager

from models import Base, User, engine, session
from routes import register_routes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hgfert654jhbhy6t5rt54re4edsfrvgbhyh'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    
    if user:
        return user
    else:
        return None

import db

RECIPES_PER_PAGE = 10

register_routes(app, RECIPES_PER_PAGE, session)

if __name__ == "__main__":
    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Run the Flask application
    app.run(debug=True)
