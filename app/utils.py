"""
Utility functions for Faculty Workload Management System
"""

from app import db
from app.models import TimeSlot, Class, Timetable, Assignment

MAX_DAILY_HOURS = 4


def create_timeslots():
    """Create all timeslots if they don't exist"""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    hours = list(range(1, 7))  # 1 to 6
    
    created_count = 0
    for day in days:
        for hour in hours:
            existing = TimeSlot.query.filter_by(day=day, hour=hour).first()
            if not existing:
                ts = TimeSlot(day=day, hour=hour)
                db.session.add(ts)
                created_count += 1
    
    db.session.commit()
    return created_count


def assignment_matches_class(assignment, class_obj):
    """Return True when an assignment belongs to the given class."""
    if assignment.class_id:
        return assignment.class_id == class_obj.id

    if not assignment.class_division:
        return False

    assignment_division = assignment.class_division.strip().upper()
    class_name = class_obj.class_name.strip().upper()

    if assignment_division == class_name:
        return True

    return class_name.endswith(f"-{assignment_division}")


def get_daily_scheduled_hours(academic_year, day, class_id=None, faculty_id=None):
    """Get the number of periods already scheduled for a class or faculty on a day."""
    query = Timetable.query.filter_by(academic_year=academic_year)

    if class_id is not None:
        query = query.filter_by(class_id=class_id)

    if faculty_id is not None:
        query = query.filter_by(faculty_id=faculty_id)

    return sum(1 for timetable in query.all() if timetable.timeslot.day == day)


def get_available_slots(class_id, faculty_id, academic_year, day=None, max_daily_hours=MAX_DAILY_HOURS):
    """
    Get available timeslots for a class and faculty combination
    Optionally filter by specific day
    """
    query = TimeSlot.query
    
    if day:
        query = query.filter_by(day=day)
    
    all_slots = query.all()
    available = []
    
    for slot in all_slots:
        class_daily_hours = get_daily_scheduled_hours(
            academic_year,
            slot.day,
            class_id=class_id
        )
        faculty_daily_hours = get_daily_scheduled_hours(
            academic_year,
            slot.day,
            faculty_id=faculty_id
        )

        if class_daily_hours >= max_daily_hours or faculty_daily_hours >= max_daily_hours:
            continue

        # Check if class already has a subject at this time
        class_conflict = Timetable.query.filter_by(
            class_id=class_id,
            timeslot_id=slot.id,
            academic_year=academic_year
        ).first()
        
        # Check if faculty is already scheduled at this time
        faculty_conflict = Timetable.query.filter_by(
            faculty_id=faculty_id,
            timeslot_id=slot.id,
            academic_year=academic_year
        ).first()
        
        if not class_conflict and not faculty_conflict:
            available.append(slot)
    
    return available


def get_faculty_workload_today(faculty_id, academic_year, day):
    """Get current hours scheduled for a faculty on a specific day"""
    return get_daily_scheduled_hours(
        academic_year,
        day,
        faculty_id=faculty_id
    )


def get_class_workload_today(class_id, academic_year, day):
    """Get current hours scheduled for a class on a specific day."""
    return get_daily_scheduled_hours(
        academic_year,
        day,
        class_id=class_id
    )


def find_continuous_slots(class_id, faculty_id, academic_year, duration, day=None, max_daily_hours=MAX_DAILY_HOURS):
    """
    Find continuous available slots for lab subjects
    duration: number of continuous hours needed (e.g., 3 for labs)
    """
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    if day:
        days = [day]
    
    for target_day in days:
        class_daily_hours = get_class_workload_today(class_id, academic_year, target_day)
        faculty_daily_hours = get_faculty_workload_today(faculty_id, academic_year, target_day)

        if class_daily_hours + duration > max_daily_hours:
            continue

        if faculty_daily_hours + duration > max_daily_hours:
            continue

        available = get_available_slots(
            class_id,
            faculty_id,
            academic_year,
            target_day,
            max_daily_hours=max_daily_hours
        )
        available.sort(key=lambda x: x.hour)
        
        # Try to find continuous slots
        for i in range(len(available) - duration + 1):
            # Check if slots are continuous
            is_continuous = True
            for j in range(duration):
                if available[i + j].hour != available[i].hour + j:
                    is_continuous = False
                    break
            
            if is_continuous:
                return available[i:i + duration]
    
    return []


def schedule_subject(class_id, subject_id, faculty_id, academic_year, semester, slots):
    """Create timetable entries for a subject in given slots"""
    created = 0
    
    for slot in slots:
        existing = Timetable.query.filter_by(
            class_id=class_id,
            subject_id=subject_id,
            faculty_id=faculty_id,
            timeslot_id=slot.id,
            academic_year=academic_year
        ).first()
        
        if not existing:
            timetable = Timetable(
                class_id=class_id,
                subject_id=subject_id,
                faculty_id=faculty_id,
                timeslot_id=slot.id,
                academic_year=academic_year,
                semester=semester
            )
            db.session.add(timetable)
            created += 1
    
    db.session.commit()
    return created


def get_faculty_weekly_hours(faculty_id, academic_year):
    """Get total weekly hours for a faculty"""
    return Timetable.query.filter_by(
        faculty_id=faculty_id,
        academic_year=academic_year
    ).count()


