from datetime import datetime
from models import db

class Deck(db.Model):
    __tablename__ = 'decks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    source_type = db.Column(db.String(20))
    original_content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)
    
    flashcards = db.relationship('Flashcard', backref='deck', lazy=True, cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='deck', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, user_id, title, description='', source_type='text', original_content='', is_public=False):
        self.user_id = user_id
        self.title = title
        self.description = description
        self.source_type = source_type
        self.original_content = original_content
        self.is_public = is_public
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'source_type': self.source_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_public': self.is_public,
            'flashcard_count': len(self.flashcards) if self.flashcards else 0,
            'quiz_count': len(self.quizzes) if self.quizzes else 0
        }
    
    def __repr__(self):
        return f'<Deck {self.title}>'