from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Enum, Text
from werkzeug.security import generate_password_hash, check_password_hash
import enum

class LearningStyle(enum.Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    UNKNOWN = "unknown"

class EmotionalState(enum.Enum):
    ENGAGED = "engaged"
    CONFUSED = "confused"
    DISENGAGED = "disengaged"
    FRUSTRATED = "frustrated"
    HAPPY = "happy"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"

class Language(enum.Enum):
    ENGLISH = "english"
    HINDI = "hindi"
    BENGALI = "bengali"
    TAMIL = "tamil"
    TELUGU = "telugu"
    MARATHI = "marathi"
    UNKNOWN = "unknown"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # User profile data
    preferred_language = db.Column(Enum(Language), default=Language.ENGLISH)
    grade_level = db.Column(db.Integer)
    school_name = db.Column(db.String(120))
    learning_style = db.Column(Enum(LearningStyle), default=LearningStyle.UNKNOWN)
    
    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False)
    mentor_profile = db.relationship('MentorProfile', backref='user', uselist=False)
    activities = db.relationship('LearningActivity', backref='user')
    achievements = db.relationship('Achievement', backref='user')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    learning_style = db.Column(Enum(LearningStyle), default=LearningStyle.UNKNOWN)
    subjects_of_interest = db.Column(db.String(256))
    difficulty_level = db.Column(db.Integer, default=1)  # 1-5 scale
    streak_days = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Learning analytics
    average_session_time = db.Column(db.Float, default=0)
    completion_rate = db.Column(db.Float, default=0)
    emotion_history = db.Column(db.JSON)
    
    # Accessibility needs
    requires_voice_nav = db.Column(db.Boolean, default=False)
    requires_large_text = db.Column(db.Boolean, default=False)
    

class MentorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expertise = db.Column(db.String(256))
    availability = db.Column(db.String(256))
    languages = db.Column(db.String(256))
    bio = db.Column(db.Text)
    
    # Mentor-student relationships
    students = db.relationship('MentorStudentRelationship', backref='mentor')


class MentorStudentRelationship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor_profile.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, active, completed
    
    # The specific student being mentored
    student = db.relationship('StudentProfile', backref='mentorships')


class LearningContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    content_type = db.Column(db.String(50))  # video, text, quiz, etc.
    difficulty_level = db.Column(db.Integer)  # 1-5 scale
    subject = db.Column(db.String(50))
    language = db.Column(Enum(Language))
    content = db.Column(Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # For adaptive learning
    prerequisites = db.Column(db.String(256))
    learning_outcomes = db.Column(db.Text)
    
    # Relationships
    activities = db.relationship('LearningActivity', backref='content')


class LearningActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('learning_content.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Float)
    
    # Emotion tracking
    emotional_states = db.Column(db.JSON)
    engagement_level = db.Column(db.Float)  # 0-1 scale
    
    # Feedback
    feedback = db.Column(db.Text)
    
    
class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    badge_name = db.Column(db.String(50))
    points_awarded = db.Column(db.Integer, default=0)
    date_earned = db.Column(db.DateTime, default=datetime.utcnow)
    achievement_type = db.Column(db.String(50))  # streak, completion, skill mastery, etc.


class EmotionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    emotion = db.Column(Enum(EmotionalState), default=EmotionalState.UNKNOWN)
    confidence = db.Column(db.Float)  # 0-1 scale
    context = db.Column(db.String(120))  # what the student was doing


class LearningStyleAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    visual_score = db.Column(db.Float)
    auditory_score = db.Column(db.Float)
    kinesthetic_score = db.Column(db.Float)
    dominant_style = db.Column(Enum(LearningStyle))
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)
    

class OfflineContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('learning_content.id'), nullable=False)
    sync_status = db.Column(db.String(20), default='synced')  # synced, pending_sync
    local_storage_key = db.Column(db.String(120), nullable=False)
    size_bytes = db.Column(db.Integer)
    
    # The associated content
    content = db.relationship('LearningContent')
