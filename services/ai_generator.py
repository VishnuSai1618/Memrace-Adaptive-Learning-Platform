import json
from services.gemini_client import call_gemini


class AIGenerator:
    """Service for generating flashcards and quizzes using Google Gemini API.

    All Gemini calls are delegated to `services.gemini_client.call_gemini`,
    which handles multi-key rotation and quota-error retry transparently.
    No API key handling is needed here.
    """

    MODEL = "gemini-2.5-flash"

    # ── Internal Helper ────────────────────────────────────────────────────────

    @staticmethod
    def _clean_json(raw: str) -> str:
        """Strip markdown code-block fences from a Gemini response."""
        text = raw.strip()
        if text.startswith("```"):
            parts = text.split("```")
            # parts[1] is the content between the first pair of fences
            text = parts[1]
            if text.startswith("json"):
                text = text[4:]
        return text.strip()

    # ── Public Methods ─────────────────────────────────────────────────────────

    def generate_flashcards(self, content, num_cards=10):
        """
        Generate flashcards from study content.

        Args:
            content:   Text content to generate flashcards from.
            num_cards: Number of flashcards to generate.

        Returns:
            List of dicts with 'topic' and 'key_point' keys.
        """
        prompt = f"""You are an expert educational content creator. Analyze the following study material and extract the {num_cards} MOST IMPORTANT points that students need to remember.

CRITICAL INSTRUCTIONS:
1. Identify the most critical facts, concepts, definitions, and key information
2. For each important point, create a TOPIC (short phrase) and KEY INFORMATION (the important detail)
3. Focus on what students MUST remember for exams and understanding
4. Make each point clear, concise, and self-contained
5. Avoid trivial details - only include essential information
6. Return ONLY a valid JSON array, no additional text

EXAMPLES OF GOOD FLASHCARDS:
- Topic: "Photosynthesis Definition" → Key Point: "The process by which plants convert light energy into chemical energy (glucose) using carbon dioxide and water, releasing oxygen as a byproduct."
- Topic: "Newton's First Law" → Key Point: "An object at rest stays at rest, and an object in motion stays in motion at constant velocity, unless acted upon by an external force."
- Topic: "Mitochondria Function" → Key Point: "The powerhouse of the cell that produces ATP through cellular respiration, providing energy for cellular processes."

FORMAT (return exactly this structure):
[
  {{"topic": "Short topic/concept name", "key_point": "The important information to remember"}},
  {{"topic": "Another concept", "key_point": "Key fact or definition"}},
  ...
]

STUDY MATERIAL:
{content[:4000]}

Extract the {num_cards} MOST IMPORTANT points as a JSON array:"""

        try:
            response = call_gemini(prompt, model_name=self.MODEL)
            flashcards = json.loads(self._clean_json(response.text))

            if not isinstance(flashcards, list):
                raise ValueError("Response is not a list")
            for card in flashcards:
                if 'topic' not in card or 'key_point' not in card:
                    raise ValueError("Invalid flashcard structure — must have 'topic' and 'key_point' fields")

            return flashcards[:num_cards]

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {e}")
        except Exception as e:
            raise Exception(f"Error generating flashcards: {e}")

    def generate_quiz_questions(self, content, num_questions=5):
        """
        Generate multiple-choice quiz questions from content.

        Args:
            content:       Text content to generate quiz from.
            num_questions: Number of questions to generate.

        Returns:
            List of dicts with question, correct_answer, and option_a/b/c/d.
        """
        prompt = f"""You are an expert quiz creator. Generate {num_questions} multiple-choice questions from the following study material.

INSTRUCTIONS:
1. Create challenging but fair questions
2. Provide 4 options (A, B, C, D) for each question
3. Mark the correct answer clearly
4. Make distractors plausible but incorrect
5. Return ONLY a valid JSON array, no additional text

FORMAT (return exactly this structure):
[
  {{
    "question": "What is...",
    "correct_answer": "The correct answer text",
    "option_a": "First option",
    "option_b": "Second option",
    "option_c": "Third option",
    "option_d": "Fourth option"
  }},
  ...
]

Note: One of the options (A, B, C, or D) must match the correct_answer exactly.

STUDY MATERIAL:
{content[:4000]}

Generate {num_questions} quiz questions as a JSON array:"""

        try:
            response = call_gemini(prompt, model_name=self.MODEL)
            quiz_questions = json.loads(self._clean_json(response.text))

            if not isinstance(quiz_questions, list):
                raise ValueError("Response is not a list")

            required_fields = ['question', 'correct_answer', 'option_a', 'option_b', 'option_c', 'option_d']
            for question in quiz_questions:
                for field in required_fields:
                    if field not in question:
                        raise ValueError(f"Missing field: {field}")

            return quiz_questions[:num_questions]

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {e}")
        except Exception as e:
            raise Exception(f"Error generating quiz questions: {e}")

    def generate_study_summary(self, content, max_length=200):
        """
        Generate a brief summary of study content.

        Args:
            content:    Text content to summarize.
            max_length: Maximum length of summary in words.

        Returns:
            Summary string.
        """
        prompt = f"""Summarize the following study material in {max_length} words or less.
Focus on the main concepts and key points.

STUDY MATERIAL:
{content[:4000]}

Summary:"""

        try:
            response = call_gemini(prompt, model_name=self.MODEL)
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Error generating summary: {e}")

    def generate_personalized_recommendation(self, user_stats, weak_topics):
        """
        Generate personalized study advice based on user performance.

        Args:
            user_stats:  Dict containing user performance metrics.
            weak_topics: List of dicts containing weak topic details.

        Returns:
            String containing personalized recommendation.
        """
        weak_areas_str = "None"
        if weak_topics:
            weak_areas_str = ", ".join(
                [f"{t['deck_title']} (Accuracy: {t['accuracy']}%)" for t in weak_topics[:3]]
            )

        prompt = f"""As an AI study coach, generate a short, personalized, and motivating recommendation for a student based on their recent performance.

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

Recommendation:"""

        try:
            response = call_gemini(prompt, model_name=self.MODEL)
            return response.text.strip()
        except Exception as e:
            import traceback
            print(f"DEBUG: Recommendation error: {e}")
            traceback.print_exc()
            return f"Keep studying! Consistent practice is key to mastery. (Error: {e})"
