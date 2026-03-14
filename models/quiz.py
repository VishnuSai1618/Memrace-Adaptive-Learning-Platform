from datetime import datetime
from models import db

class Quiz(db.Model):
    """Quiz model for multiple-choice questions"""
    
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, deck_id, question, correct_answer, option_a, option_b, option_c, option_d):
        """Initialize quiz question"""
        self.deck_id = deck_id
        self.question = question
        self.correct_answer = correct_answer
        self.option_a = option_a
        self.option_b = option_b
        self.option_c = option_c
        self.option_d = option_d
    
    def to_dict(self):
        """Convert quiz to dictionary"""
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'question': self.question,
            'correct_answer': self.correct_answer,
            'options': {
                'A': self.option_a,
                'B': self.option_b,
                'C': self.option_c,
                'D': self.option_d
            },
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Quiz {self.id}: {self.question[:30]}...>'


class QuizAttempt(db.Model):
    """Track quiz attempts and performance"""
    
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    selected_answer = db.Column(db.String(255), nullable=False)
    correct = db.Column(db.Boolean, nullable=False)
    time_taken_ms = db.Column(db.Integer)  # Time taken in milliseconds
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, quiz_id, user_id, selected_answer, correct, time_taken_ms=0):
        """Initialize quiz attempt"""
        self.quiz_id = quiz_id
        self.user_id = user_id
        self.selected_answer = selected_answer
        self.correct = correct
        self.time_taken_ms = time_taken_ms
    
    def to_dict(self):
        """Convert attempt to dictionary"""
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'user_id': self.user_id,
            'selected_answer': self.selected_answer,
            'correct': self.correct,
            'time_taken_ms': self.time_taken_ms,
            'attempted_at': self.attempted_at.isoformat() if self.attempted_at else None
        }
    
    def __repr__(self):
        return f'<QuizAttempt {self.id}: {"Correct" if self.correct else "Wrong"}>'
