from flask import Blueprint, jsonify, session
from datetime import datetime, timedelta
from services.recommendation import RecommendationEngine
from models import db
from models.analytics import AIInsight
from routes.auth import login_required

recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')

COOLDOWN_MINUTES = 5

@recommendations_bp.route('/', methods=['GET'])
@login_required
def get_latest_insight():
    """Get the most recent cached AI insight for the current user (no API call)"""
    try:
        user_id = session['user_id']
        
        latest = AIInsight.query.filter_by(user_id=user_id)\
            .order_by(AIInsight.generated_at.desc()).first()
        
        if latest:
            return jsonify({
                'recommendation': latest.content,
                'weak_areas_count': latest.weak_areas_count,
                'accuracy': latest.accuracy,
                'generated_at': latest.generated_at.isoformat(),
                'cached': True
            }), 200
        else:
            return jsonify({
                'recommendation': None,
                'cached': True,
                'message': 'No insights generated yet. Click "Generate Insights" to get your first AI coaching!'
            }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recommendations_bp.route('/generate', methods=['POST'])
@login_required
def generate_insight():
    """Generate a new AI insight (with cooldown enforcement)"""
    try:
        user_id = session['user_id']
        
        # Check cooldown
        latest = AIInsight.query.filter_by(user_id=user_id)\
            .order_by(AIInsight.generated_at.desc()).first()
        
        if latest:
            elapsed = datetime.utcnow() - latest.generated_at
            if elapsed < timedelta(minutes=COOLDOWN_MINUTES):
                remaining = COOLDOWN_MINUTES - int(elapsed.total_seconds() / 60)
                return jsonify({
                    'error': f'Please wait {remaining} more minute(s) before generating new insights.',
                    'cooldown': True,
                    'retry_after_seconds': int((timedelta(minutes=COOLDOWN_MINUTES) - elapsed).total_seconds())
                }), 429
        
        # Call the AI API
        insights = RecommendationEngine.get_ai_insights(user_id)
        
        # Save to database
        new_insight = AIInsight(
            user_id=user_id,
            content=insights.get('recommendation', ''),
            weak_areas_count=insights.get('weak_areas_count', 0),
            accuracy=insights.get('accuracy', 0.0)
        )
        db.session.add(new_insight)
        db.session.commit()
        
        return jsonify({
            'recommendation': new_insight.content,
            'weak_areas_count': new_insight.weak_areas_count,
            'accuracy': new_insight.accuracy,
            'generated_at': new_insight.generated_at.isoformat(),
            'cached': False
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