def generate_timetable(semester, academic_year):
    """
    Automatically generate timetable based on assignments
    
    Algorithm:
    1. Create timeslots
    2. Get all classes for this semester
    3. For each class, get assignments
    4. Schedule lab subjects first (need continuous 3 hours)
    5. Schedule theory subjects (distribute across week)
    6. Check constraints: faculty availability, workload, and max 4 periods/day
    
    Args:
        semester (int): Semester number (1-8)
        academic_year (str): Academic year (e.g., "2025-26")
    
    Returns:
        dict: Status message with statistics
    """
    
    try:
        # Create timeslots if not exist
        create_timeslots()
        
        # Get all classes for this semester
        classes = Class.query.filter_by(semester=semester).all()
        
        if not classes:
            return {
                'success': False,
                'message': f'No classes found for semester {semester}',
                'timetables_created': 0
            }
        
        total_timetables = 0
        failed_assignments = []
        successful_assignments = []
        assignments = Assignment.query.filter_by(
            semester=semester,
            academic_year=academic_year
        ).all()
        
        # Start clean for the target semester/year so a regenerated timetable
        # does not inherit stale entries from an earlier attempt.
        clear_timetable(semester, academic_year)

        # Process each class
        for class_obj in classes:
            class_assignments = [
                assignment for assignment in assignments
                if assignment_matches_class(assignment, class_obj)
            ]
            
            if not class_assignments:
                continue
            
            # Separate lab and theory assignments
            lab_assignments = [a for a in class_assignments if a.subject.is_lab]
            theory_assignments = [a for a in class_assignments if not a.subject.is_lab]
            
            # Schedule lab subjects first (they need continuous slots)
            for assignment in lab_assignments:
                subject = assignment.subject
                faculty = assignment.faculty
                
                # Check if faculty workload allows this
                current_load = get_faculty_weekly_hours(faculty.id, academic_year)
                if current_load + subject.hours_per_week > faculty.max_workload:
                    failed_assignments.append(
                        f"{faculty.name} - {subject.subject_name} (workload exceeded)"
                    )
                    continue
                
                # Labs should occupy one continuous block based on configured hours.
                # Try to find by day
                allocated = False
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                required_duration = max(subject.hours_per_week, 1)
                
                for attempt_day in days:
                    continuous_slots = find_continuous_slots(
                        class_obj.id,
                        faculty.id,
                        academic_year,
                        required_duration,
                        attempt_day,
                        max_daily_hours=MAX_DAILY_HOURS
                    )
                    
                    if continuous_slots and len(continuous_slots) == required_duration:
                        created = schedule_subject(
                            class_obj.id,
                            subject.id,
                            faculty.id,
                            academic_year,
                            semester,
                            continuous_slots
                        )
                        total_timetables += created
                        successful_assignments.append(
                            f"{class_obj.class_name}: {subject.course_code} ({subject.subject_name}) on {attempt_day}"
                        )
                        allocated = True
                        break
                
                if not allocated:
                    failed_assignments.append(
                        f"{class_obj.class_name} - {subject.subject_name} (no continuous slots)"
                    )
            
            # Schedule theory subjects (more flexible)
            for assignment in theory_assignments:
                subject = assignment.subject
                faculty = assignment.faculty
                
                # Check workload
                current_load = get_faculty_weekly_hours(faculty.id, academic_year)
                if current_load + subject.hours_per_week > faculty.max_workload:
                    failed_assignments.append(
                        f"{faculty.name} - {subject.subject_name} (workload exceeded)"
                    )
                    continue
                
                # Need to schedule subject.hours_per_week times
                hours_needed = subject.hours_per_week
                hours_scheduled = 0
                
                # Try to distribute across different days
                days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                day_index = 0
                
                while hours_scheduled < hours_needed and day_index < len(days) * 2:
                    current_day = days[day_index % len(days)]
                    available = get_available_slots(
                        class_obj.id,
                        faculty.id,
                        academic_year,
                        current_day,
                        max_daily_hours=MAX_DAILY_HOURS
                    )
                    
                    if available:
                        # Schedule one hour on this day
                        created = schedule_subject(
                            class_obj.id,
                            subject.id,
                            faculty.id,
                            academic_year,
                            semester,
                            [available[0]]
                        )
                        total_timetables += created
                        hours_scheduled += 1
                    
                    day_index += 1
                
                if hours_scheduled == hours_needed:
                    successful_assignments.append(
                        f"{class_obj.class_name}: {subject.course_code} ({subject.subject_name})"
                    )
                else:
                    failed_assignments.append(
                        f"{class_obj.class_name} - {subject.subject_name} "
                        f"(scheduled {hours_scheduled}/{hours_needed} hours)"
                    )
        
        # Return detailed status
        return {
            'success': True,
            'message': f'Timetable generation completed for semester {semester}, year {academic_year}',
            'timetables_created': total_timetables,
            'successful': len(successful_assignments),
            'failed': len(failed_assignments),
            'successful_assignments': successful_assignments[:10],  # Show first 10
            'failed_assignments': failed_assignments[:10],  # Show first 10
            'summary': f'{total_timetables} timetable entries created. '
                      f'{len(successful_assignments)} subjects scheduled successfully. '
                      f'{len(failed_assignments)} failed due to constraints.'
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': f'Error generating timetable: {str(e)}',
            'error': str(e),
            'timetables_created': 0
        }


def clear_timetable(semester, academic_year):
    """Clear all timetable entries for a semester and academic year"""
    count = 0
    
    timetables = Timetable.query.filter_by(
        semester=semester,
        academic_year=academic_year
    ).all()
    
    for tt in timetables:
        db.session.delete(tt)
        count += 1
    
    db.session.commit()
    return count
