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
    max_workload = db.Column(db.Integer, default=20)
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

    def get_active_duties(self, reference_date=None):
        """Get only duties active on the given date."""
        return [
            d for d in self.duties
            if d.faculty_id == self.id and d.is_active(reference_date)
        ]
    
    def calculate_teaching_hours(self):
        """Calculate total teaching hours from all assignments (includes multi-class teaching)"""
        return sum([a.subject.hours_per_week for a in self.assignments])
    
    def calculate_duty_hours(self, reference_date=None):
        """Calculate total duty hours active on the given date."""
        return sum([d.hours for d in self.get_active_duties(reference_date)])

    def calculate_total_workload(self, reference_date=None):
        """Calculate total workload: teaching + duties active on the given date."""
        teaching_hours = self.calculate_teaching_hours()
        duty_hours = self.calculate_duty_hours(reference_date)
        return teaching_hours + duty_hours

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
            'class_id',
            'academic_year',
            name='unique_faculty_subject_class_year'
        ),
    )
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=True)
    class_division = db.Column(db.String(20), nullable=True)  # Legacy compatibility for older rows
    semester = db.Column(db.Integer, nullable=False)  # Inherited from subject but stored for reference
    academic_year = db.Column(db.String(20), nullable=False)  # e.g., "2025-26"
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)

    class_obj = db.relationship('Class', backref='assignments')

    @property
    def class_name(self):
        if self.class_obj:
            return self.class_obj.class_name
        return self.class_division or "Unassigned Class"

    def __repr__(self):
        return f'<Assignment {self.faculty_id} -> {self.subject_id} ({self.class_name})>'


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
    duty_day = db.Column(db.String(20), nullable=True)  # Monday-Friday
    start_date = db.Column(db.Date, nullable=False)  # When duty starts
    end_date = db.Column(db.Date, nullable=False)  # When duty ends
    academic_year = db.Column(db.String(20), nullable=False)  # e.g., "2025-26"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def preferred_days_list(self):
        if not self.duty_day:
            return []
        return [day.strip() for day in self.duty_day.split(',') if day.strip()]

    @property
    def preferred_days_display(self):
        days = self.preferred_days_list
        return ", ".join(days) if days else "Random"
    
    def is_active(self, reference_date=None):
        """Check if duty is active for a given date."""
        target_date = reference_date or datetime.utcnow().date()
        return self.start_date <= target_date <= self.end_date

    def overlaps_week(self, week_start):
        """Check if duty overlaps the displayed Monday-Friday week."""
        week_end = week_start + timedelta(days=4)
        return self.start_date <= week_end and self.end_date >= week_start

    def occurs_on_date(self, target_date):
        """Check if the duty should appear on a specific calendar date."""
        if not self.is_active(target_date):
            return False

        preferred_days = self.preferred_days_list
        if preferred_days and target_date.strftime('%A') not in preferred_days:
            return False

        return True
    
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
