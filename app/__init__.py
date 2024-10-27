from flask import Flask
from flask_login import LoginManager

from config import Config
from app.extensions import db, is_admin
from app.models.user import User


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    print(f"Upload Folder: {app.config['UPLOAD_FOLDER']}")

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.get_or_404(User, user_id)

    # Initialize Flask extensions here
    db.init_app(app)

    @app.context_processor
    def check_admin():
        template_config = {"is_admin": is_admin()}
        return template_config

    ## Register blueprints here
    # Register
    from app.register import bp as register_bp

    app.register_blueprint(register_bp, url_prefix="/register")

    # Main
    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    # Login
    from app.login import bp as login_bp

    app.register_blueprint(login_bp, url_prefix="/login")

    # Logout
    from app.logout import bp as logout_bp

    app.register_blueprint(logout_bp, url_prefix="/logout")

    # Upload
    from app.upload import bp as upload_bp

    app.register_blueprint(upload_bp, url_prefix="/upload")

    # Edit
    from app.edit import bp as edit_bp

    app.register_blueprint(edit_bp, url_prefix="/edit")

    # Delete
    from app.delete import bp as delete_bp

    app.register_blueprint(delete_bp, url_prefix="/delete")

    # Compare
    from app.compare import bp as compare_bp

    app.register_blueprint(compare_bp, url_prefix="/compare")

    # Update or ignore data comparison
    from app.update_or_ignore import bp as update_or_ignore_bp

    app.register_blueprint(update_or_ignore_bp, url_prefix="/update_or_ignore")

    # Datatable
    from app.dt import bp as dt_bp

    app.register_blueprint(dt_bp, url_prefix="/dt")

    # Secret Page (Admin Only)
    from app.secret import bp as secret_bp

    app.register_blueprint(secret_bp, url_prefix="/secret")

    # User Management (Admin Only)
    from app.users import bp as users_bp

    app.register_blueprint(users_bp, url_prefix="/users")

    # Plot data
    from app.chart import bp as chart_bp

    app.register_blueprint(chart_bp, url_prefix="/chart")

    return app
