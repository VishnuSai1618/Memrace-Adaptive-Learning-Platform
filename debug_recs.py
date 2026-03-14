
from app import create_app
from models import db, User, Deck, Flashcard, FlashcardReview
from services.recommendation import RecommendationEngine
import random

app = create_app()

with app.app_context():
    print("--- Starting Debug ---")
    
    # 1. Create a test user if not exists
    user = User.query.filter_by(username='debug_user').first()
    if not user:
        user = User(username='debug_user', email='debug@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        print(f"Created debug_user with ID: {user.id}")
    else:
        print(f"Using existing debug_user with ID: {user.id}")
        
    # 2. Create a deck (owned by someone else, e.g., admin or even the user themselves, let's try user first)
    deck = Deck.query.filter_by(title='Debug Deck').first()
    if not deck:
        deck = Deck(user_id=user.id, title='Debug Deck', description='Testing recommendations')
        db.session.add(deck)
        db.session.commit()
        
        # Add flashcards
        for i in range(5):
            fc = Flashcard(deck_id=deck.id, question=f'Q{i}', answer=f'A{i}')
            db.session.add(fc)
        db.session.commit()
        print(f"Created deck '{deck.title}' with ID: {deck.id}")
    else:
        print(f"Using existing deck '{deck.title}' with ID: {deck.id}")
        
    # 3. Create failure reviews (9 fails, 1 success) for this user on this deck
    # First, clear existing reviews for this user/deck combo to ensure clean state
    cards = Flashcard.query.filter_by(deck_id=deck.id).all()
    card_ids = [c.id for c in cards]
    
    existing_reviews = FlashcardReview.query.filter(
        FlashcardReview.user_id == user.id,
        FlashcardReview.flashcard_id.in_(card_ids)
    ).delete()
    db.session.commit()
    print("Cleared usage history for clean test.")
    
    print("Simulating 9 fails and 1 success...")
    for i in range(10):
        # card = random.choice(cards)
        card = cards[i % len(cards)]
        is_correct = (i == 9) # Only last one is correct. 9 fails.
        review = FlashcardReview(flashcard_id=card.id, user_id=user.id, correct=is_correct)
        db.session.add(review)
    db.session.commit()
    
    # 4. Run the RecommendationEngine
    print("\nRunning get_weak_topics...")
    weak_topics = RecommendationEngine.get_weak_topics(user.id)
    
    print(f"\nResult Weak Topics: {weak_topics}")
    
    if weak_topics:
        print("\nSUCCESS: Weak topic found!")
        for t in weak_topics:
            print(f"- Deck: {t['deck_title']}, Accuracy: {t['accuracy']}%, Reviews: {t['total_reviews']}")
    else:
        print("\nFAILURE: No weak topics found despite 10% accuracy.")

    print("\n--- Cleaning up ---")
    # Clean up can be manual or automated. For now leaving it to inspect DB if needed.
