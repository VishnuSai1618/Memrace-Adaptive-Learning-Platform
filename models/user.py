from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from models import db

class User(UserMixin, db.Model):
    """User model for authentication and profile management"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Gamification Fields
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak = db.Column(db.Integer, default=0)
    last_study_date = db.Column(db.Date)
    
    # Relationships (will be added as models are implemented)
    decks = db.relationship('Deck', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, username, email, password):
        """Initialize user with hashed password"""
        self.username = username
        self.email = email
        self.set_password(password)
        self.xp = 0
        self.level = 1
        self.streak = 0
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
        
    def add_xp(self, amount):
        """Add XP to the user and handle leveling up"""
        if self.xp is None: self.xp = 0
        if self.level is None: self.level = 1
            
        self.xp += amount
        threshold = self.level * 1000
        
        # Check for level up
        if self.xp >= threshold:
            self.level += 1
            # Keep excess XP, or you could optionally reset to 0
            # self.xp -= threshold 
        
        db.session.commit()
        return self.level, self.xp
        
    def update_streak(self):
        """Update the daily study streak"""
        if self.streak is None: self.streak = 0
        
        today = datetime.utcnow().date()
        
        if not self.last_study_date:
            self.streak = 1
            self.last_study_date = today
        else:
            delta = (today - self.last_study_date).days
            
            if delta == 1:
                # Studied yesterday, increment streak
                self.streak += 1
                self.last_study_date = today
            elif delta > 1:
                # Missed a day, reset streak
                self.streak = 1
                self.last_study_date = today
            # If delta == 0, they already studied today, keep current streak
                
        db.session.commit()
        return self.streak
    
    def to_dict(self):
        """Convert user to dictionary (exclude password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'xp': self.xp or 0,
            'level': self.level or 1,
            'streak': self.streak or 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'last_study_date': self.last_study_date.isoformat() if self.last_study_date else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
