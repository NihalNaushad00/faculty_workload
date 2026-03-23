from flask import Blueprint, render_template
from app import db
from app.models import Faculty, Subject, Assignment, AdditionalDuty, Timetable, TimeSlot, Class
from flask import request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        faculty = Faculty.query.filter_by(email=email).first()

        if faculty and faculty.check_password(password):
            login_user(faculty)
            return redirect(url_for('main.dashboard'))

        return "Invalid Credentials"

    return render_template("login.html")

@main.route('/dashboard')
@login_required
def dashboard():
    # Get academic year filter from query string
    selected_year = request.args.get('academic_year', None)
    
    if current_user.role == "admin":
        # ADMIN VIEW
        total_load = current_user.calculate_total_workload()
        assignments = current_user.assignments

        # Admin Analytics
        total_faculty = Faculty.query.count()
        total_subjects = Subject.query.count()
        total_assignments = Assignment.query.count()
        total_duties = AdditionalDuty.query.count()

        overloaded_count = 0
        all_faculty = Faculty.query.all()
        for faculty in all_faculty:
            if faculty.calculate_total_workload() > faculty.max_workload:
                overloaded_count += 1

        return render_template(
            "dashboard.html",
            total_load=total_load,
            assignments=assignments,
            total_faculty=total_faculty,
            total_subjects=total_subjects,
            total_assignments=total_assignments,
            overloaded_count=overloaded_count,
            total_duties=total_duties
        )
    else:
        # FACULTY VIEW
        # Get all unique academic years from assignments and duties
        assignment_years = [a.academic_year for a in current_user.assignments]
        duty_years = [d.academic_year for d in current_user.duties if d.faculty_id == current_user.id]
        all_years = sorted(list(set(assignment_years + duty_years)), reverse=True)
        
        # Default to most recent year if not specified
        if not selected_year and all_years:
            selected_year = all_years[0]
        
        # Filter assignments by academic year
        if selected_year:
            filtered_assignments = [a for a in current_user.assignments if a.academic_year == selected_year]
            filtered_duties = [d for d in current_user.duties if d.faculty_id == current_user.id and d.academic_year == selected_year]
        else:
            filtered_assignments = current_user.assignments
            filtered_duties = [d for d in current_user.duties if d.faculty_id == current_user.id]
        
        # Calculate workload for filtered year
        teaching_hours = sum([a.subject.hours_per_week for a in filtered_assignments])
        duty_hours = sum([d.hours for d in filtered_duties])
        total_workload = teaching_hours + duty_hours
        workload_percentage = (total_workload / current_user.max_workload * 100) if current_user.max_workload > 0 else 0
        
        return render_template(
            "faculty_dashboard.html",
            selected_year=selected_year,
            all_years=all_years,
            assignments=filtered_assignments,
            duties=filtered_duties,
            teaching_hours=teaching_hours,
            duty_hours=duty_hours,
            total_workload=total_workload,
            workload_percentage=workload_percentage
        )
