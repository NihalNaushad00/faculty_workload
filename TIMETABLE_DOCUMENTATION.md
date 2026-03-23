# 📅 Timetable System Documentation

## Overview
The Faculty Workload Management System has been extended with a complete timetable management system. This allows you to schedule faculty to teach subjects to specific classes at specific times.

---

## New Database Models

### 1. **TimeSlot Model**
Represents a time slot in the timetable (day + hour).

**Attributes:**
- `id` (Integer, Primary Key)
- `day` (String) - Monday to Friday
- `hour` (Integer) - Hours 1-6
- `created_at` (DateTime) - Creation timestamp

**Example Data:**
```
Monday Hour 1, Monday Hour 2, ..., Friday Hour 6
Total: 30 timeslots (5 days × 6 hours)
```

---

### 2. **Class Model**
Represents a student class/section in a particular semester.

**Attributes:**
- `id` (Integer, Primary Key)
- `class_name` (String, Unique) - e.g., "S3-A", "S5-B"
- `semester` (Integer) - Semester number (1-8)
- `department` (String) - e.g., "Computer Science"
- `created_at` (DateTime)

**Example Data:**
```
S1-A (Sem 1, Computer Science)
S1-B (Sem 1, Computer Science)
S3-A (Sem 3, Computer Science)
...
Total: 12 classes (Computer Science department)
```

---

### 3. **Timetable Model**
Links a faculty member, subject, and timeslot for a specific class.

**Attributes:**
- `id` (Integer, Primary Key)
- `class_id` (FK to Class)
- `subject_id` (FK to Subject)
- `faculty_id` (FK to Faculty)
- `timeslot_id` (FK to TimeSlot)
- `academic_year` (String) - e.g., "2025-26"
- `semester` (Integer)
- `created_at` (DateTime)

**Relationships:**
- Class → Timetable (Many-to-Many)
- Subject → Timetable (via timetable relationship)
- Faculty → Timetable (via faculty_obj backref)
- TimeSlot → Timetable (via timeslot backref)

---

## Constraints

### Unique Constraints

1. **Unique Class-TimeSlot**
   - **Name:** `unique_class_timeslot`
   - **Constraint:** `(class_id, timeslot_id)`
   - **Purpose:** A class cannot have two subjects at the same time
   - **Example:** Class S3-A cannot have both Data Structures and DBMS in Monday Hour 1

2. **Unique Faculty-TimeSlot**
   - **Name:** `unique_faculty_timeslot`
   - **Constraint:** `(faculty_id, timeslot_id)`
   - **Purpose:** A faculty cannot teach two classes at the same time
   - **Example:** Prof. Priya cannot teach S3-A and S5-B simultaneously

---

## Relationships

### From Faculty Model
```python
faculty.timetables  # All timetable entries where this faculty teaches
```

### From Class Model
```python
class_obj.timetables  # All timetable entries for this class
```

### From TimeSlot Model
```python
timeslot.timetables  # All classes at this time slot
```

### From Subject Model
```python
subject.timetables  # All timetable entries for this subject
```

---

## Database Tables Structure

### timeslot Table
```
id (PK)  | day       | hour | created_at
---------|-----------|------|------------------------
1        | Monday    | 1    | 2026-03-04 11:30:00
2        | Monday    | 2    | 2026-03-04 11:30:00
...
30       | Friday    | 6    | 2026-03-04 11:30:00
```

### class Table
```
id (PK) | class_name | semester | department        | created_at
--------|------------|----------|-------------------|------------------------
1       | S1-A       | 1        | Computer Science  | 2026-03-04 11:35:00
2       | S1-B       | 1        | Computer Science  | 2026-03-04 11:35:00
3       | S1-C       | 1        | Computer Science  | 2026-03-04 11:35:00
...
12      | S7-C       | 7        | Computer Science  | 2026-03-04 11:35:00
```

### timetable Table
```
id | class_id | subject_id | faculty_id | timeslot_id | academic_year | semester | created_at
---|----------|-----------|-----------|------------|-------------|----------|------------------------
1  | 1        | 101       | 1         | 1          | 2025-26     | 1        | (when created)
2  | 2        | 101       | 2         | 2          | 2025-26     | 1        | (when created)
```

---

## Current Data

**TimeSlots Initialized:**
- Days: Monday to Friday
- Hours: 1 to 6
- Total: 30 unique timeslots

**Classes Initialized:**
- Computer Science Department:
  - Semesters: 1, 3, 5, 7
  - Divisions: A, B, C (for each semester)
  - Total: 12 classes

---

## Usage Examples

### 1. Assign Subject to Class
```python
from app.models import Timetable, TimeSlot, Subject, Faculty, Class

# Create a timetable entry
timetable = Timetable(
    class_id=1,              # S1-A
    subject_id=1,            # Data Structures
    faculty_id=1,            # Dr. Rajesh Kumar
    timeslot_id=1,           # Monday Hour 1
    academic_year='2025-26',
    semester=1
)
db.session.add(timetable)
db.session.commit()
```

### 2. Check Faculty Schedule
```python
# Get all classes a faculty teaches
faculty = Faculty.query.get(1)
for timetable_entry in faculty.timetables:
    print(f"{timetable_entry.class_obj.class_name} - {timetable_entry.timeslot.day} Hour {timetable_entry.timeslot.hour}")
```

### 3. Check Class Schedule
```python
# Get all subjects in a class
class_obj = Class.query.get(1)
for timetable_entry in class_obj.timetables:
    print(f"{timetable_entry.subject.subject_name} by {timetable_entry.faculty_obj.name}")
```

### 4. View TimeSlot Occupancy
```python
# Get all classes at a specific timeslot
timeslot = TimeSlot.query.filter_by(day='Monday', hour=1).first()
for entry in timeslot.timetables:
    print(f"Class {entry.class_obj.class_name}: {entry.subject.subject_name}")
```

---

## Backward Compatibility

✅ **Existing models remain unchanged:**
- Faculty model updated (added timetables relationship)
- Subject model unchanged (has timetables backref)
- Assignment model unchanged (different use case - tracks faculty-subject-class linkage)
- AdditionalDuty model unchanged

✅ **No data loss:** All existing data in faculty.db is preserved

---

## Next Steps

To add timetable entries to the system:

1. **Create Routes:** Add Flask routes for creating/editing timetables
2. **Create Templates:** Build HTML forms for timetable management
3. **Add Conflict Detection:** Check for scheduling conflicts before saving
4. **Generate Reports:** Create views to display timetables for classes/faculty
5. **Add Validation:** Ensure subject semester matches class semester

---

## Initialization Scripts

Run the following to initialize timetable base data:

```bash
# Initialize timeslots and classes
python3 init_timetable.py
```

This creates:
- 30 TimeSlots (Monday-Friday, Hours 1-6)
- 12 Computer Science Classes (S1-A/B/C, S3-A/B/C, S5-A/B/C, S7-A/B/C)

---

## ⚠️ Important Notes

1. **Timeslot/Class Management:** Currently, timeslots and classes are pre-configured. You may want to add admin UI to add more classes from other departments later.

2. **Conflict Prevention:** The database constraints prevent:
   - Same class having two subjects at same time
   - Same faculty teaching two classes at same time

3. **Table Names:** 
   - TimeSlot → `timeslot`
   - Class → `class`
   - Timetable → `timetable`

4. **Academic Year:** Always specify academic_year (e.g., "2025-26") when creating timetables

---

## File Locations

- **Models:** `/app/models.py`
- **Initialization Script:** `/init_timetable.py`

---

**Status:** ✅ Complete and Ready to Use
