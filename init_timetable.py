#!/usr/bin/env python3
"""
Initialize TimeSlot and Class data for timetable
"""

from app import create_app, db
from app.models import TimeSlot, Class

app = create_app()

def init_timetable_data():
    with app.app_context():
        print("=" * 60)
        print("📅 INITIALIZING TIMETABLE DATA")
        print("=" * 60)
        
        # Create all database tables from models
        print("\n📊 Creating database tables...")
        db.create_all()
        print("   ✓ Database tables created")
        
        # Create TimeSlots
        print("\n⏰ Creating TimeSlots...")
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        hours = list(range(1, 7))  # 1 to 6
        
        timeslots = []
        for day in days:
            for hour in hours:
                existing = TimeSlot.query.filter_by(day=day, hour=hour).first()
                if not existing:
                    ts = TimeSlot(day=day, hour=hour)
                    timeslots.append(ts)
                    db.session.add(ts)
                    print(f"   ✓ {day} - Hour {hour}")
        
        db.session.commit()
        print(f"✅ Created {len(timeslots)} timeslots")
        
        # Create Classes
        print("\n🏫 Creating Classes...")
        department_codes = {
            'Computer Science': 'CSE',
            'Electronics': 'ECE',
            'Mechanical': 'ME',
        }
        departments = {
            'Computer Science': [1, 3, 5, 7],
            'Electronics': [1, 3, 5, 7],
            'Mechanical': [1, 3, 5, 7],
        }
        
        classes = []
        class_count = 0
        for dept, semesters in departments.items():
            dept_code = department_codes[dept]
            for semester in semesters:
                for division in ['A', 'B', 'C']:
                    class_name = f"{dept_code}-S{semester}-{division}"
                    existing = Class.query.filter_by(class_name=class_name).first()
                    if not existing:
                        cls = Class(
                            class_name=class_name,
                            semester=semester,
                            department=dept
                        )
                        classes.append(cls)
                        db.session.add(cls)
                        print(f"   ✓ {class_name} ({semester}s, {dept})")
                        class_count += 1
        
        db.session.commit()
        print(f"✅ Created {class_count} classes")
        
        print("\n" + "=" * 60)
        print("✅ TIMETABLE DATA INITIALIZED!")
        print("=" * 60)
        print("\n📊 Summary:")
        print(f"   ✓ {len(timeslots)} TimeSlots (5 days × 6 hours)")
        print(f"   ✓ {class_count} Classes (3 depts × 4 sems × 3 divs)")
        print("\nTimeSlots: Monday-Friday, Hours 1-6")
        print("Classes: CSE-S1-A/B/C, ECE-S1-A/B/C, ME-S1-A/B/C, etc.")
        print("Departments: Computer Science, Electronics, Mechanical")
        print("=" * 60)

if __name__ == '__main__':
    init_timetable_data()
