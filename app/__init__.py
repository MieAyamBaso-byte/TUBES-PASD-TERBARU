from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.expenses import expenses_bp
    from app.routes.analytics import analytics_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(analytics_bp)
    
    return app