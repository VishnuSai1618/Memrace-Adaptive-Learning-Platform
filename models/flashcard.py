from datetime import datetime, timedelta
from models import db

class Flashcard(db.Model):
    """Flashcard model with SM-2 spaced repetition fields"""
    
    __tablename__ = 'flashcards'
    
    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    
    # SM-2 Algorithm fields
    ease_factor = db.Column(db.Float, default=2.5)  # Initial ease factor
    interval = db.Column(db.Integer, default=0)  # Days until next review
    repetitions = db.Column(db.Integer, default=0)  # Number of successful repetitions
    next_review = db.Column(db.DateTime, default=datetime.utcnow)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('FlashcardReview', backref='flashcard', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, deck_id, question, answer):
        """Initialize flashcard with default SM-2 values"""
        self.deck_id = deck_id
        self.question = question
        self.answer = answer
        self.ease_factor = 2.5
        self.interval = 0
        self.repetitions = 0
        self.next_review = datetime.utcnow()
    
    def is_due(self):
        """Check if flashcard is due for review"""
        return datetime.utcnow() >= self.next_review
    
    def to_dict(self):
        """Convert flashcard to dictionary"""
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'question': self.question,
            'answer': self.answer,
            'ease_factor': self.ease_factor,
            'interval': self.interval,
            'repetitions': self.repetitions,
            'next_review': self.next_review.isoformat() if self.next_review else None,
            'is_due': self.is_due(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Flashcard {self.id}: {self.question[:30]}...>'


class FlashcardReview(db.Model):
    """Track individual flashcard review attempts"""
    
    __tablename__ = 'flashcard_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    flashcard_id = db.Column(db.Integer, db.ForeignKey('flashcards.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    correct = db.Column(db.Boolean, nullable=False)
    response_time_ms = db.Column(db.Integer)  # Response time in milliseconds
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, flashcard_id, user_id, correct, response_time_ms=0):
        """Initialize review record"""
        self.flashcard_id = flashcard_id
        self.user_id = user_id
        self.correct = correct
        self.response_time_ms = response_time_ms
    
    def to_dict(self):
        """Convert review to dictionary"""
        return {
            'id': self.id,
            'flashcard_id': self.flashcard_id,
            'user_id': self.user_id,
            'correct': self.correct,
            'response_time_ms': self.response_time_ms,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None
        }
    
    def __repr__(self):
        return f'<FlashcardReview {self.id}: {"Correct" if self.correct else "Wrong"}>'
