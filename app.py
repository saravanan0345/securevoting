from flask import Flask

from config import Config
from database.seed import seed_demo_data
from models.models import db
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        if not app.config.get("TESTING", False):
            seed_demo_data()

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
