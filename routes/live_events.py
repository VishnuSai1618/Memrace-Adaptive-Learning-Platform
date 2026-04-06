from flask import request
from flask_socketio import emit, join_room, leave_room
from models import db
from models.live_quiz import LiveSession, LiveParticipant, LiveAnswer
from models.quiz import Quiz
import random
import string


def generate_pin():
    """Generate a unique 6-character alphanumeric PIN"""
    while True:
        pin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not LiveSession.query.filter_by(pin=pin, status='waiting').first():
            return pin


def register_events(socketio):
    """Call this once after creating SocketIO to register all live-quiz event handlers."""

    @socketio.on('host_create_session')
    def handle_create_session(data):
        """Host creates a new Live Session for a deck"""
        try:
            host_id = data.get('host_id')
            deck_id = data.get('deck_id')

            pin = generate_pin()
            session = LiveSession(host_id=host_id, deck_id=deck_id, pin=pin, status='waiting')
            db.session.add(session)
            db.session.commit()

            # Host needs to join both its private host room and the broadcast session room
            join_room(f"host_{session.id}")
            join_room(f"session_{session.id}")

            emit('session_created', {'session_id': session.id, 'pin': pin})
        except Exception as e:
            print(f"Error in host_create_session: {e}")

    @socketio.on('player_join')
    def handle_player_join(data):
        """A participant joins a Live Session via PIN (Initial Join)"""
        try:
            pin = data.get('pin')
            display_name = data.get('display_name')
            user_id = data.get('user_id')  # Can be null

            session = LiveSession.query.filter_by(pin=pin, status='waiting').first()
            if not session:
                emit('join_error', {'message': 'Invalid PIN or session already started'})
                return

            participant = LiveParticipant(session_id=session.id, user_id=user_id, display_name=display_name)
            db.session.add(participant)
            db.session.commit()

            # We don't join the room here because the client immediately redirects to /live/player
            # and will connect again. We'll join the room in player_rejoin.

            # Notify player they joined
            emit('join_success', {'participant_id': participant.id, 'session_id': session.id, 'deck_id': session.deck_id})

            # Notify host that a player joined
            emit('player_joined', {'participant': participant.to_dict()}, room=f"host_{session.id}")
        except Exception as e:
            print(f"Error in player_join: {e}")

    @socketio.on('player_rejoin')
    def handle_player_rejoin(data):
        """A participant's interactive screen connects and joins the Socket.io room.
        If the quiz is already active, immediately send them the current question state."""
        try:
            session_id = data.get('session_id')
            participant_id = data.get('participant_id')
            if session_id:
                session_id = int(session_id)
                join_room(f"session_{session_id}")
                emit('rejoin_success', {'status': 'connected'})

                # --- Reconnect state sync ---
                # If the quiz is already active, send the current question immediately
                # so late-joiners are not stuck on the "Waiting" screen.
                live_session = LiveSession.query.get(session_id)
                if live_session and live_session.status == 'active' and live_session.current_question_index is not None:
                    from models.deck import Deck
                    deck = Deck.query.get(live_session.deck_id)
                    if deck:
                        quizzes = Quiz.query.filter_by(deck_id=deck.id).all()
                        idx = live_session.current_question_index
                        if 0 <= idx < len(quizzes):
                            q = quizzes[idx]
                            emit('new_question', {'question': q.to_dict(), 'index': idx})
                            print(f"Reconnect sync: sent question {idx} to participant {participant_id}")
        except Exception as e:
            print(f"Error in player_rejoin: {e}")

    @socketio.on('host_start_quiz')
    def handle_start_quiz(data):
        """Host starts the quiz, moving to the first question"""
        try:
            session_id = int(data.get('session_id'))
            session = LiveSession.query.get(session_id)

            if session:
                session.status = 'active'
                session.current_question_index = 0
                db.session.commit()

                emit('quiz_started', {}, room=f"session_{session_id}")
        except Exception as e:
            print(f"Error in host_start_quiz: {e}")

    @socketio.on('host_show_question')
    def handle_show_question(data):
        """Host broadcasts a question to all joined participants"""
        try:
            session_id = int(data.get('session_id'))
            question_data = data.get('question')
            question_index = data.get('question_index')

            session = LiveSession.query.get(session_id)
            if session:
                session.current_question_index = int(question_index)
                db.session.commit()

                emit('new_question', {'question': question_data, 'index': question_index}, room=f"session_{session_id}")
        except Exception as e:
            print(f"Error in host_show_question: {e}")

    @socketio.on('player_submit_answer')
    def handle_submit_answer(data):
        """Participant submits an answer to the current question"""
        try:
            participant_id = int(data.get('participant_id'))
            session_id = int(data.get('session_id'))
            quiz_id = int(data.get('quiz_id'))
            selected_answer = data.get('selected_answer')
            time_taken_ms = int(data.get('time_taken_ms', 0))

            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                print(f"Quiz {quiz_id} not found.")
                return

            # Prevent duplicate submissions
            existing_answer = LiveAnswer.query.filter_by(
                participant_id=participant_id,
                quiz_id=quiz_id
            ).first()

            if existing_answer:
                print(f"Duplicate answer attempt by participant {participant_id} for quiz {quiz_id}")
                return

            is_correct = (selected_answer == quiz.correct_answer)

            score_awarded = 0
            if is_correct:
                base_score = 500
                time_bonus = max(0, 500 - int((time_taken_ms / 30000) * 500))
                score_awarded = base_score + time_bonus

            print(f"Server validated answer: {selected_answer} (correct: {is_correct}), score: {score_awarded}")

            answer = LiveAnswer(
                participant_id=participant_id,
                quiz_id=quiz_id,
                selected_answer=selected_answer,
                is_correct=is_correct,
                time_taken_ms=time_taken_ms,
                score_awarded=score_awarded
            )

            participant = LiveParticipant.query.get(participant_id)
            if participant:
                participant.score += score_awarded

            db.session.add(answer)
            db.session.commit()

            emit('answer_received', {
                'participant_id': participant_id,
                'is_correct': is_correct
            }, room=f"host_{session_id}")
        except Exception as e:
            print(f"Error in player_submit_answer: {e}")
            db.session.rollback()

    @socketio.on('host_show_results')
    def handle_show_results(data):
        """Host ends the timer and broadcasts results/leaderboard for the current question"""
        try:
            session_id = int(data.get('session_id'))
            quiz_id = int(data.get('quiz_id'))

            quiz = Quiz.query.get(quiz_id)

            participants = LiveParticipant.query.filter_by(session_id=session_id).order_by(LiveParticipant.score.desc()).limit(5).all()
            leaderboard = [{'display_name': p.display_name, 'score': p.score} for p in participants]

            emit('question_results', {
                'correct_answer': quiz.correct_answer if quiz else '',
                'leaderboard': leaderboard
            }, room=f"session_{session_id}")
        except Exception as e:
            print(f"Error in host_show_results: {e}")

    @socketio.on('host_end_session')
    def handle_end_session(data):
        """Host ends the entire session"""
        try:
            session_id = int(data.get('session_id'))
            session = LiveSession.query.get(session_id)

            if session:
                session.status = 'finished'
                db.session.commit()

                participants = LiveParticipant.query.filter_by(session_id=session_id).order_by(LiveParticipant.score.desc()).limit(10).all()
                leaderboard = [{'display_name': p.display_name, 'score': p.score} for p in participants]

                emit('session_finished', {'leaderboard': leaderboard}, room=f"session_{session_id}")
        except Exception as e:
            print(f"Error in host_end_session: {e}")
