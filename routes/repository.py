from flask import Blueprint, request, jsonify, session
from models import db
from models.deck import Deck
from models.flashcard import Flashcard
from models.analytics import PublicDeck
from routes.auth import login_required

repository_bp = Blueprint('repository', __name__, url_prefix='/api/repository')

@repository_bp.route('/', methods=['GET'])
def browse_public_decks():
    """Browse all public decks"""
    try:
        public_decks = PublicDeck.query.order_by(PublicDeck.published_at.desc()).all()
        
        return jsonify({
            'public_decks': [pd.to_dict() for pd in public_decks]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@repository_bp.route('/publish', methods=['POST'])
@login_required
def publish_deck():
    """Publish a deck to the public repository"""
    try:
        data = request.get_json()
        
        if not data or 'deck_id' not in data:
            return jsonify({'error': 'Deck ID required'}), 400
        
        deck_id = data['deck_id']
        
        # Get deck
        deck = Deck.query.get(deck_id)
        
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404
        
        # Verify ownership
        if deck.user_id != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if already published
        existing_public = PublicDeck.query.filter_by(deck_id=deck_id).first()
        if existing_public:
            return jsonify({'error': 'Deck already published'}), 409
        
        # Mark deck as public
        deck.is_public = True
        
        # Create public deck entry
        public_deck = PublicDeck(
            deck_id=deck_id,
            author_id=session['user_id']
        )
        db.session.add(public_deck)
        db.session.commit()
        
        return jsonify({
            'message': 'Deck published successfully',
            'public_deck': public_deck.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@repository_bp.route('/clone/<int:deck_id>', methods=['POST'])
@login_required
def clone_deck(deck_id):
    """Clone a public deck to user's library"""
    try:
        # Get original deck
        original_deck = Deck.query.get(deck_id)
        
        if not original_deck:
            return jsonify({'error': 'Deck not found'}), 404
        
        if not original_deck.is_public:
            return jsonify({'error': 'Deck is not public'}), 403
        
        # Create cloned deck
        cloned_deck = Deck(
            user_id=session['user_id'],
            title=f"{original_deck.title} (Cloned)",
            description=original_deck.description,
            source_type=original_deck.source_type,
            original_content=original_deck.original_content,
            is_public=False
        )
        db.session.add(cloned_deck)
        db.session.flush()  # Get the new deck ID
        
        # Clone flashcards
        for original_fc in original_deck.flashcards:
            cloned_fc = Flashcard(
                deck_id=cloned_deck.id,
                question=original_fc.question,
                answer=original_fc.answer
            )
            db.session.add(cloned_fc)
        
        # Increment clone count
        public_deck = PublicDeck.query.filter_by(deck_id=deck_id).first()
        if public_deck:
            public_deck.increment_clone_count()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Deck cloned successfully',
            'deck': cloned_deck.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@repository_bp.route('/unpublish/<int:deck_id>', methods=['POST'])
@login_required
def unpublish_deck(deck_id):
    """Remove a deck from public repository"""
    try:
        # Get deck
        deck = Deck.query.get(deck_id)
        
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404
        
        # Verify ownership
        if deck.user_id != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Remove from public repository
        public_deck = PublicDeck.query.filter_by(deck_id=deck_id).first()
        
        if not public_deck:
            return jsonify({'error': 'Deck is not published'}), 404
        
        deck.is_public = False
        db.session.delete(public_deck)
        db.session.commit()
        
        return jsonify({'message': 'Deck unpublished successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
