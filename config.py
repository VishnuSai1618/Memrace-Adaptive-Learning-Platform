import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Flask application configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///flashcard_system.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Google Gemini API
    # Single-key (legacy, backward-compatible)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    # Multi-key (comma-separated, takes priority in gemini_client.py)
    GEMINI_API_KEYS = os.getenv('GEMINI_API_KEYS')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'txt'}
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        pass
