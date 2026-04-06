from flask import Flask, render_template, send_from_directory
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User
import os

# Import blueprints
from routes.auth import auth_bp
from routes.content import content_bp
from routes.flashcards import flashcards_bp
from routes.quizzes import quizzes_bp
from routes.analytics import analytics_bp
from routes.repository import repository_bp
from routes.recommendations import recommendations_bp

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize SocketIO
    from flask_socketio import SocketIO
    # Create socketio object globally but init here so it can be imported elsewhere
    # (Actually it's better to create it in a separate file or attach to app)
    # We will attach it to the app instance for now
    socketio = SocketIO(app, cors_allowed_origins="*")
    app.socketio = socketio
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Import Live Quiz models so they are created
    import models.live_quiz
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(flashcards_bp)
    app.register_blueprint(quizzes_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(repository_bp)
    app.register_blueprint(recommendations_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Routes for serving HTML pages
    @app.route('/')
    def landing():
        """Landing page"""
        return render_template('landing.html')
    
    @app.route('/login')
    def login():
        """Login page"""
        return render_template('login.html')
    
    @app.route('/signup')
    def signup():
        """Signup page"""
        return render_template('signup.html')
    
    @app.route('/forgot-password')
    def forgot_password_page():
        """Forgot password page"""
        return render_template('forgot_password.html')
    
    @app.route('/reset-password/<token>')
    def reset_password_page(token):
        """Reset password page — token is passed into the template for the JS form submit"""
        return render_template('reset_password.html', token=token)
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard page"""
        return render_template('dashboard.html')
    
    @app.route('/upload')
    def upload():
        """Content upload page"""
        return render_template('upload.html')
    
    @app.route('/study/<int:deck_id>')
    def study(deck_id):
        """Flashcard study page"""
        return render_template('study.html', deck_id=deck_id)
    
    @app.route('/quiz/<int:deck_id>')
    def quiz(deck_id):
        """Quiz page"""
        return render_template('quiz.html', deck_id=deck_id)
        
    @app.route('/deck/<int:deck_id>/edit')
    def edit_deck(deck_id):
        """Edit Deck page"""
        return render_template('edit_deck.html', deck_id=deck_id)
    
    @app.route('/analytics')
    def analytics():
        """Analytics page"""
        return render_template('analytics.html')
    
    @app.route('/repository')
    def repository():
        """Public repository page"""
        return render_template('repository.html')
        
    @app.route('/ai-coach')
    def ai_coach():
        """AI Coach page"""
        return render_template('ai_coach.html')
        
    # --- LIVE QUIZ ROUTES ---
    @app.route('/live/join')
    def live_join():
        """Public page for participants to enter a PIN and join a Live Quiz"""
        return render_template('live_join.html')

    @app.route('/live/player/<int:session_id>')
    def live_player(session_id):
        """Participant's interactive game controller screen"""
        return render_template('live_player.html', session_id=session_id)

    @app.route('/live/host/<int:deck_id>')
    def live_host(deck_id):
        """Host's dashboard to broadcast a Live Quiz"""
        # Authentication is handled in the template or by the socket connection, 
        # but for simplicity we will check the session directly here
        from flask import session
        if 'user_id' not in session:
            from flask import redirect, url_for
            return redirect(url_for('login'))
            
        from models.deck import Deck
        deck = Deck.query.get_or_404(deck_id)
        if deck.user_id != session['user_id']:
            from flask import jsonify
            return jsonify({'error': 'Unauthorized access'}), 403
            
        return render_template('live_host.html', deck_id=deck_id)
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Register live quiz socket event handlers
    from routes.live_events import register_events
    register_events(app.socketio)
    
    print("=" * 50)
    print("AI-Powered Flashcard Learning System")
    print("=" * 50)
    print("Server starting on http://localhost:5000")
    print("=" * 50)
    # Use socketio.run instead of app.run
    app.socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
