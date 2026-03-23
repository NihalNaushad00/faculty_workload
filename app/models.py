from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
# -----------------------
# Faculty Table
# -----------------------
class Faculty(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    max_workload = db.Column(db.Integer, default=16)
    role = db.Column(db.String(20), default="faculty")

    assignments = db.relationship(
        'Assignment',
        backref='faculty',
        lazy=True,
        cascade="all, delete-orphan"
    )
    duties = db.relationship(
        'AdditionalDuty',
        backref='faculty',
        lazy=True,
        cascade="all, delete-orphan"
    )
    timetables = db.relationship(
        'Timetable',
        backref='faculty_obj',
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def calculate_total_workload(self):
        subject_hours = sum([a.subject.hours_per_week for a in self.assignments])
        duty_hours = sum([d.hours for d in self.duties])
        return subject_hours + duty_hours

# -----------------------
# Subject Table
# -----------------------
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), nullable=False)
    subject_name = db.Column(db.String(150), nullable=False)
    subject_type = db.Column(db.String(20), nullable=False)  # 'Theory' or 'Lab'
    is_lab = db.Column(db.Boolean, default=False)  # Flag for lab subjects
    hours_per_week = db.Column(db.Integer, nullable=False)  # Theory: varies, Lab: typically 3 hours continuous
    semester = db.Column(db.Integer, nullable=False)  # Semester number (1-8)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assignments = db.relationship(
        'Assignment',
        backref='subject',
        lazy=True,
        cascade="all, delete-orphan"
    )


# -----------------------
# Assignment Table
# -----------------------
class Assignment(db.Model):
    __table_args__ = (
        db.UniqueConstraint(
            'faculty_id',
            'subject_id',
            'class_division',
            'academic_year',
            name='unique_faculty_subject_class_year'
        ),
    )
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    class_division = db.Column(db.String(20), nullable=False)  # e.g., "A", "B", "S1-A", "S2-B"
    semester = db.Column(db.Integer, nullable=False)  # Inherited from subject but stored for reference
    academic_year = db.Column(db.String(20), nullable=False)  # e.g., "2025-26"
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Assignment {self.faculty_id} -> {self.subject_id} ({self.class_division})>'


# -----------------------
# Additional Duties
# -----------------------
class AdditionalDuty(db.Model):
    __table_args__ = (
        db.UniqueConstraint(
            'faculty_id',
            'duty_name',
            'start_date',
            name='unique_faculty_duty_period'
        ),
    )
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True)  # Allow unassigned
    duty_name = db.Column(db.String(150), nullable=False)  # e.g., "HOD", "Placement Officer", "Exam Cell Duty"
    category = db.Column(db.String(50), nullable=False)  # 'Leadership' (HOD/Placement Officer), 'Exam', 'Administrative', 'Research'
    duration_type = db.Column(db.String(20), nullable=False)  # 'Yearly' or 'Weekly' or 'Custom'
    hours = db.Column(db.Integer, nullable=False)  # Hours per week
    start_date = db.Column(db.Date, nullable=False)  # When duty starts
    end_date = db.Column(db.Date, nullable=False)  # When duty ends
    academic_year = db.Column(db.String(20), nullable=False)  # e.g., "2025-26"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_active(self):
        """Check if duty is currently active"""
        today = datetime.utcnow().date()
        return self.start_date <= today <= self.end_date
    
    def duration_days(self):
        """Get total duration in days"""
        return (self.end_date - self.start_date).days
    
    def __repr__(self):
        return f'<AdditionalDuty {self.duty_name} ({self.start_date} to {self.end_date})>'


# -----------------------
# TimeSlot Table
# -----------------------
class TimeSlot(db.Model):
    __tablename__ = 'timeslot'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)  # Monday to Friday
    hour = db.Column(db.Integer, nullable=False)  # 1 to 6
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    timetables = db.relationship(
        'Timetable',
        backref='timeslot',
        lazy=True,
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f'<TimeSlot {self.day} - Hour {self.hour}>'


# -----------------------
# Class Table
# -----------------------
class Class(db.Model):
    __tablename__ = 'class'
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(50), nullable=False, unique=True)  # e.g., "S3-A", "S5-B"
    semester = db.Column(db.Integer, nullable=False)  # 1-8
    department = db.Column(db.String(100), nullable=False)  # e.g., "Computer Science"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    timetables = db.relationship(
        'Timetable',
        backref='class_obj',
        lazy=True,
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f'<Class {self.class_name} ({self.semester}s, {self.department})>'


# -----------------------
# Timetable Table
# -----------------------
class Timetable(db.Model):
    __tablename__ = 'timetable'
    __table_args__ = (
        db.UniqueConstraint(
            'class_id',
            'timeslot_id',
            name='unique_class_timeslot'
        ),
        db.UniqueConstraint(
            'faculty_id',
            'timeslot_id',
            name='unique_faculty_timeslot'
        ),
    )
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    timeslot_id = db.Column(db.Integer, db.ForeignKey('timeslot.id'), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)  # e.g., "2025-26"
    semester = db.Column(db.Integer, nullable=False)  # Inherited from subject but stored for reference
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key relationships
    subject = db.relationship('Subject', backref='timetables')
    
    def __repr__(self):
        return f'<Timetable {self.class_id} - {self.subject_id} by {self.faculty_id} ({self.timeslot_id})>'