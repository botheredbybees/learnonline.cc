# Sprint 4: Training Quest (Guest Onboarding)

## Overview
This sprint implements the interactive tutorial system for guest onboarding, including avatar selection, mock unit interactions, and reward animations. Completing the tutorial becomes a prerequisite for registration.

## Technical Implementation

### 1. Avatar Selection System
- Create avatar selection interface with:
  - 6-8 default avatar options
  - Customization options (colors, accessories)
  - Preview functionality
- Store avatar data in `frontend/static/js/avatars.js`
- Save selections to temporary guest session storage

### 2. Interactive Tutorial Flow
- Implement step-by-step tutorial using:
  - GSAP for animations
  - jQuery for interactions
  - Bootstrap modals for instructions
- Include:
  - Basic navigation tutorial
  - Mock unit interaction
  - Certification path explanation
  - Reward system introduction

### 3. Mock Unit Interaction
- Create simulated unit completion flow:
  - Simple multiple-choice questions
  - Progress tracking
  - Immediate feedback
  - Animated reward sequence (GSAP/Anime.js)
- Store mock data in `frontend/static/js/mock_units.js`

### 4. Registration Gating
- Implement tutorial completion check:
  - Required before registration form appears
  - Progress saved in session storage
  - Visual indicator of completion status
- Connect to auth system in `backend/routers/auth.py`

## Data Structure Updates
```sql
-- Add tutorial tracking table
CREATE TABLE tutorial_progress (
    session_id VARCHAR(64) PRIMARY KEY,
    avatar_id INTEGER,
    steps_completed INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    data JSONB
);

-- Extend user table with tutorial status
ALTER TABLE users ADD COLUMN tutorial_completed BOOLEAN DEFAULT FALSE;
```

## UI Components
1. **Avatar Selector**
   - Location: `frontend/static/js/avatar-selector.js`
   - Features: Avatar preview, selection handling

2. **Tutorial Manager**
   - Location: `frontend/static/js/tutorial.js`
   - Features: Step progression, completion tracking

3. **Mock Unit**
   - Location: `frontend/static/js/mock-unit.js`
   - Features: Question handling, feedback display

## Testing
1. **Avatar Selection**
   - Test all avatar options
   - Verify session storage

2. **Tutorial Flow**
   - Test all tutorial steps
   - Verify completion tracking

3. **Registration Gating**
   - Test pre/post completion behavior
   - Verify auth system integration

## Dependencies
- Requires GSAP/jQuery from Sprint 1
- Integrates with auth system
- Uses session storage APIs

## Potential Breaking Changes
- New database tables required
- Session storage requirements
- Registration flow modification