#!/usr/bin/env python3

import sys
sys.path.insert(0, '/Users/nihalnaushad/Desktop/faculty_workload')

from app import create_app, db
from app.models import AdditionalDuty, Faculty
from datetime import datetime, date, timedelta

app = create_app()

with app.app_context():
    # Delete old expired duties
    all_duties = AdditionalDuty.query.all()
    for duty in all_duties:
        if duty.end_date < date.today():
            db.session.delete(duty)
    
    db.session.commit()
    
    # Create new active duties for today onwards
    today = date.today()
    end_of_year = date(2026, 3, 31)
    
    faculty_members = Faculty.query.filter_by(role='faculty').all()
    
    duties = [
        {'faculty': faculty_members[0], 'name': 'Exam Cell - Invigilator', 'category': 'Exam', 'type': 'Weekly', 'hours': 3},
        {'faculty': faculty_members[1], 'name': 'Head of Department', 'category': 'Leadership', 'type': 'Yearly', 'hours': 5},
        {'faculty': faculty_members[2], 'name': 'Placement Officer', 'category': 'Administrative', 'type': 'Weekly', 'hours': 2},
        {'faculty': faculty_members[3], 'name': 'Workshop Coordinator', 'category': 'Research', 'type': 'Custom', 'hours': 2},
    ]
    
    for i, duty_info in enumerate(duties):
        duty = AdditionalDuty(
            faculty_id=duty_info['faculty'].id,
            duty_name=duty_info['name'],
            category=duty_info['category'],
            duration_type=duty_info['type'],
            hours=duty_info['hours'],
            start_date=today,
            end_date=end_of_year,
            academic_year='2025-26'
        )
        db.session.add(duty)
    
    db.session.commit()
    print("✅ Updated duties with current dates!")
    
    # Test
    faculty = Faculty.query.filter_by(role='faculty').first()
    print(f"\n✅ Faculty: {faculty.name}")
    print(f"   Active Duties: {len(faculty.get_active_duties())}")
    print(f"   Duty Hours: {faculty.calculate_duty_hours()}")
    print(f"   Total Workload: {faculty.calculate_total_workload()}")
