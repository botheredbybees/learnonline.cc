# Sprint 3: District & Certification Paths

## Overview
This sprint focuses on implementing the district layouts for certification paths (Cert I-IV) and scroll-based navigation with unlock logic. This builds upon the city map implementation from Sprint 2.

## Technical Implementation

### 1. District Layouts
- Design district layouts for each certification level (Cert I-IV)
- Implement responsive grid system for district organization
- Include visual indicators for:
  - Certification level
  - Completion status
  - Required courses
  - Elective options
- Store district data in `frontend/static/js/districts.js` with:
  - District boundaries
  - Certification requirements
  - Associated courses

### 2. Scroll Navigation
- Implement scroll-based navigation system
- Add scroll-snap functionality for smooth transitions
- Create unlock logic for:
  - Progress-based district access
  - Course prerequisites
  - Certification requirements
  - Elective completion
- Store navigation state in `frontend/static/js/navigation.js`

### 3. Elective Support
- Implement elective (side quest) system
- Add elective tracking to user profile
- Include:
  - Elective selection interface
  - Progress tracking
  - Completion rewards
  - Integration with certification path
- Store elective data in `frontend/static/js/electives.js`

## Integration Points
- Connect to existing systems:
  - User authentication (via `auth_handler.js`)
  - Progress tracking (via `user_progress.js`)
  - Certification tracking (via `certification.js`)
  - Elective management (via `electives.js`)

## Data Structure Updates
```sql
-- Add district table
CREATE TABLE districts (
    district_id SERIAL PRIMARY KEY,
    certification_level VARCHAR(10) NOT NULL,
    required_courses INTEGER[] DEFAULT '{}',
    elective_slots INTEGER DEFAULT 2,
    unlock_threshold INTEGER DEFAULT 0,
    svg_path TEXT NOT NULL
);

-- Add elective tracking table
CREATE TABLE user_electives (
    user_id INTEGER REFERENCES users(user_id),
    elective_id INTEGER REFERENCES electives(elective_id),
    completion_status BOOLEAN DEFAULT FALSE,
    completion_date TIMESTAMP,
    PRIMARY KEY (user_id, elective_id)
);
```

## UI Components
1. **District Map**
   - Location: `frontend/static/js/districts.js`
   - Features: Scroll navigation, district highlighting

2. **Certification Path**
   - Location: `frontend/static/js/certification.js`
   - Features: Progress tracking, unlock logic

3. **Elective Selection**
   - Location: `frontend/static/js/electives.js`
   - Features: Elective tracking, completion status

## Testing
1. **District Layouts**
   - Verify responsive behavior
   - Test certification level indicators

2. **Navigation**
   - Test scroll behavior
   - Verify unlock logic

3. **Electives**
   - Test elective selection
   - Verify progress tracking

## Dependencies
- Requires completion of Sprint 2 (city map)
- Uses existing authentication system
- Integrates with certification tracking

## Potential Breaking Changes
- New database tables required
- Scroll behavior may require polyfills
- Elective tracking integration