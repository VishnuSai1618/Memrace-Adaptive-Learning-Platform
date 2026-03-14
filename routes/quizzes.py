from flask import Blueprint, request, jsonify, session, render_template
from models import db
from models.quiz import Quiz, QuizAttempt
from routes.auth import login_required

quizzes_bp = Blueprint('quizzes', __name__, url_prefix='/api/quizzes')

@quizzes_bp.route('/deck/<int:deck_id>', methods=['GET'])
def get_quizzes(deck_id):
    """Get all quiz questions for a deck"""
    try:
        # Manual session check instead of @login_required so AJAX calls get JSON, not a redirect
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        quizzes = Quiz.query.filter_by(deck_id=deck_id).all()
        
        return jsonify({
            'quizzes': [q.to_dict() for q in quizzes]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/create', methods=['POST'])
@login_required
def create_quiz():
    """Create a new manual quiz question"""
    try:
        data = request.get_json()
        required_fields = ['deck_id', 'question', 'correct_answer', 'option_a', 'option_b', 'option_c', 'option_d']
        if not data or not all(k in data for k in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        quiz = Quiz(
            deck_id=data['deck_id'],
            question=data['question'],
            correct_answer=data['correct_answer'],
            option_a=data['option_a'],
            option_b=data['option_b'],
            option_c=data['option_c'],
            option_d=data['option_d']
        )
        db.session.add(quiz)
        db.session.commit()
        
        return jsonify({'message': 'Quiz created', 'quiz': quiz.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/<int:quiz_id>', methods=['PUT'])
@login_required
def update_quiz(quiz_id):
    """Update a quiz question's content"""
    try:
        data = request.get_json()
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
            
        quiz.question = data.get('question', quiz.question)
        quiz.correct_answer = data.get('correct_answer', quiz.correct_answer)
        quiz.option_a = data.get('option_a', quiz.option_a)
        quiz.option_b = data.get('option_b', quiz.option_b)
        quiz.option_c = data.get('option_c', quiz.option_c)
        quiz.option_d = data.get('option_d', quiz.option_d)
        
        db.session.commit()
        
        return jsonify({'message': 'Quiz updated', 'quiz': quiz.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/<int:quiz_id>', methods=['DELETE'])
@login_required
def delete_quiz(quiz_id):
    """Delete a quiz question"""
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
            
        db.session.delete(quiz)
        db.session.commit()
        
        return jsonify({'message': 'Quiz deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/submit', methods=['POST'])
@login_required
def submit_quiz_answer():
    """Submit an answer to a quiz question"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['quiz_id', 'selected_answer']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        quiz_id = data['quiz_id']
        selected_answer = data['selected_answer']
        time_taken_ms = data.get('time_taken_ms', 0)
        
        # Get quiz
        quiz = Quiz.query.get(quiz_id)
        
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        
        # Check if answer is correct
        correct = (selected_answer == quiz.correct_answer)
        
        # Create quiz attempt record
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            user_id=session['user_id'],
            selected_answer=selected_answer,
            correct=correct,
            time_taken_ms=time_taken_ms
        )
        db.session.add(attempt)
        
        # Gamification: Update user streak and add XP
        from models.user import User
        user = User.query.get(session['user_id'])
        xp_earned = 0
        if user:
            user.update_streak()
            if correct:
                xp_earned = 20
                user.add_xp(xp_earned)  # Higher XP reward for quizzes
                
        db.session.commit()
        
        return jsonify({
            'message': 'Answer submitted',
            'correct': correct,
            'correct_answer': quiz.correct_answer,
            'attempt': attempt.to_dict(),
            'gamification': {
                'xp_earned': xp_earned,
                'total_xp': user.xp if user else 0,
                'level': user.level if user else 1,
                'streak': user.streak if user else 0
            } if user else None
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@quizzes_bp.route('/results/<int:deck_id>', methods=['GET'])
@login_required
def get_quiz_results(deck_id):
    """Get quiz results for a deck"""
    try:
        user_id = session['user_id']
        
        # Get all quizzes for the deck
        quizzes = Quiz.query.filter_by(deck_id=deck_id).all()
        quiz_ids = [q.id for q in quizzes]
        
        # Get user's attempts
        attempts = QuizAttempt.query.filter(
            QuizAttempt.user_id == user_id,
            QuizAttempt.quiz_id.in_(quiz_ids)
        ).all()
        
        if not attempts:
            return jsonify({
                'total_attempts': 0,
                'correct_count': 0,
                'accuracy': 0
            }), 200
        
        correct_count = sum(1 for a in attempts if a.correct)
        total_attempts = len(attempts)
        accuracy = (correct_count / total_attempts) * 100 if total_attempts > 0 else 0
        
        return jsonify({
            'total_attempts': total_attempts,
            'correct_count': correct_count,
            'accuracy': round(accuracy, 2),
            'attempts': [a.to_dict() for a in attempts]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

