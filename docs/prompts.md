** Sprint Prefix for Code-Inclusive Workflows:**

You are a senior full-stack developer. I'm working on a gamified vocational training platform that transforms traditional vocational education into an engaging, interactive learning experience. The platform leverages the Australian Quality Training Framework (AQTF) data to provide structured, nationally recognized training content while incorporating game mechanics to enhance learner engagement and motivation with FastAPI/PostgreSQL/jQuery/Bootstrap.

For this sprint, analyze the provided source files and:
- Understand existing patterns and conventions in my codebase
- Maintain consistency with current architecture
- Identify dependencies between the files I've shared
- Propose changes that integrate cleanly with existing code
- Point out any potential breaking changes

When making suggestions:
- Reference specific functions/classes/elements from my code
- Show modifications in context, not isolated snippets
- Consider the ripple effects on other parts of the system


**Things to avoid:**

1. **Scope creep in requests** - Are you asking for too much in one sprint? LLMs work better with focused, specific tasks.

2. **Insufficient architectural context** - Even with source files, the model might not grasp your overall data flow or business logic.

3. **Integration complexity** - Changes touching multiple layers (DB → API → Frontend) are inherently slower to get right.

**Try this approach:**
- Break sprints into single-layer focuses when possible
- Start each sprint by asking "What questions do you have about the existing code before I describe what I want to build?"
- Be explicit about which files are most relevant to the current task

The key is helping the model understand not just *what* your code does, but *why* you structured it that way.


**If things have gone hopelessly wrong:**

Starting fresh with a solid foundation is often faster than trying to untangle inconsistent architecture. Here's how to salvage the good parts:

**What to definitely keep:**
- Docker configuration (containerization setup is valuable)
- Database DDL/schema (represents your data model thinking)
- API documentation (shows your requirements clearly)
- Any complex business logic in API endpoints
- Authentication/authorization code (if it works)

**What to audit before keeping:**
- API route organization - are they logically grouped?
- Database models/ORM code - do they match your DDL?
- Error handling patterns - are they consistent?
- Configuration management - is it clean?

**Restart strategy:**

1. **Foundation sprint:**
```
I'm rebuilding a FastAPI/PostgreSQL app. I have working Docker setup and database schema (attached). 

Create a clean project structure with:
- Proper FastAPI app organization (routers, dependencies, models)
- SQLAlchemy models matching my existing schema
- Consistent error handling and logging
- Clear separation of concerns

Show me the complete folder structure and core files to establish patterns for future development.
```

2. **Migration sprint:**
```
Using the established architecture, help me migrate the valuable API endpoints from my old code (attached). 

Refactor them to match the new patterns while preserving the business logic.
```

This approach lets you keep months of domain work while getting a clean, maintainable codebase. Much better than struggling with architectural debt.
Peter

**Be specific about test types and scope:**

Instead of "write tests for this," try:

**For API endpoints:**
```
Write pytest tests for this FastAPI endpoint including:
- Happy path with valid data
- Validation errors (400 responses)
- Authentication/authorization checks
- Database state verification
- Edge cases like empty/null values

Include both the test code and any necessary fixtures or setup.
```

**For database models/queries:**
```
Create tests for this SQLAlchemy model covering:
- CRUD operations
- Relationship handling
- Constraint validation
- Query performance with sample data

Show me the test data setup and teardown.
```

**For frontend JavaScript:**
```
Write tests for this jQuery function including:
- DOM manipulation verification
- AJAX call mocking
- Error handling
- User interaction simulation

Use a testing framework appropriate for jQuery/vanilla JS.
```

**Test-driven approach:**
```
Before implementing [feature], write the tests that should pass when it's complete. Include:
- Input/output expectations
- Error scenarios
- Integration points

This will guide the implementation.
```

**Key specifics to include:**
- What testing framework to use (pytest, Jest, etc.)
- Whether you want unit tests, integration tests, or both
- Mock/fixture requirements
- Coverage expectations
- How tests should integrate with your existing test suite

The more specific you are about what scenarios to test, the better coverage you'll get.

