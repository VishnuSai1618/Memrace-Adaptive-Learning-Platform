from flask import Blueprint, request, jsonify, session
from models import db
from models.flashcard import Flashcard, FlashcardReview
from models.analytics import StudySession
from services.sm2_algorithm import SM2Algorithm
from routes.auth import login_required
from datetime import datetime

flashcards_bp = Blueprint('flashcards', __name__, url_prefix='/api/flashcards')

@flashcards_bp.route('/<int:deck_id>', methods=['GET'])
@login_required
def get_flashcards(deck_id):
    """Get all flashcards for a deck"""
    try:
        flashcards = Flashcard.query.filter_by(deck_id=deck_id).all()
        
        return jsonify({
            'flashcards': [fc.to_dict() for fc in flashcards]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@flashcards_bp.route('/due/<int:deck_id>', methods=['GET'])
@login_required
def get_due_flashcards(deck_id):
    """Get flashcards due for review in a deck"""
    try:
        due_cards = SM2Algorithm.get_due_flashcards(deck_id)
        
        return jsonify({
            'due_flashcards': [fc.to_dict() for fc in due_cards],
            'count': len(due_cards)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@flashcards_bp.route('/create', methods=['POST'])
@login_required
def create_flashcard():
    """Create a new manual flashcard"""
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['deck_id', 'question', 'answer']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        flashcard = Flashcard(
            deck_id=data['deck_id'],
            question=data['question'],
            answer=data['answer']
        )
        db.session.add(flashcard)
        db.session.commit()
        
        return jsonify({'message': 'Flashcard created', 'flashcard': flashcard.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@flashcards_bp.route('/<int:flashcard_id>', methods=['PUT'])
@login_required
def update_flashcard(flashcard_id):
    """Update a flashcard's content"""
    try:
        data = request.get_json()
        flashcard = Flashcard.query.get(flashcard_id)
        if not flashcard:
            return jsonify({'error': 'Flashcard not found'}), 404
            
        flashcard.question = data.get('question', flashcard.question)
        flashcard.answer = data.get('answer', flashcard.answer)
        db.session.commit()
        
        return jsonify({'message': 'Flashcard updated', 'flashcard': flashcard.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@flashcards_bp.route('/<int:flashcard_id>', methods=['DELETE'])
@login_required
def delete_flashcard(flashcard_id):
    """Delete a flashcard"""
    try:
        flashcard = Flashcard.query.get(flashcard_id)
        if not flashcard:
            return jsonify({'error': 'Flashcard not found'}), 404
            
        db.session.delete(flashcard)
        db.session.commit()
        
        return jsonify({'message': 'Flashcard deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@flashcards_bp.route('/review', methods=['POST'])
@login_required
def review_flashcard():
    """Submit a flashcard review and update using SM-2 algorithm"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['flashcard_id', 'correct']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        flashcard_id = data['flashcard_id']
        correct = data['correct']
        response_time_ms = data.get('response_time_ms', 0)
        
        # Get flashcard
        flashcard = Flashcard.query.get(flashcard_id)
        
        if not flashcard:
            return jsonify({'error': 'Flashcard not found'}), 404
        
        # Create review record
        review = FlashcardReview(
            flashcard_id=flashcard_id,
            user_id=session['user_id'],
            correct=correct,
            response_time_ms=response_time_ms
        )
        db.session.add(review)
        
        # Gamification: Update user streak and add XP
        from models.user import User
        user = User.query.get(session['user_id'])
        if user:
            user.update_streak()
            user.add_xp(10)  # Award XP for reviewing a flashcard
        
        # Update flashcard using SM-2 algorithm
        updated_flashcard = SM2Algorithm.process_review(flashcard, correct, response_time_ms)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Review recorded successfully',
            'flashcard': updated_flashcard.to_dict(),
            'next_review': updated_flashcard.next_review.isoformat(),
            'gamification': {
                'xp_earned': 10,
                'total_xp': user.xp if user else 0,
                'level': user.level if user else 1,
                'streak': user.streak if user else 0
            } if user else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@flashcards_bp.route('/session/start', methods=['POST'])
@login_required
def start_study_session():
    """Start a new study session"""
    try:
        data = request.get_json()
        
        if not data or 'deck_id' not in data:
            return jsonify({'error': 'Deck ID required'}), 400
        
        deck_id = data['deck_id']
        
        # Create study session
        study_session = StudySession(
            user_id=session['user_id'],
            deck_id=deck_id
        )
        db.session.add(study_session)
        db.session.commit()
        
        # Store session ID in Flask session
        session['study_session_id'] = study_session.id
        
        return jsonify({
            'message': 'Study session started',
            'session': study_session.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@flashcards_bp.route('/session/end', methods=['POST'])
@login_required
def end_study_session():
    """End the current study session"""
    try:
        if 'study_session_id' not in session:
            return jsonify({'error': 'No active study session'}), 400
        
        study_session = StudySession.query.get(session['study_session_id'])
        
        if not study_session:
            return jsonify({'error': 'Study session not found'}), 404
        
        # Update session with data from request
        data = request.get_json()
        if data:
            study_session.cards_reviewed = data.get('cards_reviewed', study_session.cards_reviewed)
            study_session.correct_count = data.get('correct_count', study_session.correct_count)
            study_session.total_time_ms = data.get('total_time_ms', study_session.total_time_ms)
        
        study_session.end_session()
        db.session.commit()
        
        # Clear session ID
        session.pop('study_session_id', None)
        
        return jsonify({
            'message': 'Study session ended',
            'session': study_session.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@flashcards_bp.route('/<int:flashcard_id>', methods=['GET'])
@login_required
def get_flashcard(flashcard_id):
    """Get a specific flashcard"""
    try:
        flashcard = Flashcard.query.get(flashcard_id)
        
        if not flashcard:
            return jsonify({'error': 'Flashcard not found'}), 404
        
        return jsonify({'flashcard': flashcard.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@flashcards_bp.route('/upcoming-reviews', methods=['GET'])
@login_required
def get_upcoming_reviews():
    """Get upcoming review schedule for the user"""
    try:
        days = request.args.get('days', 7, type=int)
        user_id = session['user_id']
        
        review_schedule = SM2Algorithm.get_upcoming_reviews(user_id, days)
        
        return jsonify({
            'review_schedule': review_schedule,
            'total_upcoming': sum(review_schedule.values())
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
