import os
import logging
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from app import app, db
from models import (
    User, StudentProfile, MentorProfile, LearningContent, 
    LearningActivity, Achievement, EmotionLog, LearningStyle,
    Language, EmotionalState, LearningStyleAssessment, MentorStudentRelationship
)
from utils.ai_services import (
    generate_personalized_content, analyze_student_response,
    get_multilingual_content, recommend_content
)
# Import vision services with error handling
try:
    from utils.vision_services import (
        detect_emotion, track_engagement, analyze_learning_state
    )
except ImportError as e:
    logging.warning(f"Could not import vision services: {e}")
    
    # Define fallback functions if imports fail
    def detect_emotion(image_file):
        logging.warning("Using fallback emotion detection")
        return {
            'emotion': 'neutral',
            'confidence': 0.5,
            'all_emotions': {
                'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0,
                'sad': 0, 'surprise': 0, 'neutral': 100
            }
        }
    
    def track_engagement(image_file):
        logging.warning("Using fallback engagement tracking")
        return {
            'face_detected': False,
            'eyes_detected': False,
            'engagement_level': 0.5,
            'emotion': 'neutral'
        }
    
    def analyze_learning_state(engagement_history, emotion_history):
        logging.warning("Using fallback learning state analysis")
        return {
            'average_engagement': 0.5,
            'dominant_emotion': 'neutral',
            'learning_state': 'passive_learning',
            'recommendations': ['Take a short break before continuing']
        }
from utils.language_services import translate_content, detect_language
from utils.learning_utils import (
    assess_learning_style, update_student_progress,
    award_achievement, calculate_streak
)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        preferred_language = request.form.get('preferred_language', 'english')
        grade_level = request.form.get('grade_level', 1)
        school_name = request.form.get('school_name', '')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            preferred_language=Language[preferred_language.upper()],
            grade_level=grade_level,
            school_name=school_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create student profile
        student_profile = StudentProfile(user_id=user.id)
        db.session.add(student_profile)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Student Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    # Get student profile
    student_profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    if not student_profile:
        flash('Student profile not found', 'danger')
        return redirect(url_for('index'))
    
    # Get recent activities
    recent_activities = LearningActivity.query.filter_by(
        user_id=current_user.id
    ).order_by(LearningActivity.start_time.desc()).limit(5).all()
    
    # Get achievements
    achievements = Achievement.query.filter_by(
        user_id=current_user.id
    ).order_by(Achievement.date_earned.desc()).all()
    
    # Calculate streak
    current_streak = calculate_streak(current_user.id)
    
    # Get recommended content
    recommended_content = recommend_content(current_user.id)
    
    return render_template(
        'dashboard.html',
        student=student_profile,
        activities=recent_activities,
        achievements=achievements,
        streak=current_streak,
        recommended_content=recommended_content
    )

# Learning routes
@app.route('/learn')
@login_required
def learn():
    # Get available content based on student's profile
    student_profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    subjects = request.args.get('subjects', '')
    difficulty = request.args.get('difficulty', student_profile.difficulty_level)
    
    # Query available content
    query = LearningContent.query
    
    if subjects:
        query = query.filter(LearningContent.subject.contains(subjects))
    
    query = query.filter(LearningContent.difficulty_level <= difficulty + 1)
    query = query.filter(LearningContent.difficulty_level >= difficulty - 1)
    
    content_list = query.all()
    
    return render_template(
        'learn.html',
        content_list=content_list,
        student=student_profile
    )

@app.route('/learn/<int:content_id>')
@login_required
def learn_content(content_id):
    content = LearningContent.query.get_or_404(content_id)
    student_profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    # Check if we need to translate content
    if content.language != current_user.preferred_language:
        translated_content = translate_content(
            content.content,
            str(content.language.value),
            str(current_user.preferred_language.value)
        )
        content.content = translated_content
    
    # Record learning activity start
    activity = LearningActivity(
        user_id=current_user.id,
        content_id=content_id,
        start_time=datetime.utcnow()
    )
    db.session.add(activity)
    db.session.commit()
    
    # Store activity ID in session for tracking
    session['current_activity_id'] = activity.id
    
    return render_template('learn_content.html', content=content, student=student_profile)

@app.route('/complete_activity', methods=['POST'])
@login_required
def complete_activity():
    activity_id = session.get('current_activity_id')
    
    if not activity_id:
        return jsonify({'error': 'No active learning activity found'}), 400
    
    activity = LearningActivity.query.get(activity_id)
    
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404
    
    # Update activity completion
    activity.end_time = datetime.utcnow()
    activity.completed = True
    
    # Get score if provided
    score = request.form.get('score')
    if score:
        activity.score = float(score)
    
    db.session.commit()
    
    # Update student progress and check for achievements
    update_student_progress(current_user.id, activity)
    
    # Clear session
    session.pop('current_activity_id', None)
    
    return jsonify({'success': True})

# Assessment routes
@app.route('/assessment')
@login_required
def assessment():
    return render_template('assessment.html')

@app.route('/learning_style_assessment', methods=['POST'])
@login_required
def learning_style_assessment():
    answers = request.get_json()
    
    if not answers:
        return jsonify({'error': 'No assessment data provided'}), 400
    
    # Process learning style assessment
    visual_score, auditory_score, kinesthetic_score = assess_learning_style(answers)
    
    # Determine dominant style
    scores = {
        'visual': visual_score,
        'auditory': auditory_score,
        'kinesthetic': kinesthetic_score
    }
    dominant_style = max(scores, key=scores.get)
    
    # Save assessment results
    assessment = LearningStyleAssessment(
        user_id=current_user.id,
        visual_score=visual_score,
        auditory_score=auditory_score,
        kinesthetic_score=kinesthetic_score,
        dominant_style=LearningStyle[dominant_style.upper()]
    )
    db.session.add(assessment)
    
    # Update student profile
    student_profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    student_profile.learning_style = LearningStyle[dominant_style.upper()]
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'dominant_style': dominant_style,
        'scores': scores
    })

