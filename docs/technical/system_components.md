# System Components Technical Specifications

## Frontend (HTML + jQuery + Bootstrap)

- **Core Technologies**:
  - HTML5
  - [jQuery 3.7.1](https://jquery.com/)
  - [Bootstrap 5.3.2](https://getbootstrap.com/)
- **Server**: Nginx for static file serving
- **Build Process**: None (direct static files)
- **HTTP Client**: jQuery AJAX with Promises
- **Development Tools**:
  - Browser DevTools
  - Live server reload via Docker volumes
- **Key Features**:
  - Responsive design with Bootstrap
  - Client-side routing via custom JavaScript
  - Modular JavaScript with ES6 modules
  - AJAX-based API communication

## Backend (FastAPI)

- **Framework**: [FastAPI 0.104.1](https://fastapi.tiangolo.com/)
- **Python Version**: [Python 3.9+](https://www.python.org/)
- **Database ORM**: [SQLAlchemy 2.0.23](https://www.sqlalchemy.org/)
- **Authentication**: [JWT](https://jwt.io/) with [python-jose](https://python-jose.readthedocs.io/)
- **Password Hashing**: [passlib](https://passlib.readthedocs.io/) with [bcrypt](https://github.com/pyca/bcrypt/)
- **API Documentation**: [OpenAPI/Swagger](https://swagger.io/)
- **Testing**: [pytest](https://docs.pytest.org/)
- **Task Queue**: [Celery](https://docs.celeryq.dev/) (for async tasks)
- **Caching**: [Redis](https://redis.io/)

## Database (PostgreSQL)

- **Version**: [PostgreSQL 14](https://www.postgresql.org/)
- **Extensions**:

  - [pgcrypto](https://www.postgresql.org/docs/current/pgcrypto.html) for encryption
  - [pg_trgm](https://www.postgresql.org/docs/current/pgtrgm.html) for text search
  - [postgis](https://postgis.net/) for spatial data

- **Backup Strategy**: Daily full backups
- **Replication**: Master-Slave setup
- **Connection Pooling**: [PgBouncer](https://www.pgbouncer.org/)

## Containerization (Docker)

- **Base Images**:

  - Frontend: [node:16-alpine](https://hub.docker.com/_/node) ([Dockerfile](../frontend/Dockerfile))
  - Backend: [python:3.9-slim](https://hub.docker.com/_/python) ([Dockerfile](../backend/Dockerfile))
  - Database: [postgres:14](https://hub.docker.com/_/postgres)

- **Orchestration**: [Docker Compose](https://docs.docker.com/compose/) ([docker-compose.yml](../docker-compose.yml))
- **Networking**: Bridge network
- **Volume Management**: Named volumes
- **Environment**: .env files
- **Additional Services**:
  - [Streamlit](https://streamlit.io/) ([Dockerfile](../streamlit/Dockerfile))
  - [Redis](https://redis.io/) for caching and task queue
  - [MinIO](https://min.io/) for static file storage
  - [Prometheus](https://prometheus.io/) and [Grafana](https://grafana.com/) for monitoring
  - [ELK Stack](https://www.elastic.co/what-is/elk-stack) for logging

## AI/ML Components

- **LLM Integration**: [Gemini API](https://ai.google.dev/)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **Framework**: [LangChain](https://www.langchain.com/)
- **Model Management**: [HuggingFace Transformers](https://huggingface.co/docs/transformers/index)
- **Content Generation**: [Local LLM (llamafile)](https://github.com/Mozilla-Ocho/llamafile)
- **AI-Assisted Moderation**: Integrated for content quality review and assessment.

## Content Delivery

- **Interactive Content**: [H5P](https://h5p.org/)
- **Data Visualization**: [Streamlit](https://streamlit.io/)
- **Static File Storage**: [MinIO](https://min.io/)
- **CDN**: [Cloudflare](https://www.cloudflare.com/)
- **Media Processing**: [FFmpeg](https://ffmpeg.org/)

## Development Environment

- **Version Control**: [Git](https://git-scm.com/)
- **CI/CD**: [GitHub Actions](https://github.com/features/actions)
- **Code Quality**: [SonarQube](https://www.sonarqube.org/)
- **Monitoring**: [Prometheus](https://prometheus.io/) + [Grafana](https://grafana.com/)
- **Logging**: [ELK Stack](https://www.elastic.co/what-is/elk-stack)
- **Testing Frameworks**:
  - [Selenium](https://www.selenium.dev/) for UI testing
  - [Pytest](https://docs.pytest.org/) for backend testing

## Monitoring and Analytics

- **System Monitoring**:
  - Performance metrics
  - Error tracking
  - Usage statistics
  - Resource utilization
- **User Analytics**:
  - Engagement metrics
  - Learning outcomes
  - Progress tracking
  - Success rates