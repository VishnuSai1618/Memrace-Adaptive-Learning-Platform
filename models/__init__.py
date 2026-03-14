from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Import all models
from models.user import User
from models.deck import Deck
from models.flashcard import Flashcard, FlashcardReview
from models.quiz import Quiz, QuizAttempt
from models.analytics import StudySession, PublicDeck
