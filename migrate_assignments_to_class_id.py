#!/usr/bin/env python3
"""
Migrate assignment rows from legacy class_division storage to class_id.
"""

import re

from sqlalchemy import text

from app import create_app, db
from app.models import Assignment, Class

app = create_app()


DEPARTMENT_CODES = {
    'Computer Science': 'CSE',
    'Electronics': 'ECE',
    'Mechanical': 'ME',
}


def ensure_class_id_column():
    columns = db.session.execute(text("PRAGMA table_info(assignment)")).fetchall()
    column_names = {column[1] for column in columns}

    if 'class_id' not in column_names:
        db.session.execute(text("ALTER TABLE assignment ADD COLUMN class_id INTEGER"))
        db.session.commit()


def ensure_assignment_index():
    db.session.execute(text(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_assignment_faculty_subject_class_year "
        "ON assignment (faculty_id, subject_id, class_id, academic_year) "
        "WHERE class_id IS NOT NULL"
    ))
    db.session.commit()


def department_class_name(department, semester, division):
    dept_code = DEPARTMENT_CODES.get(department, department[:3].upper())
    return f"{dept_code}-S{semester}-{division}"


def ensure_standard_classes():
    created = 0
    semesters = [1, 3, 5, 7]
    divisions = ['A', 'B', 'C']

    for department, dept_code in DEPARTMENT_CODES.items():
        for semester in semesters:
            for division in divisions:
                class_name = f"{dept_code}-S{semester}-{division}"
                existing = Class.query.filter_by(class_name=class_name).first()
                if existing:
                    continue

                db.session.add(Class(
                    class_name=class_name,
                    semester=semester,
                    department=department
                ))
                created += 1

    db.session.commit()
    return created


def extract_division_token(raw_value):
    if not raw_value:
        return None

    cleaned = raw_value.strip().upper()
    parts = cleaned.split('-')
    return parts[-1] if parts else cleaned


def resolve_class_for_assignment(assignment):
    if assignment.class_id:
        return assignment.class_obj

    faculty_department = assignment.faculty.department
    division = extract_division_token(assignment.class_division)
    if not division:
        return None

    direct_match = Class.query.filter_by(class_name=assignment.class_division).first()
    if direct_match:
        return direct_match

    target_name = department_class_name(faculty_department, assignment.semester, division)
    class_obj = Class.query.filter_by(class_name=target_name).first()
    if class_obj:
        return class_obj

    class_obj = Class(
        class_name=target_name,
        semester=assignment.semester,
        department=faculty_department
    )
    db.session.add(class_obj)
    db.session.flush()
    return class_obj


def cleanup_legacy_classes():
    removed = 0
    legacy_pattern = re.compile(r"^S\d+-[A-Z]$")

    for class_obj in Class.query.all():
        if not legacy_pattern.match(class_obj.class_name):
            continue

        if class_obj.assignments or class_obj.timetables:
            continue

        db.session.delete(class_obj)
        removed += 1

    db.session.commit()
    return removed


def migrate():
    with app.app_context():
        print("=" * 70)
        print("ASSIGNMENT CLASS MIGRATION")
        print("=" * 70)

        ensure_class_id_column()
        created_classes = ensure_standard_classes()
        migrated = 0
        skipped = []

        assignments = Assignment.query.order_by(Assignment.id).all()
        for assignment in assignments:
            class_obj = resolve_class_for_assignment(assignment)
            if not class_obj:
                skipped.append(assignment.id)
                continue

            assignment.class_id = class_obj.id
            assignment.class_division = class_obj.class_name
            migrated += 1

        db.session.commit()
        ensure_assignment_index()
        removed_classes = cleanup_legacy_classes()

        print(f"Created standardized classes: {created_classes}")
        print(f"Migrated assignments: {migrated}")
        print(f"Removed legacy classes: {removed_classes}")
        if skipped:
            print(f"Skipped assignments: {skipped}")
        else:
            print("Skipped assignments: none")
        print("Next step: regenerate timetable for each semester/year in use.")
        print("=" * 70)


if __name__ == '__main__':
    migrate()
