# User Favorites and Quests System

LearnOnline.cc provides a robust favorites and quests system to enhance the learning experience and user engagement.

## Features Overview

### Favorites System

Users with Player level or higher can mark their favorite content for quick access later:

- **Favorite Training Packages**: Save training packages to refer to later
- **Favorite Units**: Bookmark specific units of interest
- **Favorite Quests**: Save curated learning paths (quests) for future study

### Quests System

Quests are structured sets of units designed to provide a guided learning path:

- **Introductory Quests**: Available to guest users without registration
- **Mentor-Created Quests**: Curated by experienced mentors
- **Qualification-Based Quests**: Automatically generated from qualifications
- **Skillset-Based Quests**: Focused on building specific skillsets

## User Experience

### Guest User Journey

The platform supports a seamless onboarding path for new users:

1. Guest users can access introductory quests without creating an account
2. Progress on introductory quests is stored in browser cookies
3. Upon completing an introductory quest, guests are prompted to create an account
4. After registration, their progress is transferred to their new user account
5. New users who complete introductory quests are automatically upgraded to Player level
6. Player level users gain access to additional features like favorites and more quests

### Accessing Favorites (Player Level and Above)

1. Navigate to the user profile page
2. Click on the "Favorites" tab
3. Browse favorites by category (Training Packages, Units, or Quests)

### Using the Quests System

1. Browse available quests from the Quests page
2. Filter quests by type (Introductory, Mentor-Created, Qualification-Based, or Skillset-Based)
3. Click on a quest to view its details
4. Start a quest to begin the learning path

### Creating Quests (for Mentors)

Users with Mentor level permissions can create custom quests:

1. From the Quests page, click "Create New Quest"
2. Fill in the quest details (title, description, etc.)
3. Add units to the quest in the desired sequence
4. Set the experience points awarded for completing the quest
5. Save and publish the quest

## Technical Implementation

### Database Schema

The favorites and quests system uses the following database tables:

- `quests`: Stores quest metadata and configuration, including a flag for introductory quests
- `quest_units`: Links quests and units with sequence information
- `user_favorite_training_packages`: Records user's favorite training packages
- `user_favorite_units`: Records user's favorite units
- `user_favorite_quests`: Records user's favorite quests
- `guest_progress`: Temporarily stores guest user progress using browser cookie identifiers
- `user_quest_progress`: Records user progress on quests, including completion status

### API Endpoints

#### Quests Endpoints

- `GET /api/quests`: List available quests with filters
- `GET /api/quests/{id}`: Get details for a specific quest
- `POST /api/quests`: Create a new quest (mentor/admin only)
- `PUT /api/quests/{id}`: Update an existing quest (creator/admin only)
- `DELETE /api/quests/{id}`: Delete a quest (creator/admin only)

#### Public Endpoints (No Authentication Required)

- `GET /api/public/quests/introductory`: List all introductory quests available to guests
- `GET /api/public/quests/{id}`: Get details for a specific introductory quest
- `POST /api/public/quest-progress`: Save guest progress using cookies
- `GET /api/public/quest-progress/{guest_id}`: Get a guest user's progress
- `POST /api/public/transfer-progress`: Transfer guest progress to a user account after registration

#### Favorites Endpoints (Player Level and Above Only)

- `GET /api/favorites`: Get all favorites for the current user
- `POST /api/favorites/training-packages`: Add a training package to favorites
- `DELETE /api/favorites/training-packages/{id}`: Remove a training package from favorites
- `POST /api/favorites/units`: Add a unit to favorites
- `DELETE /api/favorites/units/{id}`: Remove a unit from favorites
- `POST /api/favorites/quests`: Add a quest to favorites
- `DELETE /api/favorites/quests/{id}`: Remove a quest from favorites

## Experience Points Integration

The quests system is integrated with the user progression model:

1. Each quest has an experience point value
2. Completing a quest awards the user with the specified experience points
3. As users accumulate experience points, they progress through levels (Guest → Player → Mentor)
4. Higher levels unlock additional capabilities, such as quest creation

## Future Enhancements

Planned enhancements for the favorites and quests system:

1. Quest progress tracking
2. Quest completion badges and certificates
3. Team quests for collaborative learning
4. Quest recommendations based on user interests and progress
