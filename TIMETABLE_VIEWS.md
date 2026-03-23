# Faculty & Class Timetable Views

## Overview

Two new routes have been added to display timetable information in an interactive grid format:

1. **Faculty Timetable View** (`/faculty/timetable`) - Shows weekly schedule for logged-in faculty
2. **Class Timetable View** (`/class/<class_id>/timetable`) - Shows weekly schedule for any specific class

Both views display timetables as a 5-day × 6-hour grid with subject and faculty/class information.

---

## Routes

### Route 1: Faculty Timetable
**Path:** `/faculty/timetable`  
**Method:** GET  
**Authentication:** Required (Login needed)  
**Access:** Faculty members only

**URL Parameters:**
- `academic_year` (optional, query string): Filter by academic year (default: `2025-26`)
  - Example: `/faculty/timetable?academic_year=2024-25`

**Response:** HTML page displaying faculty's weekly timetable grid

#### Features:
- Grid layout: Days (Monday-Friday) × Hours (1-6)
- Shows subject name, class name, course code
- Color-coded for lab vs theory classes
- Filters by academic year
- Responsive design (mobile-friendly)
- Badge indicators for lab vs theory
- Legend explanation

#### Example Usage:
```
GET /faculty/timetable
GET /faculty/timetable?academic_year=2025-26
```

---

### Route 2: Class Timetable
**Path:** `/class/<class_id>/timetable`  
**Method:** GET  
**Authentication:** Not required (Public)  
**Access:** Anyone

**URL Parameters:**
- `class_id` (required, path): ID of the class (integer)
- `academic_year` (optional, query string): Filter by academic year (default: `2025-26`)
  - Example: `/class/1/timetable?academic_year=2024-25`

**Response:** HTML page displaying class's weekly timetable grid

#### Features:
- Grid layout: Days (Monday-Friday) × Hours (1-6)
- Shows subject name, faculty name, course code
- Color-coded for lab vs theory classes
- Displays class info (semester, department, name)
- Filters by academic year
- Responsive design with stat cards
- Status badges

#### Example Usage:
```
GET /class/1/timetable
GET /class/2/timetable?academic_year=2024-25
```

#### Finding Class IDs:
```python
from app.models import Class
classes = Class.query.all()
for c in classes:
    print(f"ID: {c.id}, Name: {c.class_name}, Semester: {c.semester}")
```

---

## Templates

### `faculty_timetable.html`
- **Purpose:** Display faculty's weekly timetable
- **Location:** `app/templates/faculty_timetable.html`
- **Context Variables:**
  - `timetable_grid`: 2D dict with day→hour→entry mapping
  - `days`: List of day names
  - `hours`: List of hour numbers (1-6)
  - `academic_year`: Selected academic year
  - `faculty_name`: Current faculty member's name

**Key Sections:**
```html
- Header with faculty name and year filter
- Timetable grid (5 days × 6 hours)
- Legend explanation (Lab vs Theory)
- Quick action buttons (Profile, Dashboard)
- Empty state message if no entries
```

### `class_timetable.html`
- **Purpose:** Display class's weekly timetable
- **Location:** `app/templates/class_timetable.html`
- **Context Variables:**
  - `timetable_grid`: 2D dict with day→hour→entry mapping
  - `days`: List of day names
  - `hours`: List of hour numbers (1-6)
  - `academic_year`: Selected academic year
  - `class_name`: Class identifier (e.g., "S1-A")
  - `semester`: Semester number
  - `department`: Department name

**Key Sections:**
```html
- Header with class badges (class, semester, department, year)
- Year filter dropdown
- Timetable grid (5 days × 6 hours)
- Class statistics cards
- Legend explanation (Lab vs Theory)
- Quick action buttons
- Empty state message if no entries
```

---

## Grid Structure

Both templates use an identical grid structure:

```
        Monday  Tuesday  Wednesday  Thursday  Friday
Hour 1   [ ]      [ ]       [ ]        [ ]      [ ]
Hour 2   [ ]      [ ]       [ ]        [ ]      [ ]
Hour 3   [ ]      [ ]       [ ]        [ ]      [ ]
Hour 4   [ ]      [ ]       [ ]        [ ]      [ ]
Hour 5   [ ]      [ ]       [ ]        [ ]      [ ]
Hour 6   [ ]      [ ]       [ ]        [ ]      [ ]
```

**Cell Contents (Faculty View):**
```
┌─────────────────────────┐
│ Subject Name (Bold)     │
│ 📁 Class Name           │
│ 🔧 Course Code          │
│ [Lab] or [Theory] Badge │
└─────────────────────────┘
```

**Cell Contents (Class View):**
```
┌─────────────────────────┐
│ Subject Name (Bold)     │
│ 👤 Faculty Name         │
│ 🔧 Course Code          │
│ [Lab] or [Theory] Badge │
└─────────────────────────┘
```

---

## Route Implementation

### Code Location
Both routes are implemented in `app/routes.py`:

```python
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
    
    # Build grid structure...
    # Return rendered template


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
    
    # Build grid structure...
    # Return rendered template
```

---

## Database Models Used

### Timetable Model
```python
class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    timeslot_id = db.Column(db.Integer, db.ForeignKey('timeslot.id'), nullable=False)
    academic_year = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Related Models
- **Subject**: Provides `subject_name`, `course_code`, `is_lab`, `hours_per_week`
- **Faculty**: Provides faculty member's `name`
- **TimeSlot**: Provides `day` (Monday-Friday) and `hour` (1-6)
- **Class**: Provides `class_name`, `semester`, `department`

---

## Features

### Faculty Timetable View
✅ Displays logged-in faculty's weekly class schedule  
✅ Shows class names and course codes  
✅ Filter by academic year  
✅ Color-coded lab vs theory classes  
✅ Responsive design (mobile optimized)  
✅ Direct link from faculty dashboard  
✅ Lab subjects highlighted in blue  
✅ Theory subjects highlighted in purple  
✅ Empty state handling  
✅ Quick navigation links  

### Class Timetable View
✅ Displays any class's weekly schedule  
✅ Shows faculty names and course codes  
✅ Filter by academic year  
✅ Color-coded lab vs theory classes  
✅ Class information cards (semester, department)  
✅ Responsive design (mobile optimized)  
✅ Lab subjects highlighted in yellow  
✅ Theory subjects highlighted in green  
✅ 404 error handling (invalid class ID)  
✅ Empty state handling  

---

## Navigation Integration

### Faculty Dashboard
A new button "📅 My Timetable" has been added to the faculty dashboard header:
```html
<a href="{{ url_for('main.faculty_timetable') }}" class="btn btn-info btn-sm">📅 My Timetable</a>
```

### Admin Dashboard (Future)
Admins can access class timetables by:
1. Navigating to `/class/<id>/timetable` directly
2. Creating a class list with timetable links

---

## Example: Finding and Viewing a Class Timetable

### Get all classes:
```bash
curl http://localhost:5001/class/1/timetable
```

### List available classes (via Python):
```python
from app.models import Class
classes = Class.query.all()
for c in classes:
    print(f"/class/{c.id}/timetable")
    
# Output examples:
# /class/1/timetable      (S1-A)
# /class/2/timetable      (S1-B)
# /class/3/timetable      (S1-C)
```

---

## Styling & Design

Both templates use:
- **Bootstrap 5.3.0** for responsive layout
- **Gradient backgrounds** matching existing design theme
- **Color-coded badges** for subject types
- **Hover effects** on table rows
- **Mobile-responsive** for all screen sizes
- **Accessible design** with semantic HTML

### Color Scheme:
- **Faculty View:**
  - Lab: Blue background (#e3f2fd), blue-left border
  - Theory: Purple background (#f3e5f5), purple-left border
  
- **Class View:**
  - Lab: Orange background (#fff3e0), red-left border
  - Theory: Light green background (#f1f8e9), green-left border

---

## Testing

### Test Faculty Timetable:
```bash
# Login as faculty
# Navigate to Dashboard
# Click "📅 My Timetable" button

# Or direct URL:
curl -b "session=..." http://localhost:5001/faculty/timetable
```

### Test Class Timetable:
```bash
# Direct URL (no login required):
curl http://localhost:5001/class/1/timetable
curl http://localhost:5001/class/2/timetable?academic_year=2025-26

# With filters:
curl http://localhost:5001/class/5/timetable?academic_year=2024-25
```

---

## Error Handling

### Faculty Timetable
- **No data:** Displays empty state message
- **Invalid academic year:** Shows empty grid
- **Not logged in:** Redirects to login page

### Class Timetable
- **Invalid class ID:** Returns 404 error page
- **No data:** Displays empty state message
- **Invalid academic year:** Shows empty grid

---

## Performance Notes

- Grid is built in-memory (fast lookup)
- Database queries optimized with filters
- No pagination needed (only 5×6=30 cells)
- Suitable for real-time display

---

## Future Enhancements

### Possible improvements:
1. **Add filter sidebar** for semester, department
2. **Export to PDF** (class/faculty schedule)
3. **Print-friendly view**
4. **Compare timetables** (faculty vs class)
5. **Conflict detection** (show clashes)
6. **Download as iCalendar** (.ics file)
7. **Mobile app integration**
8. **Email schedule to faculty**
9. **Announcement system** (changes notification)
10. **Timetable editor** (drag-drop scheduling)

---

## Summary

Two new fully-functional routes display timetable information:

| Feature | Faculty Timetable | Class Timetable |
|---------|-------------------|-----------------|
| **URL** | `/faculty/timetable` | `/class/<id>/timetable` |
| **Auth** | Required | Not required |
| **Shows** | Faculty's classes | Class's faculty |
| **Grid** | 5 days × 6 hours | 5 days × 6 hours |
| **Filters** | Academic year | Academic year |
| **Status** | ✅ Complete | ✅ Complete |

Both routes are production-ready and fully integrated with existing system!