# Mentor matching routes
@app.route('/mentors')
@login_required
def mentors():
    # Get all available mentors
    mentors = MentorProfile.query.all()
    
    # Get student's current mentors
    student_profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    current_mentors = [m.mentor for m in student_profile.mentorships]
    
    return render_template(
        'mentors.html',
        mentors=mentors,
        current_mentors=current_mentors
    )

@app.route('/request_mentor/<int:mentor_id>', methods=['POST'])
@login_required
def request_mentor(mentor_id):
    student_profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    if not student_profile:
        flash('Student profile not found', 'danger')
        return redirect(url_for('mentors'))
    
    # Check if already has a relationship
    existing = MentorStudentRelationship.query.filter_by(
        mentor_id=mentor_id,
        student_id=student_profile.id
    ).first()
    
    if existing:
        flash('You already have a relationship with this mentor', 'info')
        return redirect(url_for('mentors'))
    
    # Create new relationship
    relationship = MentorStudentRelationship(
        mentor_id=mentor_id,
        student_id=student_profile.id,
        status='pending'
    )
    
    db.session.add(relationship)
    db.session.commit()
    
    flash('Mentor request sent successfully', 'success')
    return redirect(url_for('mentors'))

# AI and Vision API routes
@app.route('/api/generate_content', methods=['POST'])
@login_required
def api_generate_content():
    topic = request.form.get('topic')
    subject = request.form.get('subject')
    difficulty = request.form.get('difficulty', 1)
    
    if not topic or not subject:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Get student profile
    student_profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    # Generate personalized content
    try:
        content = generate_personalized_content(
            topic=topic,
            subject=subject,
            difficulty=difficulty,
            learning_style=student_profile.learning_style.value,
            language=current_user.preferred_language.value,
            grade_level=current_user.grade_level
        )
        
        return jsonify(content)
    except Exception as e:
        logging.error(f"Error generating content: {str(e)}")
        return jsonify({'error': 'Failed to generate content'}), 500

@app.route('/api/emotion_detection', methods=['POST'])
@login_required
def api_emotion_detection():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image_file = request.files['image']
    
    # Process emotion detection
    try:
        emotion_data = detect_emotion(image_file)
        
        # Log the detected emotion
        emotion_log = EmotionLog(
            user_id=current_user.id,
            emotion=EmotionalState[emotion_data['emotion'].upper()],
            confidence=emotion_data['confidence'],
            context=request.form.get('context', 'learning')
        )
        db.session.add(emotion_log)
        db.session.commit()
        
        return jsonify(emotion_data)
    except Exception as e:
        logging.error(f"Error detecting emotion: {str(e)}")
        return jsonify({'error': 'Failed to process emotion detection'}), 500

@app.route('/api/track_engagement', methods=['POST'])
@login_required
def api_track_engagement():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    image_file = request.files['image']
    activity_id = session.get('current_activity_id')
    
    if not activity_id:
        return jsonify({'error': 'No active learning activity found'}), 400
    
    # Process engagement tracking
    try:
        engagement_data = track_engagement(image_file)
        
        # Update learning activity
        activity = LearningActivity.query.get(activity_id)
        
        if activity:
            # Initialize emotional_states if it doesn't exist
            if not activity.emotional_states:
                activity.emotional_states = []
            
            # Append new emotion state
            emotion_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'emotion': engagement_data['emotion'],
                'engagement_level': engagement_data['engagement_level']
            }
            
            activity.emotional_states.append(emotion_entry)
            activity.engagement_level = engagement_data['engagement_level']
            db.session.commit()
        
        return jsonify(engagement_data)
    except Exception as e:
        logging.error(f"Error tracking engagement: {str(e)}")
        return jsonify({'error': 'Failed to track engagement'}), 500

# Voice-based navigation
@app.route('/api/voice_command', methods=['POST'])
def api_voice_command():
    command = request.json.get('command')
    
    if not command:
        return jsonify({'error': 'No command provided'}), 400
    
    # Process voice command
    try:
        # Simple command parsing logic
        if 'dashboard' in command.lower():
            return jsonify({'action': 'navigate', 'url': url_for('dashboard')})
        elif 'learn' in command.lower():
            return jsonify({'action': 'navigate', 'url': url_for('learn')})
        elif 'mentors' in command.lower():
            return jsonify({'action': 'navigate', 'url': url_for('mentors')})
        elif 'assessment' in command.lower():
            return jsonify({'action': 'navigate', 'url': url_for('assessment')})
        elif 'logout' in command.lower():
            return jsonify({'action': 'navigate', 'url': url_for('logout')})
        else:
            return jsonify({'action': 'speak', 'message': 'I did not understand that command'})
    except Exception as e:
        logging.error(f"Error processing voice command: {str(e)}")
        return jsonify({'error': 'Failed to process voice command'}), 500

# Profile management
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    student_profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        # Update user profile
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.preferred_language = Language[request.form.get('preferred_language', 'ENGLISH').upper()]
        current_user.grade_level = request.form.get('grade_level')
        current_user.school_name = request.form.get('school_name')
        
        # Update student profile
        student_profile.subjects_of_interest = request.form.get('subjects_of_interest')
        student_profile.requires_voice_nav = 'requires_voice_nav' in request.form
        student_profile.requires_large_text = 'requires_large_text' in request.form
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', student=student_profile)

# Offline mode route
@app.route('/offline')
def offline():
    return render_template('offline.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
