from datetime import datetime, timedelta
from sqlalchemy import func, case, desc
from models import db
from models.flashcard import Flashcard, FlashcardReview
from models.quiz import QuizAttempt, Quiz
from models.deck import Deck

class RecommendationEngine:
    """Generate personalized study recommendations based on user performance"""
    
    @staticmethod
    def get_weak_topics(user_id, threshold=0.6):
        """
        Identify decks/topics where user performance is below threshold
        
        Args:
            user_id: ID of the user
            threshold: Accuracy threshold (0.0 to 1.0)
            
        Returns:
            List of dictionaries with deck info and performance metrics
        """
        try:
            # Stats per deck from Flashcard Reviews
            fc_stats = db.session.query(
                Deck.id, 
                Deck.title,
                func.count(FlashcardReview.id).label('total'),
                func.sum(case((FlashcardReview.correct == True, 1), else_=0)).label('correct')
            ).select_from(FlashcardReview)\
            .join(Flashcard, FlashcardReview.flashcard_id == Flashcard.id)\
            .join(Deck, Flashcard.deck_id == Deck.id)\
            .filter(FlashcardReview.user_id == user_id)\
            .group_by(Deck.id, Deck.title).all()

            # Stats per deck from Quiz Attempts
            quiz_stats = db.session.query(
                Deck.id,
                Deck.title,
                func.count(QuizAttempt.id).label('total'),
                func.sum(case((QuizAttempt.correct == True, 1), else_=0)).label('correct')
            ).select_from(QuizAttempt)\
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id)\
            .join(Deck, Quiz.deck_id == Deck.id)\
            .filter(QuizAttempt.user_id == user_id)\
            .group_by(Deck.id, Deck.title).all()

            # Merge stats
            deck_performance = {}

            for deck_id, title, total, correct in fc_stats:
                deck_performance[deck_id] = {
                    'deck_id': deck_id,
                    'deck_title': title,
                    'total_reviews': total,
                    'correct_reviews': correct or 0
                }

            for deck_id, title, total, correct in quiz_stats:
                if deck_id not in deck_performance:
                    deck_performance[deck_id] = {
                        'deck_id': deck_id,
                        'deck_title': title,
                        'total_reviews': 0,
                        'correct_reviews': 0
                    }
                
                deck_performance[deck_id]['total_reviews'] += total
                deck_performance[deck_id]['correct_reviews'] += (correct or 0)

            # Filter weak topics
            weak_topics = []
            for stats in deck_performance.values():
                if stats['total_reviews'] > 0:
                    accuracy = stats['correct_reviews'] / stats['total_reviews']
                    stats['accuracy'] = round(accuracy * 100, 2)
                    
                    if accuracy < threshold:
                        weak_topics.append(stats)
            
            # Sort by accuracy (lowest first)
            weak_topics.sort(key=lambda x: x['accuracy'])
            
            return weak_topics

        except Exception as e:
            print(f"Error calculating weak topics: {e}")
            return []
    
    @staticmethod
    def get_study_recommendations(user_id):
        """
        Generate comprehensive study recommendations
        """
        try:
            recommendations = {
                'weak_topics': [],
                'due_reviews': 0,
                'suggested_focus': None,
                'study_streak': 0,
                'total_cards_mastered': 0
            }
            
            # Get weak topics
            recommendations['weak_topics'] = RecommendationEngine.get_weak_topics(user_id)
            
            # Count due reviews
            # Note: This checks ALL decks for which the user is the owner, as per SM-2 Model design
            # For public decks, we'd need a separate user_progress table.
            from services.sm2_algorithm import SM2Algorithm
            
            # Handle decks owned by user
            owned_decks = Deck.query.filter_by(user_id=user_id).all()
            due_count = 0
            
            for deck in owned_decks:
                # Safely get due cards
                try:
                    due_cards = SM2Algorithm.get_due_flashcards(deck.id)
                    due_count += len(due_cards)
                except:
                    continue
            
            recommendations['due_reviews'] = due_count
            
            # Suggest focus area
            if recommendations['weak_topics']:
                recommendations['suggested_focus'] = recommendations['weak_topics'][0]['deck_title']
            elif due_count > 0:
                recommendations['suggested_focus'] = "Complete your due reviews"
            else:
                recommendations['suggested_focus'] = "Create new flashcards or explore public decks"
            
            # Calculate mastered cards (repetitions >= 3)
            # Only for owned decks due to schema limitations
            mastered_count = db.session.query(Flashcard).join(Deck).filter(
                Deck.user_id == user_id,
                Flashcard.repetitions >= 3
            ).count()
            
            recommendations['total_cards_mastered'] = mastered_count

            # Compute tiered mastery rank from mastered count
            recommendations['mastery_rank'] = RecommendationEngine._mastery_tier(mastered_count)

            return recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            # Return safe default
            return {
                'weak_topics': [],
                'due_reviews': 0,
                'suggested_focus': "Start Studying",
                'study_streak': 0,
                'total_cards_mastered': 0,
                'mastery_rank': 'Beginner'
            }
    
    @staticmethod
    def _mastery_tier(count):
        """Map mastered-card count to a tiered rank label."""
        if count > 100:
            return 'Master'
        elif count > 50:
            return 'Expert'
        elif count > 20:
            return 'Scholar'
        elif count > 5:
            return 'Learner'
        return 'Beginner'

    @staticmethod
    def get_performance_analytics(user_id, days=30):
        """
        Get detailed performance analytics for a user
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            analytics = {
                'total_reviews': 0,
                'correct_reviews': 0,
                'accuracy': 0,
                'average_response_time': 0,
                'daily_activity': {},
                'deck_performance': []
            }
            
            # Get all reviews in time period
            reviews = FlashcardReview.query.filter(
                FlashcardReview.user_id == user_id,
                FlashcardReview.reviewed_at >= start_date
            ).all()
            
            if reviews:
                analytics['total_reviews'] = len(reviews)
                analytics['correct_reviews'] = sum(1 for r in reviews if r.correct)
                if analytics['total_reviews'] > 0:
                    analytics['accuracy'] = round((analytics['correct_reviews'] / analytics['total_reviews']) * 100, 2)
                
                # Calculate average response time
                response_times = [r.response_time_ms for r in reviews if r.response_time_ms]
                if response_times:
                    analytics['average_response_time'] = round(sum(response_times) / len(response_times))
                
                # Group by day
                for review in reviews:
                    date_key = review.reviewed_at.date().isoformat()
                    if date_key not in analytics['daily_activity']:
                        analytics['daily_activity'][date_key] = {'total': 0, 'correct': 0}
                    
                    analytics['daily_activity'][date_key]['total'] += 1
                    if review.correct:
                        analytics['daily_activity'][date_key]['correct'] += 1
            
            # Get performance by deck (Reuse weak topics logic but without threshold)
            # This is cleaner than looping decks
            deck_stats = RecommendationEngine.get_weak_topics(user_id, threshold=2.0) # 2.0 ensures we get ALL decks
            
            analytics['deck_performance'] = deck_stats
            
            return analytics
            
        except Exception as e:
            print(f"Error generating analytics: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def get_ai_insights(user_id):
        """
        Get AI-powered study insights
        """
        from services.ai_generator import AIGenerator
        
        try:
            # Get user stats
            analytics = RecommendationEngine.get_performance_analytics(user_id, days=14)
            weak_topics = RecommendationEngine.get_weak_topics(user_id)
            
            # Generate recommendation
            ai_generator = AIGenerator()
            recommendation = ai_generator.generate_personalized_recommendation(analytics, weak_topics)
            
        except Exception as e:
            recommendation = "Our AI coach is taking a coffee break. Keep reviewing your due cards!"
            print(f"AI Recommendation Error: {e}")
            weak_topics = []
            analytics = {'accuracy': 0}
            
        return {
            'recommendation': recommendation,
            'weak_areas_count': len(weak_topics),
            'weak_topics': weak_topics,
            'accuracy': analytics.get('accuracy', 0)
        }
