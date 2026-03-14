
    def generate_personalized_recommendation(self, user_stats, weak_topics):
        """
        Generate personalized study advice based on user performance
        
        Args:
            user_stats: Dictionary containing user performance metrics
            weak_topics: List of dictionaries containing weak topic details
            
        Returns:
            String containing personalized recommendation
        """
        try:
            # Format weak topics for prompt
            weak_areas_str = "None"
            if weak_topics:
                weak_areas_str = ", ".join([f"{t['deck_title']} (Accuracy: {t['accuracy']}%)" for t in weak_topics[:3]])
            
            prompt = f"""
As an AI study coach, generate a short, personalized, and motivating recommendation for a student based on their recent performance.

Student Stats:
- Overall Accuracy: {user_stats.get('accuracy', 0)}%
- Total Reviews: {user_stats.get('total_reviews', 0)}
- Weak Areas: {weak_areas_str}

Instructions:
1. Be encouraging but honest about areas for improvement.
2. If they have weak areas, specifically mention them and suggest a strategy (e.g., "focus on...").
3. If accuracy is high, challenge them to maintain it or try harder subjects.
4. Keep it under 50 words.
5. Address the student directly ("You...").

Recommendation:
"""
            
            response = self.model.generate_content(prompt)
            recommendation = response.text.strip()
            
            return recommendation
            
        except Exception as e:
            print(f"Error generating recommendation: {e}")
            return "Keep studying! consistent practice is key to mastery."
