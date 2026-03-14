from flask import Blueprint, request, jsonify, session
from services.recommendation import RecommendationEngine
from routes.auth import login_required

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/performance', methods=['GET'])
@login_required
def get_performance():
    """Get user performance analytics"""
    try:
        user_id = session['user_id']
        days = request.args.get('days', 30, type=int)
        
        analytics = RecommendationEngine.get_performance_analytics(user_id, days)
        
        return jsonify({'analytics': analytics}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/recommendations', methods=['GET'])
@login_required
def get_recommendations():
    """Get personalized study recommendations"""
    try:
        user_id = session['user_id']
        
        recommendations = RecommendationEngine.get_study_recommendations(user_id)
        
        return jsonify({'recommendations': recommendations}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/weak-topics', methods=['GET'])
@login_required
def get_weak_topics():
    """Get topics where user performance is weak"""
    try:
        user_id = session['user_id']
        threshold = request.args.get('threshold', 0.6, type=float)
        
        weak_topics = RecommendationEngine.get_weak_topics(user_id, threshold)
        
        return jsonify({'weak_topics': weak_topics}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