@main.route('/add-subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    if current_user.role != "admin":
        return "Access Denied: Admins Only"
    if request.method == 'POST':
        course_code = request.form.get('course_code')
        subject_name = request.form.get('subject_name')
        subject_type = request.form.get('subject_type')
        hours = request.form.get('hours')
        semester = request.form.get('semester')
        is_lab = request.form.get('is_lab') == 'on'

        subject = Subject(
            course_code=course_code,
            subject_name=subject_name,
            subject_type=subject_type,
            hours_per_week=int(hours),
            semester=int(semester),
            is_lab=is_lab
        )

        db.session.add(subject)
        db.session.commit()

        return redirect(url_for('main.dashboard'))

    return render_template("add_subject.html")


@main.route('/assign-subject', methods=['GET', 'POST'])
@login_required
def assign_subject():
    if current_user.role != "admin":
        return "Access Denied: Admins Only"
    subjects = Subject.query.all()
    faculties = Faculty.query.all()

    if request.method == 'POST':
        faculty_id = request.form.get('faculty_id')
        subject_id = request.form.get('subject_id')
        class_division = request.form.get('class_division')
        academic_year = request.form.get('academic_year')
        
        subject = Subject.query.get(int(subject_id))
        
        if not subject:
            return "Subject not found!"

        existing = Assignment.query.filter_by(
            faculty_id=int(faculty_id),
            subject_id=int(subject_id),
            class_division=class_division,
            academic_year=academic_year
        ).first()

        if existing:
            return "This subject is already assigned to this faculty for this class in this academic year!"

        assignment = Assignment(
            faculty_id=int(faculty_id),
            subject_id=int(subject_id),
            class_division=class_division,
            semester=subject.semester,
            academic_year=academic_year
        )

        db.session.add(assignment)
        db.session.commit()

        return redirect(url_for('main.dashboard'))
    
    return render_template("assign_subject.html", subjects=subjects, faculties=faculties)
@main.route('/add-faculty', methods=['GET', 'POST'])
@login_required
def add_faculty():
    if current_user.role != "admin":
        return "Access Denied: Admins Only"

    if request.method == 'POST':
        name = request.form.get('name')
        department = request.form.get('department')
        designation = request.form.get('designation')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        existing = Faculty.query.filter_by(email=email).first()
        if existing:
            return "Faculty with this email already exists!"

        faculty = Faculty(
            name=name,
            department=department,
            designation=designation,
            email=email,
            role=role
        )

        faculty.set_password(password)

        db.session.add(faculty)
        db.session.commit()

        return redirect(url_for('main.dashboard'))

    return render_template("add_faculty.html")

@main.route('/delete-assignment/<int:id>')
@login_required
def delete_assignment(id):
    if current_user.role != "admin":
        return "Access Denied: Admins Only"

    assignment = Assignment.query.get_or_404(id)
    db.session.delete(assignment)
    db.session.commit()

    return redirect(url_for('main.dashboard'))

@main.route('/faculty-list')
@login_required
def faculty_list():
    if current_user.role != "admin":
        return "Access Denied: Admins Only"
    
    faculty_members = Faculty.query.all()
    
    # Calculate workload info for each faculty
    faculty_data = []
    for faculty in faculty_members:
        total_workload = faculty.calculate_total_workload()
        status = "Overloaded" if total_workload > faculty.max_workload else "Safe"
        faculty_data.append({
            'faculty': faculty,
            'total_workload': total_workload,
            'status': status
        })
    
    return render_template("faculty_list.html", faculty_data=faculty_data)


@main.route('/faculty/<int:id>')
@login_required
def faculty_profile(id):
    if current_user.role != "admin":
        return "Access Denied: Admins Only"
    
    faculty = Faculty.query.get_or_404(id)
    assignments = faculty.assignments
    total_workload = faculty.calculate_total_workload()
    workload_percentage = (total_workload / faculty.max_workload * 100) if faculty.max_workload > 0 else 0
    
    return render_template(
        "faculty_profile.html",
        faculty=faculty,
        assignments=assignments,
        total_workload=total_workload,
        workload_percentage=workload_percentage
    )


@main.route('/subject-list')
@login_required
def subject_list():
    if current_user.role != "admin":
        return "Access Denied: Admins Only"
    
    subjects = Subject.query.all()
    
    # Build subject data with assignment counts
    subject_data = []
    for subject in subjects:
        assignment_count = Assignment.query.filter_by(subject_id=subject.id).count()
        subject_data.append({
            'subject': subject,
            'assignment_count': assignment_count
        })
    
    return render_template("subject_list.html", subject_data=subject_data)


@main.route('/delete-subject/<int:id>', methods=['POST'])
@login_required
def delete_subject(id):
    if current_user.role != "admin":
        return "Access Denied: Admins Only"
    
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    
    return redirect(url_for('main.subject_list'))


@main.route('/assignment-list')
@login_required
def assignment_list():
    if current_user.role != "admin":
        return "Access Denied: Admins Only"
    
    # Get filter parameter from query string
    filter_year = request.args.get('academic_year', None)
    
    # Get all unique academic years for dropdown
    all_assignments = Assignment.query.all()
    academic_years = sorted(list(set([a.academic_year for a in all_assignments])), reverse=True)
    
    # Apply filter if specified
    if filter_year:
        assignments = Assignment.query.filter_by(academic_year=filter_year).all()
    else:
        assignments = all_assignments
    
    # Build assignment data with faculty and subject info
    assignment_data = []
    for assignment in assignments:
        assignment_data.append({
            'assignment': assignment,
            'faculty_name': assignment.faculty.name,
            'department': assignment.faculty.department,
            'subject_name': assignment.subject.subject_name,
            'course_code': assignment.subject.course_code,
            'class_division': assignment.class_division,
            'semester': assignment.semester,
            'academic_year': assignment.academic_year,
            'hours_per_week': assignment.subject.hours_per_week,
            'is_lab': assignment.subject.is_lab
        })
    
    return render_template(
        "assignment_list.html",
        assignment_data=assignment_data,
        academic_years=academic_years,
        selected_year=filter_year
    )


@main.route('/add-duty', methods=['GET', 'POST'])
@login_required
def add_duty():
    if current_user.role != "admin":
        return "Access Denied: Admins Only"
    
    if request.method == 'POST':
        duty_name = request.form.get('duty_name')
        category = request.form.get('category')
        duration_type = request.form.get('duration_type')
        hours = request.form.get('hours')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        academic_year = request.form.get('academic_year')
        
        from datetime import datetime
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return "Invalid date format. Use YYYY-MM-DD"
        
        if start_date_obj >= end_date_obj:
            return "End date must be after start date!"
        
        duty = AdditionalDuty(
            duty_name=duty_name,
            category=category,
            duration_type=duration_type,
            hours=int(hours),
            start_date=start_date_obj,
            end_date=end_date_obj,
            academic_year=academic_year
        )
        
        db.session.add(duty)
        db.session.commit()
        
        return redirect(url_for('main.dashboard'))
    
    return render_template("add_duty.html")


@main.route('/assign-duty', methods=['GET', 'POST'])
@login_required
def assign_duty():
    if current_user.role != "admin":
        return "Access Denied: Admins Only"
    
    faculties = Faculty.query.all()
    # Show only unassigned duties
    duties = AdditionalDuty.query.filter_by(faculty_id=None).all()
    
    if request.method == 'POST':
        faculty_id = request.form.get('faculty_id')
        duty_id = request.form.get('duty_id')
        
        faculty = Faculty.query.get(int(faculty_id))
        duty = AdditionalDuty.query.get(int(duty_id))
        
        if not faculty or not duty:
            return "Faculty or Duty not found!"
        
        # Check if faculty already has this duty assigned
        existing = AdditionalDuty.query.filter_by(
            faculty_id=int(faculty_id),
            duty_name=duty.duty_name,
            start_date=duty.start_date
        ).first()
        
        if existing and existing.id != int(duty_id):
            return "This duty is already assigned to this faculty for this period!"
        
        # Assign the duty to faculty
        duty.faculty_id = int(faculty_id)
        db.session.commit()
        
        return redirect(url_for('main.dashboard'))
    
    return render_template("assign_duty.html", faculties=faculties, duties=duties)


@main.route('/duty-list')
@login_required
def duty_list():
    if current_user.role != "admin":
        return "Access Denied: Admins Only"
    
    duties = AdditionalDuty.query.all()
    
    # Build duty data with faculty info
    duty_data = []
    for duty in duties:
        duty_data.append({
            'duty': duty,
            'faculty_name': duty.faculty.name if duty.faculty_id else 'Unassigned',
            'category': duty.category,
            'duration_type': duty.duration_type,
            'hours': duty.hours,
            'start_date': duty.start_date.strftime('%Y-%m-%d'),
            'end_date': duty.end_date.strftime('%Y-%m-%d'),
            'duration_days': duty.duration_days(),
            'is_active': duty.is_active(),
            'academic_year': duty.academic_year
        })
    
    return render_template("duty_list.html", duty_data=duty_data)


@main.route('/delete-duty/<int:id>', methods=['POST'])
@login_required
def delete_duty(id):
    if current_user.role != "admin":
        return "Access Denied: Admins Only"
    
    duty = AdditionalDuty.query.get_or_404(id)
    db.session.delete(duty)
    db.session.commit()
    
    return redirect(url_for('main.duty_list'))


@main.route('/my-profile', methods=['GET', 'POST'])
@login_required
def my_profile():
    def render_profile(error=None, success=None):
        total_workload = current_user.calculate_total_workload()
        teaching_hours = sum([a.subject.hours_per_week for a in current_user.assignments])
        duty_hours = sum([d.hours for d in current_user.duties if d.faculty_id == current_user.id])
        workload_percentage = (total_workload / current_user.max_workload * 100) if current_user.max_workload > 0 else 0
        return render_template(
            "my_profile.html",
            teaching_hours=teaching_hours,
            duty_hours=duty_hours,
            total_workload=total_workload,
            workload_percentage=workload_percentage,
            error=error,
            success=success
        )

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not current_password or not new_password or not confirm_password:
            return render_profile(error="All password fields are required!")

        if not current_user.check_password(current_password):
            return render_profile(error="Current password is incorrect!")

        if new_password != confirm_password:
            return render_profile(error="Passwords do not match!")

        if len(new_password) < 6:
            return render_profile(error="Password must be at least 6 characters long!")

        current_user.set_password(new_password)
        db.session.commit()
        return render_profile(success="Password changed successfully!")

    return render_profile()


@main.route('/faculty/timetable')
@login_required
def faculty_timetable():
    """Display the logged-in faculty member's weekly timetable"""
    # Get academic year from query string (default to latest)
    academic_year = request.args.get('academic_year', '2025-26')
    
    # Get faculty's timetable entries
    timetable_entries = Timetable.query.filter_by(
        faculty_id=current_user.id,
        academic_year=academic_year
    ).all()
    
    # Organize timetable by day and hour
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = list(range(1, 7))
    
    # Create a 2D grid: grid[day][hour] = timetable entry
    timetable_grid = {}
    for day in days:
        timetable_grid[day] = {}
        for hour in hours:
            timetable_grid[day][hour] = None
    
    # Fill the grid with timetable data
    for entry in timetable_entries:
        day = entry.timeslot.day
        hour = entry.timeslot.hour
        timetable_grid[day][hour] = {
            'subject': entry.subject.subject_name,
            'class': entry.class_obj.class_name,
            'course_code': entry.subject.course_code,
            'is_lab': entry.subject.is_lab
        }
    
    return render_template(
        'faculty_timetable.html',
        timetable_grid=timetable_grid,
        days=days,
        hours=hours,
        academic_year=academic_year,
        faculty_name=current_user.name
    )


@main.route('/class/<int:class_id>/timetable')
def class_timetable(class_id):
    """Display the timetable for a specific class"""
    # Get the class
    class_obj = Class.query.get_or_404(class_id)
    
    # Get academic year from query string (default to latest)
    academic_year = request.args.get('academic_year', '2025-26')
    
    # Get class's timetable entries
    timetable_entries = Timetable.query.filter_by(
        class_id=class_id,
        academic_year=academic_year
    ).all()
    
    # Organize timetable by day and hour
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = list(range(1, 7))
    
    # Create a 2D grid: grid[day][hour] = timetable entry
    timetable_grid = {}
    for day in days:
        timetable_grid[day] = {}
        for hour in hours:
            timetable_grid[day][hour] = None
    
    # Fill the grid with timetable data
    for entry in timetable_entries:
        day = entry.timeslot.day
        hour = entry.timeslot.hour
        timetable_grid[day][hour] = {
            'subject': entry.subject.subject_name,
            'faculty': entry.faculty_obj.name,
            'course_code': entry.subject.course_code,
            'is_lab': entry.subject.is_lab
        }
    
    return render_template(
        'class_timetable.html',
        timetable_grid=timetable_grid,
        days=days,
        hours=hours,
        academic_year=academic_year,
        class_name=class_obj.class_name,
        semester=class_obj.semester,
        department=class_obj.department
    )


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))
