from flask import Blueprint, jsonify, session
from services.recommendation import RecommendationEngine
from routes.auth import login_required

recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')

@recommendations_bp.route('/', methods=['GET'])
@login_required
def get_recommendations():
    """Get personalized AI recommendations"""
    try:
        user_id = session['user_id']
        insights = RecommendationEngine.get_ai_insights(user_id)
        
        return jsonify(insights), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
