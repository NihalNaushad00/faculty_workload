# 📅 Timetable Generation Function Documentation

## Overview
The `generate_timetable()` function intelligently schedules faculty to teach subjects in classes based on assignment data. It automatically handles conflicts, workload constraints, and special requirements like lab continuity.

---

## Function Signature
```python
def generate_timetable(semester, academic_year):
    """
    Automatically generate timetable based on assignments
    
    Args:
        semester (int): Semester number (1-8)
        academic_year (str): Academic year (e.g., "2025-26")
    
    Returns:
        dict: Status message with statistics
    """
```

---

## Core Features

### 1. **Automatic Conflict Detection**
- ✅ Faculty cannot be scheduled in two places at once
- ✅ Classes cannot have two subjects at the same time
- ✅ Validates before creating timetable entry

### 2. **Lab Subject Handling**
- ✅ Automatically detects lab subjects (`subject.is_lab = True`)
- ✅ Allocates 3 continuous hours for labs
- ✅ Finds continuous blocks within a day

### 3. **Workload Management**
- ✅ Respects faculty `max_workload` limit
- ✅ Prevents scheduling if faculty workload exceeds limit
- ✅ Includes workload in failure reason

### 4. **Intelligent Distribution**
- ✅ Distributes theory subject hours across week
- ✅ Tries different days to avoid heavy single days
- ✅ Respects subject's `hours_per_week` requirement

### 5. **Detailed Reporting**
- ✅ Returns success/failure status
- ✅ Lists successfully scheduled subjects
- ✅ Lists failed assignments with reasons
- ✅ Provides summary statistics

---

## Algorithm Steps

```
Step 1: Create TimeSlotsIf not already created, initialize all 30 timeslots (Mon-Fri, Hours 1-6)

Step 2: Get Classes for SemesterFetch all classes belonging to the specified semester

Step 3: For Each Class:
   3a. Get Assignments - Fetch all faculty-subject assignments for this semester
   3b. Separate Assignments:
       - Lab assignments (is_lab = True)
       - Theory assignments (is_lab = False)
   
Step 4: Schedule Lab Subjects (Priority)
   4a. Check faculty workload
   4b. Find 3 continuous hours on any day
   4c. If found, create timetable entries
   4d. If not found, record failure
   
Step 5: Schedule Theory Subjects
   5a. Check faculty workload
   5b. Distribute hours_per_week across different days
   5c. Try different days cyclically until all hours scheduled
   5d. Record successes/failures
   
Step 6: Return Report
   - Total timetables created
   - Successful assignments
   - Failed assignments with reasons
   - Summary statistics
```

---

## Constraint Checking

### Before Scheduling Each Entry:

| Constraint | Check | Result if Failed |
|-----------|-------|------------------|
| **Class Availability** | No other subject in same timeslot | Slot skipped |
| **Faculty Availability** | Faculty not scheduled at same time | Slot skipped |
| **Faculty Workload** | Total hours < max_workload | Assignment skipped |
| **Lab Continuity** | 3 continuous hours available | Day skipped, try next day |
| **Hours Per Week** | Schedule exactly hours_per_week times | Partial/failed assignment |

---

## Return Value

The function returns a dictionary:

```python
{
    'success': True/False,
    'message': 'Descriptive status message',
    'timetables_created': 16,           # Total entries created
    'successful': 6,                    # Successfully scheduled subjects
    'failed': 6,                        # Failed assignments
    'successful_assignments': [...],    # List of successful schedules
    'failed_assignments': [...],        # List of failures with reasons
    'summary': 'Summary statistics'      # Human-readable summary
}
```

---

## Usage Examples

### Command Line Usage

```bash
# Generate timetable for semester 1, academic year 2025-26
python3 manage_timetable.py generate 1 2025-26

# Generate for semester 3
python3 manage_timetable.py generate 3 2025-26

# Clear timetable (with confirmation)
python3 manage_timetable.py clear 1 2025-26
```

### Python Usage in Routes

```python
from app.utils import generate_timetable

# In a Flask route
@main.route('/admin/generate-timetable/<int:semester>/<year>', methods=['POST'])
def generate_tt(semester, year):
    result = generate_timetable(semester, year)
    
    if result['success']:
        flash(f"Timetable created: {result['summary']}")
        return redirect(url_for('main.dashboard'))
    else:
        flash(f"Error: {result['message']}")
        return redirect(url_for('main.dashboard'))
```

