import os
import threading
import time
from flask import Flask
from models.conn import db
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_login import LoginManager
from datetime import datetime, timedelta

from models.model import User

load_dotenv()

from blueprints.frontend import app as fe_bp
from blueprints.auth import auth as auth_bp

from modules.match_updater import update_matches

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.config['API_KEY'] = os.getenv('API_KEY')

db.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(fe_bp)
app.register_blueprint(auth_bp)

# flask_login user loader block
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    
    # return User.query.get(int(user_id))   # legacy
    
    return user

LASTUPDATE = None


def background_worker():
    global LASTUPDATE

    print("[Worker] Background worker started")

    while True:
        now = datetime.now()

        if LASTUPDATE is None or now - LASTUPDATE >= timedelta(hours=1):
            try:
                with app.app_context():
                    update_matches()
                    
                LASTUPDATE = datetime.now()

            except Exception as e:
                print(f"[Worker] Errore durante aggiornamento: {e}")

        time.sleep(60)


if __name__ == "__main__":
    worker = threading.Thread(target=background_worker, daemon=True)
    worker.start()

    app.run(debug=True)