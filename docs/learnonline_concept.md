# LearnOnline.cc - Gamified Vocational Training Platform

## 1. Overview

### 1.1 Project Vision

LearnOnline.cc is a gamified vocational training platform that transforms traditional vocational education into an engaging, interactive learning experience. The platform leverages the Australian Quality Training Framework (AQTF) data to provide structured, nationally recognized training content while incorporating game mechanics to enhance learner engagement and motivation.

### 1.2 Target Audience

- Vocational education students
- Training providers and educators
- Industry professionals seeking upskilling
- Organizations implementing training programs

### 1.3 Key Features

- Integration with AQTF training packages, qualifications, and units
- Gamified learning experience with points, levels, and achievements
- Role-based access control with administrator, mentor, player, and guest roles
- AI-powered content generation and assessment
- Team-based learning and progress tracking
- Interactive quizzes and assessments
- Community contribution and feedback system
- Accessibility compliance with WCAG standards
- Mobile-first design with offline capabilities

## 2. Technical Architecture

### 2.1 System Components

For detailed technical specifications of all system components, see [System Components Technical Specifications](technical/system_components.md).

- Frontend: HTML5, [jQuery 3.7.1](https://jquery.com/), [Bootstrap 5.3.2](https://getbootstrap.com/)
- Backend: FastAPI (Python)
- Database: PostgreSQL
- Containerization: Docker
- AI/ML: Gemini API, LangChain, ChromaDB
- Content Delivery: Streamlit
- Testing Frameworks: Selenium for UI testing, Pytest for backend

### 2.2 Data Flow

1. AQTF Data Integration:

   For detailed specifications of the AQTF data integration, see [AQTF Integration Technical Specifications](technical/aqtf_integration.md).

   - SOAP API integration with Training.gov.au
   - XML data parsing and transformation
   - Database synchronization and updates

2. Content Generation:

   For detailed specifications of the content generation system, see [Content Generation Technical Specifications](technical/content_generation.md).

   - LLM-based content generation for units
   - Assessment question generation
   - Resource recommendation system
   - AI-assisted moderation for content quality

3. User Interaction:

   For detailed specifications of the user interaction system, see [User Interaction Technical Specifications](technical/user_interaction.md).

   - Real-time progress tracking
   - Points and achievement calculation
   - Team and individual performance metrics

### 2.3 Integration Points

For detailed specifications of all integration points, see [Integration Points Technical Specifications](technical/integration_points.md).

- Training.gov.au SOAP API
- Gemini API for content generation
- H5P for interactive content
- Streamlit for data visualization
- Flowchart visualization of integration points (to be added)

### 2.4 Security Considerations

- JWT-based authentication
- Role-based access control
- Data encryption at rest and in transit
- Regular security audits
- GDPR and Australian privacy compliance
- User consent management mechanisms (e.g., cookie banners)

## 3. User Management

### 3.1 User Types and Progression

#### Administrator

- Full system access
- AQTF data synchronization
- User management
- Content moderation
- System configuration

#### User

Users progress through the following experience levels as they gain points:

**Guest Level** (0-100 points)
- Limited content access
- Introduction to platform
- Basic course browsing

**Player Level** (101-1000 points)
- Course enrollment
- Content access
- Assessment participation
- Progress tracking
- Community contributions

**Mentor Level** (1001+ points)
- Team/class management
- Progress monitoring
- Content creation and editing
- Assessment creation
- Student performance tracking
- Introduction to platform
- Registration process

### 3.2 Permission Matrix

| Feature | Admin | User (Mentor Level) | User (Player Level) | User (Guest Level) |
|---------|-------|---------------------|--------------------|--------------------|
| AQTF Sync | ✓ | - | - | - |
| User Management | ✓ | - | - | - |
| Team Management | ✓ | ✓ | - | - |
| Content Creation | ✓ | ✓ | - | - |
| Assessment Creation | ✓ | ✓ | - | - |
| Content Access | ✓ | ✓ | ✓ | Limited |
| Progress Tracking | ✓ | ✓ | ✓ | - |
| Community Features | ✓ | ✓ | ✓ | - |

### 3.3 Experience Level System

Users progress through experience levels as they earn points:

1. **Guest Level** (0-100 points): Limited access to content, registration, basic browsing
2. **Player Level** (101-1000 points): Full access to content, assessments, community features
3. **Mentor Level** (1001+ points): Team management, content creation, assessment creation

## 4. Content Management

### 4.1 AQTF Integration

- Training Package synchronization
- Qualification mapping
- Unit of competency tracking
- Skillset management
- Assessment requirements integration

### 4.2 Content Generation

- Unit summaries
- Learning resources
- Assessment questions
- Interactive content
- Progress tracking
- AI-assisted content review and moderation

### 4.3 Content Moderation

- AI-assisted content review
- Human moderation workflow
- Quality assurance process
- Version control system

### 4.4 Update Procedures

- Automated AQTF data updates
- Content versioning
- Change management process
- User notification system

## 5. Gamification System

### 5.1 Point System

- Reading content: 10 points
- Completing quizzes: 50 points
- Contributing resources: 25 points
- Community feedback: 15 points
- Team achievements: 100 points

### 5.2 Level Progression

- Level 1: 0-100 points
- Level 2: 101-300 points
- Level 3: 301-600 points
- Level 4: 601-1000 points
- Level 5: 1001+ points

### 5.3 Achievements

- Content Master
- Quiz Champion
- Resource Contributor
- Team Player
- Community Builder

### 5.4 Leaderboards

- Individual rankings
- Team rankings
- Course-specific rankings
- Achievement-based rankings

## 6. Assessment System

### 6.1 Quiz Types

- Multiple choice
- Fill in the blank
- Step rearrangement
- Free text response
- Practical assessment

### 6.2 Grading System

- Automated grading
- Peer review
- Mentor assessment
- AI-assisted evaluation

### 6.3 Progress Tracking

- Individual progress
- Team progress
- Course completion
- Skill development

### 6.4 Feedback Mechanisms

- Automated feedback
- Peer feedback
- Mentor feedback
- AI-generated suggestions

## 7. Team/Class Management

### 7.1 Team Creation

- Team formation
- Role assignment
- Goal setting
- Progress tracking

### 7.2 Progress Monitoring

- Individual metrics
- Team metrics
- Course completion
- Skill development

### 7.3 Communication Tools

- Team chat
- Discussion forums
- Announcements
- Notifications

### 7.4 Reporting

- Progress reports
- Performance analytics
- Achievement tracking
- Skill development metrics

## 8. Development Roadmap

### Phase 1: Core Features (Q2 2025)

- Basic platform setup
  - Docker containerization
  - Database schema implementation
  - Basic API endpoints

- AQTF integration
  - SOAP API connection
  - Data synchronization
  - XML parsing

- User management
  - Authentication system
  - Role-based access
  - User profiles

- Content delivery
  - Basic unit display
  - Qualification browsing
  - Skillset navigation

### Phase 2: Gamification (Q3 2025)

- Points system
  - Point calculation
  - Achievement tracking
  - Progress visualization

- Level progression
  - Level thresholds
  - Permission unlocks
  - Progress tracking

- Achievements
  - Badge system
  - Milestone tracking
  - Reward distribution

- Leaderboards
  - Individual rankings
  - Team rankings
  - Course-specific rankings

### Phase 3: Advanced Features (Q4 2025)

- AI content generation
  - Gemini API integration
  - Content quality assessment
  - Resource generation

- Advanced assessments
  - Interactive quizzes
  - Peer review system
  - AI-assisted grading

- Team features
  - Team management
  - Progress tracking
  - Communication tools

- Community tools
  - Discussion forums
  - Resource sharing
  - Feedback system

### Phase 4: Optimization and Scale (Q1 2026)

- Performance optimization
  - Caching implementation
  - Load balancing
  - Database optimization

- Mobile responsiveness
  - Mobile-first design
  - Offline capabilities
  - Touch optimization

- Analytics and reporting
  - Advanced metrics
  - Custom reports
  - Data visualization

- Security enhancements
  - Advanced encryption
  - Audit logging
  - Security monitoring

## 9. Data Privacy and Compliance

### 9.1 Privacy Requirements

- GDPR compliance
- Australian privacy laws
- Data retention policies
- User consent management

### 9.2 Security Measures

- Data encryption
- Access control
- Audit logging
- Regular security updates

## 10. Monitoring and Analytics

### 10.1 System Monitoring

- Performance metrics
- Error tracking
- Usage statistics
- Resource utilization

### 10.2 User Analytics

- Engagement metrics
- Learning outcomes
- Progress tracking
- Success rates

## 11. Testing and Quality Assurance

### 11.1 Testing Strategy

- Unit testing
- Integration testing
- User acceptance testing
- Performance testing
- Selenium for UI testing
- Pytest for backend testing

### 11.2 Quality Metrics

- Code quality
- Performance benchmarks
- User satisfaction
- Learning outcomes

## 12. User Experience

### 12.1 Interface Design

- Responsive design
- Accessibility compliance
- Intuitive navigation
- Consistent styling

### 12.2 User Flows

- Registration process
- Course enrollment
- Assessment completion
- Progress tracking

## 13. Mobile Responsiveness

### 13.1 Design Requirements

- Mobile-first approach
- Responsive layouts
- Touch-friendly interfaces
- Offline capabilities

### 13.2 Performance Optimization

- Image optimization
- Code splitting
- Lazy loading
- Caching strategies