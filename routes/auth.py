from flask import Blueprint, request, jsonify, session, current_app, url_for
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from models import db
from models.user import User
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Validate input
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        # Log user in
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        
        return jsonify({
            'message': 'User created successfully',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and create session"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({'error': 'Missing email or password'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login
        user.update_last_login()
        
        # Create session
        session['user_id'] = user.id
        session['username'] = user.username
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """End user session"""
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@auth_bp.route('/user', methods=['GET'])
@login_required
def get_current_user():
    """Get current logged-in user info"""
    try:
        user = User.query.get(session['user_id'])
        
        if not user:
            session.clear()
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        return jsonify({'authenticated': True, 'user_id': session['user_id']}), 200
    return jsonify({'authenticated': False}), 200


# ── Password Reset helpers ────────────────────────────────────────────────────

def _make_serializer():
    """Create a URLSafeTimedSerializer using the app's SECRET_KEY."""
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


def _generate_reset_token(user: User) -> str:
    """Generate a signed, time-limited token for this user.

    Uses a fixed salt for signing so loads() can always decode it.
    A short fingerprint of the password_hash is embedded in the payload —
    once the password changes the fingerprint won't match, making old tokens
    automatically invalid (one-time-use guarantee without a DB table).
    """
    import hashlib
    pw_fingerprint = hashlib.sha256(user.password_hash.encode()).hexdigest()[:16]
    s = _make_serializer()
    return s.dumps(
        {'email': user.email, 'pwf': pw_fingerprint},
        salt='memrace-password-reset'
    )


def _verify_reset_token(token: str, max_age_seconds: int = 1800):
    """
    Verify a reset token.

    Returns (user, None) on success.
    Returns (None, 'expired') or (None, 'invalid') on failure.
    max_age_seconds defaults to 30 minutes.
    """
    import hashlib
    s = _make_serializer()

    # Step 1: Load and verify signature + expiry using the fixed salt
    try:
        data = s.loads(token, max_age=max_age_seconds, salt='memrace-password-reset')
    except SignatureExpired:
        current_app.logger.warning('Password reset token expired')
        return None, 'expired'
    except BadSignature as exc:
        current_app.logger.warning(f'Password reset token bad signature: {exc}')
        return None, 'invalid'
    except Exception as exc:
        current_app.logger.warning(f'Password reset token error: {exc}')
        return None, 'invalid'

    # Step 2: Look up the user by email from the payload
    email = data.get('email')
    pw_fingerprint = data.get('pwf')
    if not email or not pw_fingerprint:
        return None, 'invalid'

    user = User.query.filter_by(email=email).first()
    if not user:
        return None, 'invalid'

    # Step 3: Compare fingerprint — if password has changed the token is spent
    current_fingerprint = hashlib.sha256(user.password_hash.encode()).hexdigest()[:16]
    if pw_fingerprint != current_fingerprint:
        current_app.logger.warning(f'Password reset token fingerprint mismatch for {email}')
        return None, 'invalid'

    return user, None


# ── Routes ────────────────────────────────────────────────────────────────────

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Request a password-reset email.
    Always returns a generic success response to prevent email enumeration.
    """
    try:
        from services.email_service import send_reset_email

        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400

        email = data['email'].strip().lower()

        user = User.query.filter_by(email=email).first()
        if user:
            token = _generate_reset_token(user)
            reset_link = url_for(
                'reset_password_page', token=token, _external=True
            )
            send_reset_email(user.email, reset_link)

        # Always respond with the same message (no enumeration)
        return jsonify({
            'message': 'If that email is registered, a reset link has been sent.'
        }), 200

    except Exception as e:
        current_app.logger.error(f'forgot_password error: {e}')
        return jsonify({'error': 'An unexpected error occurred'}), 500


@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token: str):
    """
    Validate a reset token and update the user's password.
    """
    try:
        user, error = _verify_reset_token(token)

        if error == 'expired':
            return jsonify({'error': 'This reset link has expired. Please request a new one.'}), 400
        if error == 'invalid' or user is None:
            return jsonify({'error': 'This reset link is invalid or has already been used.'}), 400

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        new_password    = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()

        if not new_password:
            return jsonify({'error': 'Password is required'}), 400
        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        if new_password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400

        # Update password — this also changes password_hash, invalidating the token
        user.set_password(new_password)
        db.session.commit()

        return jsonify({'message': 'Your password has been updated successfully.'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'reset_password error: {e}')
        return jsonify({'error': 'An unexpected error occurred'}), 500
