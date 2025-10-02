from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import joblib
import os
from ml_model import DropoutPredictor
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize ML model
predictor = DropoutPredictor()

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student')  # student, counselor, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # Demographics
    marital_status = db.Column(db.Integer, default=0)
    age_at_enrollment = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.Integer, default=0)
    nationality = db.Column(db.Integer, default=0)
    
    # Academic Info
    application_mode = db.Column(db.Integer, default=0)
    application_order = db.Column(db.Integer, default=0)
    course = db.Column(db.Integer, default=0)
    daytime_evening_attendance = db.Column(db.Integer, default=0)
    previous_qualification = db.Column(db.Integer, default=0)
    
    # Family Background
    mothers_qualification = db.Column(db.Integer, default=0)
    fathers_qualification = db.Column(db.Integer, default=0)
    mothers_occupation = db.Column(db.Integer, default=0)
    fathers_occupation = db.Column(db.Integer, default=0)
    
    # Special Circumstances
    displaced = db.Column(db.Integer, default=0)
    educational_special_needs = db.Column(db.Integer, default=0)
    debtor = db.Column(db.Integer, default=0)
    tuition_fees_up_to_date = db.Column(db.Integer, default=1)
    scholarship_holder = db.Column(db.Integer, default=0)
    international = db.Column(db.Integer, default=0)
    
    # 1st Semester Performance
    curricular_units_1st_sem_credited = db.Column(db.Float, default=0)
    curricular_units_1st_sem_enrolled = db.Column(db.Float, default=0)
    curricular_units_1st_sem_evaluations = db.Column(db.Float, default=0)
    curricular_units_1st_sem_approved = db.Column(db.Float, default=0)
    curricular_units_1st_sem_grade = db.Column(db.Float, default=0)
    curricular_units_1st_sem_without_evaluations = db.Column(db.Float, default=0)
    
    # 2nd Semester Performance
    curricular_units_2nd_sem_credited = db.Column(db.Float, default=0)
    curricular_units_2nd_sem_enrolled = db.Column(db.Float, default=0)
    curricular_units_2nd_sem_evaluations = db.Column(db.Float, default=0)
    curricular_units_2nd_sem_approved = db.Column(db.Float, default=0)
    curricular_units_2nd_sem_grade = db.Column(db.Float, default=0)
    curricular_units_2nd_sem_without_evaluations = db.Column(db.Float, default=0)
    
    # Economic Indicators
    unemployment_rate = db.Column(db.Float, default=0)
    inflation_rate = db.Column(db.Float, default=0)
    gdp = db.Column(db.Float, default=0)
    
    # Prediction Results
    dropout_risk_score = db.Column(db.Float, default=0)
    risk_category = db.Column(db.String(10), default='Low')
    last_prediction_date = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    counselor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(20), default='risk_alert')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    # Get analytics data for homepage
    total_students = Student.query.count()
    high_risk = Student.query.filter_by(risk_category='High').count()
    medium_risk = Student.query.filter_by(risk_category='Medium').count()
    low_risk = Student.query.filter_by(risk_category='Low').count()
    
    # Calculate success rate
    success_rate = ((total_students - high_risk) / total_students * 100) if total_students > 0 else 87.3
    
    # Active interventions
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_interventions = Notification.query.filter(
        Notification.created_at >= thirty_days_ago
    ).count()
    
    analytics = {
        'total_students': total_students if total_students > 0 else 1247,
        'high_risk': high_risk if total_students > 0 else 89,
        'medium_risk': medium_risk,
        'low_risk': low_risk,
        'success_rate': round(success_rate, 1),
        'active_interventions': active_interventions if active_interventions > 0 else 156
    }
    
    return render_template('index.html', analytics=analytics)

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'student':
        # Get student's own data if linked
        student_data = None
        if current_user.role == 'student':
            student = Student.query.filter_by(user_id=current_user.id).first()
            if student:
                student_data = {
                    'id': student.id,
                    'student_id': student.student_id,
                    'name': student.name,
                    'risk_score': student.dropout_risk_score,
                    'risk_category': student.risk_category,
                    'age_at_enrollment': student.age_at_enrollment,
                    'scholarship_holder': student.scholarship_holder,
                    'last_prediction_date': student.last_prediction_date.isoformat() if student.last_prediction_date else None
                }
        return render_template('student_dashboard.html', student_data=student_data)
    elif current_user.role == 'admin':
        # Get analytics data for university dashboard
        total_students = Student.query.count()
        high_risk = Student.query.filter_by(risk_category='High').count()
        medium_risk = Student.query.filter_by(risk_category='Medium').count()
        low_risk = Student.query.filter_by(risk_category='Low').count()
        
        # Calculate success rate
        success_rate = ((total_students - high_risk) / total_students * 100) if total_students > 0 else 0
        
        # Active interventions
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_interventions = Notification.query.filter(
            Notification.created_at >= thirty_days_ago
        ).count()
        
        analytics = {
            'total_students': total_students,
            'high_risk': high_risk,
            'medium_risk': medium_risk,
            'low_risk': low_risk,
            'success_rate': round(success_rate, 1),
            'active_interventions': active_interventions
        }
        
        return render_template('admin_dashboard.html', analytics=analytics)
    elif current_user.role == 'counselor':
        # Get analytics data for counselor dashboard
        total_students = Student.query.count()
        high_risk = Student.query.filter_by(risk_category='High').count()
        medium_risk = Student.query.filter_by(risk_category='Medium').count()
        low_risk = Student.query.filter_by(risk_category='Low').count()
        
        # Calculate success rate
        success_rate = ((total_students - high_risk) / total_students * 100) if total_students > 0 else 0
        
        # Active interventions
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_interventions = Notification.query.filter(
            Notification.created_at >= thirty_days_ago
        ).count()
        
        analytics = {
            'total_students': total_students,
            'high_risk': high_risk,
            'medium_risk': medium_risk,
            'low_risk': low_risk,
            'success_rate': round(success_rate, 1),
            'active_interventions': active_interventions
        }
        
        return render_template('university_dashboard.html', analytics=analytics)
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        print(f"Login attempt for username: {username}")
        user = User.query.filter_by(username=username).first()
        
        if user:
            print(f"User found: {user.username}, role: {user.role}")
            if user.check_password(password):
                print("Password check passed")
                login_user(user)
                return jsonify({
                    'success': True, 
                    'role': user.role,
                    'redirect': '/dashboard'
                })
            else:
                print("Password check failed")
                return jsonify({'success': False, 'message': 'Invalid password'})
        else:
            print("User not found")
            return jsonify({'success': False, 'message': 'User not found'})
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# API Routes
@app.route('/api/predict', methods=['POST'])
@login_required
def predict_dropout():
    try:
        data = request.get_json()
        
        # Extract features for prediction
        features = [
            data.get('marital_status', 0),
            data.get('application_mode', 0),
            data.get('application_order', 0),
            data.get('course', 0),
            data.get('daytime_evening_attendance', 0),
            data.get('previous_qualification', 0),
            data.get('nationality', 0),
            data.get('mothers_qualification', 0),
            data.get('fathers_qualification', 0),
            data.get('mothers_occupation', 0),
            data.get('fathers_occupation', 0),
            data.get('displaced', 0),
            data.get('educational_special_needs', 0),
            data.get('debtor', 0),
            data.get('tuition_fees_up_to_date', 1),
            data.get('gender', 0),
            data.get('scholarship_holder', 0),
            data.get('age_at_enrollment', 18),
            data.get('international', 0),
            data.get('curricular_units_1st_sem_credited', 0),
            data.get('curricular_units_1st_sem_enrolled', 0),
            data.get('curricular_units_1st_sem_evaluations', 0),
            data.get('curricular_units_1st_sem_approved', 0),
            data.get('curricular_units_1st_sem_grade', 0),
            data.get('curricular_units_1st_sem_without_evaluations', 0),
            data.get('curricular_units_2nd_sem_credited', 0),
            data.get('curricular_units_2nd_sem_enrolled', 0),
            data.get('curricular_units_2nd_sem_evaluations', 0),
            data.get('curricular_units_2nd_sem_approved', 0),
            data.get('curricular_units_2nd_sem_grade', 0),
            data.get('curricular_units_2nd_sem_without_evaluations', 0),
            data.get('unemployment_rate', 0),
            data.get('inflation_rate', 0),
            data.get('gdp', 0)
        ]
        
        # Make prediction
        risk_score, risk_category, recommendations = predictor.predict(features)
        
        # Update student record if student_id provided
        student_id = data.get('student_id')
        if student_id:
            student = Student.query.filter_by(student_id=student_id).first()
            if student:
                student.dropout_risk_score = risk_score
                student.risk_category = risk_category
                student.last_prediction_date = datetime.utcnow()
                db.session.commit()
                
                # Create notification if high risk
                if risk_category == 'High':
                    counselors = User.query.filter_by(role='counselor').all()
                    for counselor in counselors:
                        notification = Notification(
                            student_id=student.id,
                            counselor_id=counselor.id,
                            message=f"Student {student.name} ({student.student_id}) is at HIGH risk of dropout. Immediate intervention recommended.",
                            notification_type='high_risk_alert'
                        )
                        db.session.add(notification)
                    db.session.commit()
        
        return jsonify({
            'success': True,
            'risk_score': float(risk_score),
            'risk_category': risk_category,
            'recommendations': recommendations
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/students', methods=['GET'])
@login_required
def get_students():
    if current_user.role not in ['counselor', 'admin']:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    students = Student.query.all()
    print(f"Found {len(students)} students in database")
    student_data = []
    
    for student in students:
        student_data.append({
            'id': student.id,
            'student_id': student.student_id,
            'name': student.name,
            'age_at_enrollment': student.age_at_enrollment,
            'gender': student.gender,
            'scholarship_holder': student.scholarship_holder,
            'tuition_fees_up_to_date': student.tuition_fees_up_to_date,
            'curricular_units_1st_sem_grade': student.curricular_units_1st_sem_grade,
            'curricular_units_1st_sem_approved': student.curricular_units_1st_sem_approved,
            'curricular_units_2nd_sem_grade': student.curricular_units_2nd_sem_grade,
            'curricular_units_2nd_sem_approved': student.curricular_units_2nd_sem_approved,
            'risk_score': student.dropout_risk_score,
            'risk_category': student.risk_category,
            'last_prediction_date': student.last_prediction_date.isoformat() if student.last_prediction_date else None
        })
    
    print(f"Returning {len(student_data)} students to frontend")
    return jsonify({'success': True, 'students': student_data})

@app.route('/api/student/<student_id>', methods=['GET'])
@login_required
def get_student(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    
    if not student:
        return jsonify({'success': False, 'message': 'Student not found'})
    
    # Check authorization
    if current_user.role == 'student' and student.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    student_data = {
        'id': student.id,
        'student_id': student.student_id,
        'name': student.name,
        'risk_score': student.dropout_risk_score,
        'risk_category': student.risk_category,
        'last_prediction_date': student.last_prediction_date.isoformat() if student.last_prediction_date else None,
        'age_at_enrollment': student.age_at_enrollment,
        'gender': student.gender,
        'scholarship_holder': student.scholarship_holder
    }
    
    return jsonify({'success': True, 'student': student_data})

@app.route('/api/analytics', methods=['GET'])
@login_required
def get_analytics():
    if current_user.role not in ['counselor', 'admin']:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    total_students = Student.query.count()
    high_risk = Student.query.filter_by(risk_category='High').count()
    medium_risk = Student.query.filter_by(risk_category='Medium').count()
    low_risk = Student.query.filter_by(risk_category='Low').count()
    
    # Calculate success rate (students not at high risk)
    success_rate = ((total_students - high_risk) / total_students * 100) if total_students > 0 else 0
    
    # Active interventions (notifications in last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_interventions = Notification.query.filter(
        Notification.created_at >= thirty_days_ago
    ).count()
    
    analytics_data = {
        'total_students': total_students,
        'high_risk': high_risk,
        'medium_risk': medium_risk,
        'low_risk': low_risk,
        'success_rate': round(success_rate, 1),
        'active_interventions': active_interventions
    }
    
    return jsonify({'success': True, 'analytics': analytics_data})
@app.route('/api/predict/quick', methods=['POST'])
def quick_predict():
    """Allow anonymous quick predictions from homepage"""
    try:
        data = request.get_json()

        # Extract only the simple features from homepage form
        age = float(data.get('age_at_enrollment', 20))
        gender = int(data.get('gender', 0))
        g1 = float(data.get('curricular_units_1st_sem_grade', 12))
        g2 = float(data.get('curricular_units_2nd_sem_grade', 12))
        tuition = int(data.get('tuition_fees_up_to_date', 1))
        scholarship = int(data.get('scholarship_holder', 0))
        approved1 = int(data.get('curricular_units_1st_sem_approved', 5))
        approved2 = int(data.get('curricular_units_2nd_sem_approved', 5))

        # Build a full 34-feature vector with defaults
        features = [
            0, 1, 1, 1, 0, 1, 1,  # marital, application, course, etc.
            1, 1, 1, 1,           # parents info
            0, 0,                 # displaced, special needs
            0, tuition, gender, scholarship, age, 0,   # key fields
            0, 6, 6, approved1, g1, 0,                 # 1st sem
            0, 6, 6, approved2, g2, 0,                 # 2nd sem
            8, 2, 2                                    # economy: unemployment, inflation, GDP
        ]

        risk_score, risk_category, _ = predictor.predict(features)

        return jsonify({
            'success': True,
            'risk_score': float(risk_score),
            'risk_category': risk_category,
            'recommendations': []  # keep it simple for homepage
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# ------------------------- CSV Import/Export Helpers -------------------------
def _ensure_uploads_dir():
    """Ensure uploads directory exists and return its path."""
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    return uploads_dir

def _csv_to_student_fields(row: pd.Series) -> dict:
    """
    Map incoming CSV row to Student model fields.
    Required headings follow the problem statement. Optional columns: 'student_id', 'name'.
    """
    g = lambda k, d=0: row.get(k, d)
    # Safe conversions
    def to_int(val, default=0):
        try:
            if pd.isna(val):
                return default
            return int(float(val))
        except Exception:
            return default

    def to_float(val, default=0.0):
        try:
            if pd.isna(val):
                return default
            return float(val)
        except Exception:
            return default

    return {
        'student_id': str(row.get('student_id', f"CSV{int(row.name)+1:05d}")),
        'name': str(row.get('name', f"Student {int(row.name)+1}")),
        'marital_status': to_int(g('Marital status', 0)),
        'application_mode': to_int(g('Application mode', 0)),
        'application_order': to_int(g('Application order', 0)),
        'course': to_int(g('Course', 0)),
        'daytime_evening_attendance': to_int(g('Daytime/evening attendance', 0)),
        'previous_qualification': to_int(g('Previous qualification', 0)),
        'nationality': to_int(g('Nacionality', 0)),
        'mothers_qualification': to_int(g("Mother's qualification", 0)),
        'fathers_qualification': to_int(g("Father's qualification", 0)),
        'mothers_occupation': to_int(g("Mother's occupation", 0)),
        'fathers_occupation': to_int(g("Father's occupation", 0)),
        'displaced': to_int(g('Displaced', 0)),
        'educational_special_needs': to_int(g('Educational special needs', 0)),
        'debtor': to_int(g('Debtor', 0)),
        'tuition_fees_up_to_date': to_int(g('Tuition fees up to date', 1)),
        'gender': to_int(g('Gender', 0)),
        'scholarship_holder': to_int(g('Scholarship holder', 0)),
        'age_at_enrollment': to_int(g('Age at enrollment', 18), 18),
        'international': to_int(g('International', 0)),
        'curricular_units_1st_sem_credited': to_float(g('Curricular units 1st sem (credited)', 0)),
        'curricular_units_1st_sem_enrolled': to_float(g('Curricular units 1st sem (enrolled)', 0)),
        'curricular_units_1st_sem_evaluations': to_float(g('Curricular units 1st sem (evaluations)', 0)),
        'curricular_units_1st_sem_approved': to_float(g('Curricular units 1st sem (approved)', 0)),
        'curricular_units_1st_sem_grade': to_float(g('Curricular units 1st sem (grade)', 0)),
        'curricular_units_1st_sem_without_evaluations': to_float(g('Curricular units 1st sem (without evaluations)', 0)),
        'curricular_units_2nd_sem_credited': to_float(g('Curricular units 2nd sem (credited)', 0)),
        'curricular_units_2nd_sem_enrolled': to_float(g('Curricular units 2nd sem (enrolled)', 0)),
        'curricular_units_2nd_sem_evaluations': to_float(g('Curricular units 2nd sem (evaluations)', 0)),
        'curricular_units_2nd_sem_approved': to_float(g('Curricular units 2nd sem (approved)', 0)),
        'curricular_units_2nd_sem_grade': to_float(g('Curricular units 2nd sem (grade)', 0)),
        'curricular_units_2nd_sem_without_evaluations': to_float(g('Curricular units 2nd sem (without evaluations)', 0)),
        'unemployment_rate': to_float(g('Unemployment rate', 0)),
        'inflation_rate': to_float(g('Inflation rate', 0)),
        'gdp': to_float(g('GDP', 0)),
    }

def _row_to_features(row: pd.Series) -> list:
    """Build feature list in the exact order expected by the model."""
    # Default values for each feature
    defaults = {
        'Marital status': 0,
        'Application mode': 0,
        'Application order': 0,
        'Course': 0,
        'Daytime/evening attendance': 0,
        'Previous qualification': 0,
        'Nacionality': 0,
        "Mother's qualification": 0,
        "Father's qualification": 0,
        "Mother's occupation": 0,
        "Father's occupation": 0,
        'Displaced': 0,
        'Educational special needs': 0,
        'Debtor': 0,
        'Tuition fees up to date': 1,  # Default to fees up to date
        'Gender': 0,
        'Scholarship holder': 0,
        'Age at enrollment': 18,  # Reasonable default age
        'International': 0,
        'Curricular units 1st sem (credited)': 0,
        'Curricular units 1st sem (enrolled)': 0,
        'Curricular units 1st sem (evaluations)': 0,
        'Curricular units 1st sem (approved)': 0,
        'Curricular units 1st sem (grade)': 0,
        'Curricular units 1st sem (without evaluations)': 0,
        'Curricular units 2nd sem (credited)': 0,
        'Curricular units 2nd sem (enrolled)': 0,
        'Curricular units 2nd sem (evaluations)': 0,
        'Curricular units 2nd sem (approved)': 0,
        'Curricular units 2nd sem (grade)': 0,
        'Curricular units 2nd sem (without evaluations)': 0,
        'Unemployment rate': 0,
        'Inflation rate': 0,
        'GDP': 0
    }
    
    # Get available features from row, use defaults for missing ones
    features = []
    for feature_name, default_val in defaults.items():
        try:
            # Try to get the value, use default if not found or NaN/None
            val = row[feature_name] if feature_name in row else default_val
            val = default_val if pd.isna(val) or val is None else float(val)
            features.append(val)
        except (KeyError, ValueError):
            # If any error occurs, use the default value
            features.append(default_val)
    
    return features

@app.route('/api/import', methods=['POST'])
@login_required
def import_csv():
    """Import a CSV of students, run predictions, and upsert into DB."""
    if current_user.role not in ['counselor', 'admin']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'success': False, 'message': 'Please upload a .csv file'}), 400
    
    # Check if user wants to replace existing data
    replace_existing = request.form.get('replace_existing', 'false').lower() == 'true'

    try:
        uploads_dir = _ensure_uploads_dir()
        save_path = os.path.join(uploads_dir, file.filename)
        file.save(save_path)

        # Read CSV with all columns as strings to avoid type inference issues
        df = pd.read_csv(save_path, dtype=str)
        
        # Normalize column names (strip whitespace and make case-insensitive)
        df.columns = df.columns.str.strip()
        
        # Track which expected columns are missing
        missing_columns = [col for col in predictor.feature_names 
                          if col not in df.columns]
        
        # Log the missing columns for debugging
        if missing_columns:
            print(f"Warning: Missing columns in CSV: {missing_columns}")
            print("Using default values for missing columns")

        # Clear existing data if requested
        if replace_existing:
            existing_count = Student.query.count()
            print(f"Clearing {existing_count} existing student records...")
            try:
                # Use a more aggressive deletion method
                db.session.execute(db.text("DELETE FROM student"))
                db.session.commit()
                print(f"Successfully cleared all existing student records using direct SQL")
            except Exception as e:
                print(f"Direct SQL deletion failed, trying ORM method: {e}")
                Student.query.delete()
                db.session.commit()
                print(f"Successfully cleared using ORM method")
            
            # Verify deletion
            remaining_count = Student.query.count()
            print(f"Remaining students after deletion: {remaining_count}")
            if remaining_count > 0:
                print(f"WARNING: {remaining_count} students still remain after deletion!")

        created, updated = 0, 0
        results = []

        for _, row in df.iterrows():
            # Predict risk
            features = _row_to_features(row)
            risk_score, risk_category, _ = predictor.predict(features)

            # Map to Student fields
            fields = _csv_to_student_fields(row)
            fields.update({
                'dropout_risk_score': float(risk_score),
                'risk_category': risk_category,
                'last_prediction_date': datetime.utcnow()
            })

            # In replace mode, always create new records
            if replace_existing:
                student = Student(**fields)
                db.session.add(student)
                created += 1
            else:
                # Upsert by student_id only in merge mode
                sid = fields['student_id']
                student = Student.query.filter_by(student_id=sid).first()
                if student:
                    for k, v in fields.items():
                        setattr(student, k, v)
                    updated += 1
                else:
                    student = Student(**fields)
                    db.session.add(student)
                    created += 1

            results.append({
                'student_id': fields['student_id'],
                'name': fields['name'],
                'risk_score': float(risk_score),
                'risk_category': risk_category
            })

        db.session.commit()
        
        # Verify data was saved
        total_students_after = Student.query.count()
        print(f"Total students in database after import: {total_students_after}")

        response = {
            'success': True,
            'summary': {
                'created': created,
                'updated': updated,
                'total': int(created + updated),
                'replaced_existing': replace_existing,
                'file_name': file.filename,
                'import_date': datetime.utcnow().isoformat(),
                'total_in_db': total_students_after
            },
            'results': results[:50]  # return first 50 previews
        }
        
        # Add info about missing columns if any
        if 'missing_columns' in locals() and missing_columns:
            response['warnings'] = {
                'missing_columns': missing_columns,
                'message': f'Used default values for {len(missing_columns)} missing columns'
            }
            
        return jsonify(response)
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/export', methods=['GET'])
@login_required
def export_csv():
    """Export current students with risk scores as CSV."""
    if current_user.role not in ['counselor', 'admin']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    students = Student.query.all()
    rows = []
    for s in students:
        rows.append({
            'student_id': s.student_id,
            'name': s.name,
            'risk_score': s.dropout_risk_score,
            'risk_category': s.risk_category,
            'last_prediction_date': s.last_prediction_date.isoformat() if s.last_prediction_date else ''
        })
    df = pd.DataFrame(rows)

    csv_data = df.to_csv(index=False)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=students_export.csv'
    return response

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    if current_user.role not in ['counselor', 'admin']:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    notifications = Notification.query.filter_by(
        counselor_id=current_user.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    notification_data = []
    for notification in notifications:
        student = Student.query.get(notification.student_id)
        notification_data.append({
            'id': notification.id,
            'message': notification.message,
            'student_name': student.name if student else 'Unknown',
            'type': notification.notification_type,
            'created_at': notification.created_at.isoformat()
        })
    
    return jsonify({'success': True, 'notifications': notification_data})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@university.edu',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: admin/admin123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
