#!/usr/bin/env python3
"""
Database Seeding Script
Adds sample faculty, subjects, and duties for testing
"""

from app import create_app, db
from app.models import Faculty, Subject, Assignment, AdditionalDuty
from datetime import datetime, timedelta

app = create_app()

def seed_database():
    with app.app_context():
        print("=" * 60)
        print("🌱 SEEDING DATABASE WITH SAMPLE DATA")
        print("=" * 60)
        
        # Clear existing data
        db.drop_all()
        db.create_all()
        print("\n✅ Database tables created")
        
        # Create Admin
        print("\n📝 Creating Admin User...")
        admin = Faculty(
            name='Admin User',
            email='admin@ktu.edu',
            department='Administration',
            designation='System Administrator',
            max_workload=16,
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("   ✓ Admin created")
        
        # Create Faculty Members
        print("\n👥 Creating Faculty Members...")
        faculties = [
            Faculty(
                name='Dr. Rajesh Kumar',
                email='rajesh@ktu.edu',
                department='Computer Science',
                designation='Associate Professor',
                max_workload=16,
                role='faculty'
            ),
            Faculty(
                name='Prof. Priya Sharma',
                email='priya@ktu.edu',
                department='Computer Science',
                designation='Professor',
                max_workload=14,
                role='faculty'
            ),
            Faculty(
                name='Dr. Arun Patel',
                email='arun@ktu.edu',
                department='Electronics',
                designation='Assistant Professor',
                max_workload=18,
                role='faculty'
            ),
            Faculty(
                name='Ms. Neha Singh',
                email='neha@ktu.edu',
                department='Computer Science',
                designation='Assistant Professor',
                max_workload=18,
                role='faculty'
            ),
            Faculty(
                name='Dr. Vikram Desai',
                email='vikram@ktu.edu',
                department='Electronics',
                designation='Associate Professor',
                max_workload=16,
                role='faculty'
            ),
        ]
        
        for faculty in faculties:
            faculty.set_password('faculty123')
            db.session.add(faculty)
            print(f"   ✓ {faculty.name}")
        
        # Create Subjects
        print("\n📚 Creating Subjects...")
        subjects = [
            # Computer Science - Theory & Lab
            Subject(
                course_code='CS101',
                subject_name='Data Structures',
                subject_type='Theory',
                is_lab=False,
                hours_per_week=2,
                semester=1
            ),
            Subject(
                course_code='CS102',
                subject_name='Data Structures Lab',
                subject_type='Lab',
                is_lab=True,
                hours_per_week=3,
                semester=1
            ),
            Subject(
                course_code='CS201',
                subject_name='Database Management Systems',
                subject_type='Theory',
                is_lab=False,
                hours_per_week=2,
                semester=3
            ),
            Subject(
                course_code='CS202',
                subject_name='DBMS Lab',
                subject_type='Lab',
                is_lab=True,
                hours_per_week=3,
                semester=3
            ),
            Subject(
                course_code='CS301',
                subject_name='Web Technologies',
                subject_type='Theory',
                is_lab=False,
                hours_per_week=2,
                semester=5
            ),
            Subject(
                course_code='CS302',
                subject_name='Web Development Lab',
                subject_type='Lab',
                is_lab=True,
                hours_per_week=3,
                semester=5
            ),
            # Electronics
            Subject(
                course_code='EC101',
                subject_name='Digital Electronics',
                subject_type='Theory',
                is_lab=False,
                hours_per_week=2,
                semester=1
            ),
            Subject(
                course_code='EC102',
                subject_name='Digital Electronics Lab',
                subject_type='Lab',
                is_lab=True,
                hours_per_week=3,
                semester=1
            ),
            Subject(
                course_code='EC201',
                subject_name='Microprocessors',
                subject_type='Theory',
                is_lab=False,
                hours_per_week=2,
                semester=3
            ),
        ]
        
        for subject in subjects:
            db.session.add(subject)
            print(f"   ✓ {subject.course_code} - {subject.subject_name}")
        
        db.session.commit()
        
        # Create Assignments
        print("\n🔗 Creating Assignments (Faculty -> Subjects)...")
        assignments = [
            # Rajesh Kumar - CS Faculty
            Assignment(
                faculty_id=faculties[0].id,
                subject_id=subjects[0].id,
                class_division='A',
                semester=1,
                academic_year='2025-26'
            ),
            Assignment(
                faculty_id=faculties[0].id,
                subject_id=subjects[1].id,
                class_division='A',
                semester=1,
                academic_year='2025-26'
            ),
            # Priya Sharma - CS Faculty
            Assignment(
                faculty_id=faculties[1].id,
                subject_id=subjects[2].id,
                class_division='B',
                semester=3,
                academic_year='2025-26'
            ),
            Assignment(
                faculty_id=faculties[1].id,
                subject_id=subjects[3].id,
                class_division='B',
                semester=3,
                academic_year='2025-26'
            ),
            # Neha Singh - CS Faculty
            Assignment(
                faculty_id=faculties[3].id,
                subject_id=subjects[4].id,
                class_division='A',
                semester=5,
                academic_year='2025-26'
            ),
            # Arun Patel - Electronics Faculty
            Assignment(
                faculty_id=faculties[2].id,
                subject_id=subjects[6].id,
                class_division='A',
                semester=1,
                academic_year='2025-26'
            ),
            Assignment(
                faculty_id=faculties[2].id,
                subject_id=subjects[7].id,
                class_division='A',
                semester=1,
                academic_year='2025-26'
            ),
            # Vikram Desai - Electronics Faculty
            Assignment(
                faculty_id=faculties[4].id,
                subject_id=subjects[8].id,
                class_division='B',
                semester=3,
                academic_year='2025-26'
            ),
        ]
        
        for assignment in assignments:
            db.session.add(assignment)
            print(f"   ✓ {faculties[assignment.faculty_id-2].name} -> {subjects[assignment.subject_id-1].course_code}")
        
        db.session.commit()
        
        # Create Duties
        print("\n⚙️ Creating Duties...")
        
        today = datetime.now().date()
        academic_year_start = datetime(2025, 6, 1).date()
        academic_year_end = datetime(2026, 5, 31).date()
        
        duties = [
            # Yearly Duties (Leadership)
            AdditionalDuty(
                faculty_id=faculties[1].id,
                duty_name='Head of Department (CSE)',
                category='Leadership',
                duration_type='Yearly',
                hours=5,
                start_date=academic_year_start,
                end_date=academic_year_end,
                academic_year='2025-26'
            ),
            AdditionalDuty(
                faculty_id=faculties[4].id,
                duty_name='Placement Officer',
                category='Leadership',
                duration_type='Yearly',
                hours=4,
                start_date=academic_year_start,
                end_date=academic_year_end,
                academic_year='2025-26'
            ),
            # Weekly Duties (Exam)
            AdditionalDuty(
                faculty_id=faculties[0].id,
                duty_name='Exam Cell - Invigilator',
                category='Exam',
                duration_type='Weekly',
                hours=3,
                start_date=today,
                end_date=today + timedelta(days=6),
                academic_year='2025-26'
            ),
            AdditionalDuty(
                faculty_id=faculties[2].id,
                duty_name='Exam Cell - Paper Setter',
                category='Exam',
                duration_type='Weekly',
                hours=2,
                start_date=today,
                end_date=today + timedelta(days=6),
                academic_year='2025-26'
            ),
            # Custom Duties
            AdditionalDuty(
                faculty_id=faculties[3].id,
                duty_name='Workshop Coordinator',
                category='Administrative',
                duration_type='Custom',
                hours=2,
                start_date=datetime(2026, 3, 1).date(),
                end_date=datetime(2026, 3, 31).date(),
                academic_year='2025-26'
            ),
        ]
        
        for duty in duties:
            db.session.add(duty)
            f = Faculty.query.get(duty.faculty_id)
            faculty_name = f.name if f else 'Unassigned'
            print(f"   ✓ {duty.duty_name} -> {faculty_name} ({duty.duration_type})")
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("✅ DATABASE SEEDING COMPLETE!")
        print("=" * 60)
        print("\n📊 Summary:")
        print(f"   ✓ 1 Admin User")
        print(f"   ✓ 5 Faculty Members")
        print(f"   ✓ 9 Subjects (5 Theory + 4 Lab)")
        print(f"   ✓ 8 Assignments")
        print(f"   ✓ 5 Duties (2 Yearly + 2 Weekly + 1 Custom)")
        print("\n🔐 Login Credentials:")
        print("   Admin: admin@ktu.edu / admin123")
        print("   Faculty: rajesh@ktu.edu / faculty123")
        print("           priya@ktu.edu / faculty123")
        print("           arun@ktu.edu / faculty123")
        print("           neha@ktu.edu / faculty123")
        print("           vikram@ktu.edu / faculty123")
        print("\n" + "=" * 60)

if __name__ == '__main__':
    seed_database()
