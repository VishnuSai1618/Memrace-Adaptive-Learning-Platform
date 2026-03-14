from flask import Blueprint, request, jsonify, session
from models import db
from models.deck import Deck
from models.flashcard import Flashcard
from models.quiz import Quiz
from services.pdf_extractor import PDFExtractor
from services.ai_generator import AIGenerator
from routes.auth import login_required

content_bp = Blueprint('content', __name__, url_prefix='/api/content')

@content_bp.route('/create-deck', methods=['POST'])
@login_required
def create_deck():
    """Create a completely manual empty deck"""
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
            
        title = data['title'].strip()
        description = data.get('description', '')
        
        if not title:
            return jsonify({'error': 'Title cannot be empty'}), 400
            
        # Create deck
        deck = Deck(
            user_id=user_id,
            title=title,
            description=description,
            source_type='manual',
            original_content=''
        )
        db.session.add(deck)
        db.session.commit()
        
        return jsonify({
            'message': 'Deck created successfully',
            'deck': deck.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@content_bp.route('/upload', methods=['POST'])
@login_required
def upload_content():
    """Upload PDF or text content and create a deck"""
    try:
        user_id = session['user_id']
        
        # Check if it's a file upload or text paste
        if 'file' in request.files:
            # PDF upload
            file = request.files['file']
            title = request.form.get('title', 'Untitled Deck')
            description = request.form.get('description', '')
            
            # Process PDF
            file_path, extracted_text = PDFExtractor.process_pdf_upload(file)
            
            # Create deck
            deck = Deck(
                user_id=user_id,
                title=title,
                description=description,
                source_type='pdf',
                original_content=extracted_text
            )
            db.session.add(deck)
            db.session.commit()
            
            return jsonify({
                'message': 'PDF uploaded successfully',
                'deck': deck.to_dict(),
                'content_preview': extracted_text[:200] + '...'
            }), 201
            
        else:
            # Text paste
            data = request.get_json()
            
            if not data or 'content' not in data:
                return jsonify({'error': 'No content provided'}), 400
            
            content = data['content'].strip()
            title = data.get('title', 'Untitled Deck')
            description = data.get('description', '')
            
            if not content:
                return jsonify({'error': 'Content cannot be empty'}), 400
            
            # Create deck
            deck = Deck(
                user_id=user_id,
                title=title,
                description=description,
                source_type='text',
                original_content=content
            )
            db.session.add(deck)
            db.session.commit()
            
            return jsonify({
                'message': 'Content saved successfully',
                'deck': deck.to_dict()
            }), 201
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@content_bp.route('/generate-flashcards', methods=['POST'])
@login_required
def generate_flashcards():
    """Generate flashcards from deck content using AI"""
    try:
        data = request.get_json()
        
        if not data or 'deck_id' not in data:
            return jsonify({'error': 'Deck ID required'}), 400
        
        deck_id = data['deck_id']
        num_cards = data.get('num_cards', 10)
        
        # Get deck
        deck = Deck.query.get(deck_id)
        
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404
        
        # Verify ownership
        if deck.user_id != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Generate flashcards using AI
        ai_generator = AIGenerator()
        flashcards_data = ai_generator.generate_flashcards(deck.original_content, num_cards)
        
        # Save flashcards to database
        created_flashcards = []
        for card_data in flashcards_data:
            flashcard = Flashcard(
                deck_id=deck_id,
                question=card_data['topic'],  # Store topic in question field
                answer=card_data['key_point']  # Store key_point in answer field
            )
            db.session.add(flashcard)
            created_flashcards.append(flashcard)
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(created_flashcards)} flashcards generated successfully',
            'flashcards': [fc.to_dict() for fc in created_flashcards]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@content_bp.route('/generate-quiz', methods=['POST'])
@login_required
def generate_quiz():
    """Generate quiz questions from deck content using AI"""
    try:
        data = request.get_json()
        
        if not data or 'deck_id' not in data:
            return jsonify({'error': 'Deck ID required'}), 400
        
        deck_id = data['deck_id']
        num_questions = data.get('num_questions', 5)
        
        # Get deck
        deck = Deck.query.get(deck_id)
        
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404
        
        # Verify ownership
        if deck.user_id != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Generate quiz using AI
        ai_generator = AIGenerator()
        quiz_data = ai_generator.generate_quiz_questions(deck.original_content, num_questions)
        
        # Save quiz questions to database
        created_quizzes = []
        for q_data in quiz_data:
            quiz = Quiz(
                deck_id=deck_id,
                question=q_data['question'],
                correct_answer=q_data['correct_answer'],
                option_a=q_data['option_a'],
                option_b=q_data['option_b'],
                option_c=q_data['option_c'],
                option_d=q_data['option_d']
            )
            db.session.add(quiz)
            created_quizzes.append(quiz)
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(created_quizzes)} quiz questions generated successfully',
            'quizzes': [q.to_dict() for q in created_quizzes]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@content_bp.route('/decks', methods=['GET'])
@login_required
def get_user_decks():
    """Get all decks for the current user"""
    try:
        user_id = session['user_id']
        decks = Deck.query.filter_by(user_id=user_id).order_by(Deck.created_at.desc()).all()
        
        return jsonify({
            'decks': [deck.to_dict() for deck in decks]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/decks/<int:deck_id>', methods=['GET'])
@login_required
def get_deck(deck_id):
    """Get a specific deck with its flashcards and quizzes"""
    try:
        deck = Deck.query.get(deck_id)
        
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404
        
        # Verify ownership or public access
        if deck.user_id != session['user_id'] and not deck.is_public:
            return jsonify({'error': 'Unauthorized'}), 403
        
        deck_data = deck.to_dict()
        deck_data['flashcards'] = [fc.to_dict() for fc in deck.flashcards]
        deck_data['quizzes'] = [q.to_dict() for q in deck.quizzes]
        
        return jsonify({'deck': deck_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/decks/<int:deck_id>', methods=['DELETE'])
@login_required
def delete_deck(deck_id):
    """Delete a deck and all its content"""
    try:
        deck = Deck.query.get(deck_id)
        
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404
        
        # Verify ownership
        if deck.user_id != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(deck)
        db.session.commit()
        
        return jsonify({'message': 'Deck deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
