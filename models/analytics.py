from datetime import datetime
from models import db

class StudySession(db.Model):
    """Track study sessions for analytics"""
    
    __tablename__ = 'study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    cards_reviewed = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    total_time_ms = db.Column(db.Integer, default=0)  # Total time in milliseconds
    session_start = db.Column(db.DateTime, default=datetime.utcnow)
    session_end = db.Column(db.DateTime)
    
    def __init__(self, user_id, deck_id):
        """Initialize study session"""
        self.user_id = user_id
        self.deck_id = deck_id
        self.cards_reviewed = 0
        self.correct_count = 0
        self.total_time_ms = 0
        self.session_start = datetime.utcnow()
    
    def end_session(self):
        """Mark session as ended"""
        self.session_end = datetime.utcnow()
    
    def get_accuracy(self):
        """Calculate accuracy percentage"""
        if self.cards_reviewed == 0:
            return 0
        return (self.correct_count / self.cards_reviewed) * 100
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'deck_id': self.deck_id,
            'cards_reviewed': self.cards_reviewed,
            'correct_count': self.correct_count,
            'accuracy': round(self.get_accuracy(), 2),
            'total_time_ms': self.total_time_ms,
            'session_start': self.session_start.isoformat() if self.session_start else None,
            'session_end': self.session_end.isoformat() if self.session_end else None
        }
    
    def __repr__(self):
        return f'<StudySession {self.id}: {self.cards_reviewed} cards>'


class PublicDeck(db.Model):
    """Track publicly shared decks"""
    
    __tablename__ = 'public_decks'
    
    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False, unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    clone_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    deck = db.relationship('Deck', backref='public_info', uselist=False)
    author = db.relationship('User', backref='published_decks')
    
    def __init__(self, deck_id, author_id):
        """Initialize public deck"""
        self.deck_id = deck_id
        self.author_id = author_id
        self.clone_count = 0
        self.rating = 0.0
    
    def increment_clone_count(self):
        """Increment clone counter"""
        self.clone_count += 1
        db.session.commit()
    
    def to_dict(self):
        """Convert public deck to dictionary"""
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'author_id': self.author_id,
            'author_username': self.author.username if self.author else None,
            'deck_title': self.deck.title if self.deck else None,
            'deck_description': self.deck.description if self.deck else None,
            'flashcard_count': len(self.deck.flashcards) if self.deck and self.deck.flashcards else 0,
            'clone_count': self.clone_count,
            'rating': self.rating,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
    
    def __repr__(self):
        return f'<PublicDeck {self.id}: Deck {self.deck_id}>'
