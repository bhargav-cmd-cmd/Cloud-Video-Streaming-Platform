import os
from flask import Flask
from flask_login import LoginManager
from models import db, User

# Import Blueprints
from routes.auth import auth_bp
from routes.main import main_bp
from routes.video import video_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'dev_secret_key_vidistream_platform_987654321'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Upload configurations
    app.config['UPLOAD_FOLDER_VIDEOS'] = os.path.join(app.root_path, 'uploads', 'videos')
    app.config['UPLOAD_FOLDER_THUMBNAILS'] = os.path.join(app.root_path, 'uploads', 'thumbnails')
    # Limit uploads to 100MB
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
    
    # Initialize DB
    db.init_app(app)
    
    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        # Using Session.get() for compatibility with SQLAlchemy 2.0 or legacy query.get()
        if hasattr(db.session, 'get'):
            return db.session.get(User, int(user_id))
        return User.query.get(int(user_id))
        
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(video_bp)
    
    # Create upload directories if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER_VIDEOS'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER_THUMBNAILS'], exist_ok=True)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
