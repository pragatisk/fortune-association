import os
import secrets

from dotenv import load_dotenv
from flask import Flask, render_template

from .extensions import csrf, init_db_pool


def create_app():
    load_dotenv()

    app = Flask(__name__)

    app.secret_key = os.environ.get('SECRET_KEY')
    if not app.secret_key:
        app.secret_key = secrets.token_hex(32)
        print("WARNING: SECRET_KEY not set in environment. Using a temporary "
              "random key for this run only - sessions will invalidate on "
              "restart. Set SECRET_KEY in your .env file.")

    csrf.init_app(app)
    init_db_pool(app)

    from .blueprints import auth, main, academics, events, live, analytics
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(academics.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(live.bp)
    app.register_blueprint(analytics.bp)

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', message="You don't have access to this page"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', message="Page not found"), 404

    return app