---

## Helper Functions

### `create_timeslots()`
Creates all 30 timeslots (Monday-Friday, Hours 1-6) if they don't exist.
```python
created = create_timeslots()  # Returns number of created slots
```

### `get_available_slots(class_id, faculty_id, day=None)`
Returns list of available timeslots for a class-faculty combination.
```python
slots = get_available_slots(class_id=1, faculty_id=2, day='Monday')
# Returns: [TimeSlot, TimeSlot, ...]
```

### `find_continuous_slots(class_id, faculty_id, duration, day=None)`
Finds continuous available slots (for labs requiring 3 hours).
```python
lab_slots = find_continuous_slots(class_id=1, faculty_id=2, duration=3)
# Returns: [TimeSlot, TimeSlot, TimeSlot]  # 3 consecutive hours
```

### `get_faculty_workload_today(faculty_id, day)`
Returns hours already scheduled for faculty on a specific day.
```python
hours = get_faculty_workload_today(faculty_id=1, day='Monday')  # Returns: 5
```

### `get_faculty_weekly_hours(faculty_id, academic_year)`
Returns total weekly hours for a faculty in an academic year.
```python
total = get_faculty_weekly_hours(faculty_id=1, academic_year='2025-26')
```

### `clear_timetable(semester, academic_year)`
Deletes all timetable entries for a semester and year.
```python
deleted = clear_timetable(semester=1, academic_year='2025-26')  # Returns count
```

---

## Failure Reasons

Assignment may fail due to:

| Reason | Solution |
|--------|----------|
| **Workload exceeded** | Reduce faculty's other assignments or increase max_workload |
| **No continuous slots** | Clear some timetable entries or adjust class structure |
| **Scheduled X/Y hours** | Partial success - faculty scheduled for fewer hours than needed |
| **No classes found** | Ensure classes exist for the semester |

---

## Statistics from Test Run

```
Semester 1, Academic Year 2025-26
✅ Total Timetable Entries: 16
✅ Successfully Scheduled: 6 subjects
❌ Failed: 6 subjects (due to workload constraints)

Examples:
✅ S1-A: CS102 (Data Structures Lab) - Monday (3 continuous hours)
✅ S1-A: EC102 (Digital Electronics Lab) - Monday (3 continuous hours)
✅ S1-A: CS101 (Data Structures) - Scattered across week
❌ Dr. Rajesh Kumar - Data Structures (workload exceeded)
```

---

## Optimization Notes

### Current Implementation
- Simple greedy algorithm (works well for most cases)
- Lab subjects prioritized (scheduled before theory)
- Distributes theory subjects across week
- O(n) complexity per subject

### Potential Improvements
1. **Advanced Scheduling**: Implement backtracking for optimal scheduling
2. **Load Balancing**: Smarter distribution to avoid heavy days
3. **Preferences**: Consider faculty preferences (no classes on specific days)
4. **Room Allocation**: Include classroom availability
5. **Batch Mode**: Schedule multiple semesters at once

---

## Error Handling

The function is wrapped in try-except:

```python
try:
    # Scheduling logic
except Exception as e:
    return {
        'success': False,
        'message': f'Error generating timetable: {str(e)}',
        'error': str(e),
        'timetables_created': 0
    }
```

---

## Database Integrity

- ✅ Unique constraints enforced at database level
- ✅ All operations wrapped in transactions
- ✅ Rollback on errors
- ✅ Cascade deletes configured on models

---

## Performance Considerations

- **Time Complexity**: O(C × A × S × D × H)
  - C = Classes, A = Assignments, S = Subjects, D = Days, H = Hours
- **Space Complexity**: O(T) where T = Timetable entries
- **Recommended**: Generate once per semester, clear if conflicts arise

---

## Next Steps

1. **Add UI Route**: Create Flask route to trigger generation from admin dashboard
2. **Add Scheduling View**: Display generated timetables
3. **Add Conflict Resolution**: Manual override for specific conflicts
4. **Export to PDF**: Generate printable timetables
5. **Student View**: Allow students to see their class timetables

---

## Files

- **Function Location**: `/app/utils.py`
- **Management Script**: `/manage_timetable.py`
- **Models**: `/app/models.py` (Timetable, TimeSlot, Class)

---

**Status**: ✅ Complete and Production-Ready
