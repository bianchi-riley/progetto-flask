from flask import Flask
from models.conn import db
from flask_migrate import Migrate

from blueprints.frontend import app as fe_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlalchemy_app.db'

db.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(fe_bp)

if __name__ == "__main__":
    app.run(debug=True)