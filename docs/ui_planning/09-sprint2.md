# Sprint 2: City Map & Guild Navigation

## Overview
This sprint focuses on implementing the SVG-based city map with interactive guild navigation and NPC mentor modals. This builds upon the foundation established in Sprint 1 (Bootstrap layout and animation setup).

## Technical Implementation

### 1. SVG City Map
- Create SVG-based city map with districts for each certification level (Cert I-IV)
- Implement responsive scaling for different screen sizes
- Use GSAP for smooth transitions between map views
- Store map data in `frontend/static/js/map.js` with district coordinates and guild locations

### 2. Guild Interaction System
- Implement hover/click handlers for guild elements (jQuery)
- Add visual feedback using GSAP animations:
  - Scale and glow effects on hover
  - Pulse animation for active guilds
  - Path highlighting for navigation
- Store guild data in `frontend/static/js/guilds.js` with:
  - Guild names and positions
  - Associated certification levels
  - Required skills for each

### 3. NPC Mentor Modal
- Create reusable modal component (Bootstrap 5)
- Implement dynamic content loading based on selected guild
- Include:
  - NPC avatar (SVG)
  - Available quests (from `backend/routers/qualification.py`)
  - Progress indicators (using data from `user_progress` table)
- Animation with Anime.js for modal entrance/exit

### Integration Points
- Connect to existing systems:
  - User authentication (via `auth_handler.py`)
  - Progress tracking (via `user_progress.py`)
  - Quest data (from `training_package.py`)

### Data Structure Updates
```sql
-- Add guild mapping table
CREATE TABLE guild_mapping (
    guild_id SERIAL PRIMARY KEY,
    guild_name VARCHAR(50) NOT NULL,
    certification_level VARCHAR(10) REFERENCES certifications(level),
    svg_coordinates POINT NOT NULL,
    required_skills INTEGER[] DEFAULT '{}'
);

-- Add NPC mentor table
CREATE TABLE npc_mentors (
    mentor_id SERIAL PRIMARY KEY,
    guild_id INTEGER REFERENCES guild_mapping(guild_id),
    avatar_path VARCHAR(255),
    greeting_text TEXT,
    available_quests INTEGER[] DEFAULT '{}'
);
```

## UI Components
1. **City Map Component**
   - Location: `frontend/static/js/map.js`
   - Dependencies: GSAP, jQuery

2. **Guild Interaction**
   - Location: `frontend/static/js/guilds.js`
   - Event handlers for hover/click

3. **NPC Modal**
   - Location: `frontend/static/js/npc-modal.js`
   - Uses Bootstrap 5 modal with custom animations

## Testing
1. **Map Rendering**
   - Verify SVG renders correctly on all screen sizes
   - Test touch events for mobile

2. **Guild Interaction**
   - Test hover/click states
   - Verify animation performance

3. **NPC Modal**
   - Test dynamic content loading
   - Verify accessibility (keyboard nav, ARIA)

## Dependencies
- Requires completion of Sprint 1 (base layout)
- Uses existing auth and progress tracking systems
- Integrates with qualification router for quest data

## Potential Breaking Changes
- New database tables required
- SVG rendering may require polyfills for older browsers
- Animation performance on mobile devices