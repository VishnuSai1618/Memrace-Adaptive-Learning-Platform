from datetime import datetime
from models import db

class LiveSession(db.Model):
    """A real-time Kahoot-style live quiz session"""
    __tablename__ = 'live_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    pin = db.Column(db.String(6), unique=True, nullable=False, index=True)
    status = db.Column(db.String(20), default='waiting') # waiting, active, finished
    current_question_index = db.Column(db.Integer, default=-1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    host = db.relationship('User', backref=db.backref('hosted_live_sessions', lazy=True))
    deck = db.relationship('Deck', backref=db.backref('live_sessions', lazy=True))
    participants = db.relationship('LiveParticipant', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'host_id': self.host_id,
            'deck_id': self.deck_id,
            'pin': self.pin,
            'status': self.status,
            'current_question_index': self.current_question_index,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class LiveParticipant(db.Model):
    """A participant who joined a Live Session via PIN"""
    __tablename__ = 'live_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('live_sessions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Mobile users might not be logged in
    display_name = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, default=0)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('live_participations', lazy=True))
    answers = db.relationship('LiveAnswer', backref='participant', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'display_name': self.display_name,
            'score': self.score,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }

class LiveAnswer(db.Model):
    """An answer submitted by a participant during a Live Session question"""
    __tablename__ = 'live_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('live_participants.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    selected_answer = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    time_taken_ms = db.Column(db.Integer, default=0)
    score_awarded = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    quiz = db.relationship('Quiz')
    
    def to_dict(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'quiz_id': self.quiz_id,
            'selected_answer': self.selected_answer,
            'is_correct': self.is_correct,
            'time_taken_ms': self.time_taken_ms,
            'score_awarded': self.score_awarded,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }
