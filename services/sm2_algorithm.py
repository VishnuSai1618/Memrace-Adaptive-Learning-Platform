from datetime import datetime, timedelta
from models import db

class SM2Algorithm:
    """
    Implementation of the SM-2 (SuperMemo 2) spaced repetition algorithm
    
    The algorithm calculates optimal review intervals based on user performance.
    """
    
    @staticmethod
    def calculate_next_review(flashcard, quality):
        """
        Calculate next review date and update flashcard parameters
        
        Args:
            flashcard: Flashcard model instance
            quality: Quality of recall (0-5)
                    0-2: Incorrect (reset)
                    3-5: Correct (increase interval)
                    
        The SM-2 algorithm uses:
        - EF (Ease Factor): Difficulty multiplier (1.3 to 2.5+)
        - Interval: Days until next review
        - Repetitions: Number of consecutive correct answers
        """
        
        # Validate quality score
        if quality < 0 or quality > 5:
            quality = max(0, min(5, quality))
        
        # If quality < 3, reset the card (incorrect answer)
        if quality < 3:
            flashcard.repetitions = 0
            flashcard.interval = 1  # Review again tomorrow
        else:
            # Correct answer - calculate new interval
            if flashcard.repetitions == 0:
                flashcard.interval = 1  # First correct: review in 1 day
            elif flashcard.repetitions == 1:
                flashcard.interval = 6  # Second correct: review in 6 days
            else:
                # Subsequent reviews: multiply by ease factor
                flashcard.interval = round(flashcard.interval * flashcard.ease_factor)
            
            flashcard.repetitions += 1
        
        # Update ease factor based on quality
        # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        flashcard.ease_factor = flashcard.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        
        # Ensure ease factor stays within bounds (minimum 1.3)
        if flashcard.ease_factor < 1.3:
            flashcard.ease_factor = 1.3
        
        # Calculate next review date
        flashcard.next_review = datetime.utcnow() + timedelta(days=flashcard.interval)
        
        # Commit changes to database
        db.session.commit()
        
        return flashcard
    
    @staticmethod
    def process_review(flashcard, correct, response_time_ms=0):
        """
        Process a flashcard review and update using SM-2
        
        Args:
            flashcard: Flashcard model instance
            correct: Boolean indicating if answer was correct
            response_time_ms: Time taken to answer in milliseconds
            
        Returns:
            Updated flashcard
        """
        # Convert boolean to quality score
        # Correct answers get quality 4, incorrect get quality 2
        # (In a more advanced system, quality could be based on response time)
        quality = 4 if correct else 2
        
        # Apply SM-2 algorithm
        updated_flashcard = SM2Algorithm.calculate_next_review(flashcard, quality)
        
        return updated_flashcard
    
    @staticmethod
    def get_due_flashcards(deck_id):
        """
        Get all flashcards due for review in a deck
        
        Args:
            deck_id: ID of the deck
            
        Returns:
            List of flashcard instances due for review
        """
        from models.flashcard import Flashcard
        
        due_cards = Flashcard.query.filter(
            Flashcard.deck_id == deck_id,
            Flashcard.next_review <= datetime.utcnow()
        ).all()
        
        return due_cards
    
    @staticmethod
    def get_upcoming_reviews(user_id, days=7):
        """
        Get count of upcoming reviews for a user
        
        Args:
            user_id: ID of the user
            days: Number of days to look ahead
            
        Returns:
            Dictionary with date -> count mapping
        """
        from models.flashcard import Flashcard
        from models.deck import Deck
        
        end_date = datetime.utcnow() + timedelta(days=days)
        
        flashcards = db.session.query(Flashcard).join(Deck).filter(
            Deck.user_id == user_id,
            Flashcard.next_review <= end_date
        ).all()
        
        # Group by date
        review_schedule = {}
        for card in flashcards:
            date_key = card.next_review.date().isoformat()
            review_schedule[date_key] = review_schedule.get(date_key, 0) + 1
        
        return review_schedule
