# LearnOnline.cc

## Introduction

LearnOnline.cc is a gamified vocational training platform using the Australian Quality Training Framework (AQTF) data to provide structured, nationally recognized training content with game mechanics to enhance learner engagement and motivation. The platform integrates with Training.gov.au (TGA) to fetch and process training packages, units of competency, and their elements and performance criteria.

I was previously the developer of NTISthis, a website that leveraged AQTF qualifications to generate assessment templates for vocational education. While NTISthis provided valuable tools for educators, the operational costs became unsustainable, leading me to discontinue the service.

Now, with LearnOnline.cc, I'm experimenting with a more flexible and exploratory approach — what's' called "vibe programming". I'm using a mix of tools and AI assistants, including notbooklm, clive, roo, Copilot, Claude, and cline, to find what best fits my workflow. As a result, the codebase may appear a bit chaotic at times, reflecting this experimental process.

## Setup

To get started with LearnOnline.cc, you'll need [Docker](https://www.docker.com/products/docker-desktop/) installed on your system.

1. **Clone the repository:**
   ```sh
   git clone https://github.com/botheredbybees/learnonline.cc.git
   cd learnonline.cc
   ```

2. **Run the Docker containers:**
   ```sh
   docker-compose up --build
   ```

   This will build and start all required services.

## TGA Integration

LearnOnline.cc integrates with Training.gov.au (TGA) to fetch and process training packages, units of competency, qualifications, and skillsets. The integration provides the following features:

- Sync training packages from TGA API
- Extract elements and performance criteria from unit XML files
- Process locally stored XML files
- Admin interface for managing TGA data

For more information on the TGA integration, see the [TGA Integration Documentation](docs/technical/tga_integration.md) and [TGA Testing Documentation](docs/technical/tga_testing.md).

## Troubleshooting

If you encounter issues with Docker containers, try the following commands:

- **Stop and remove all containers and volumes:**
  ```sh
  docker-compose down --volumes
  ```

- **List all containers (including stopped ones):**
  ```sh
  docker ps -a
  ```

- **Remove all stopped containers:**
  ```sh
  docker container prune -f
  ```
## Accessing Services

Once the Docker containers are running, you can access the services in your browser at the following endpoints:

- **Frontend:**  
  [http://localhost:8080](http://localhost:8080)  
  The main user interface for LearnOnline.cc.

- **Backend API (Swagger/OpenAPI docs):**  
  [http://localhost:8000/docs](http://localhost:8000/docs)  
  Interactive API documentation and testing.

*Note: Additional services like Streamlit, Grafana, Prometheus, and the ELK stack will be added in future iterations as needed.*

## Admin Interface

An administration interface is available at [http://localhost:8080/admin](http://localhost:8080/admin) for users with admin privileges. This interface allows:

- Viewing all training packages in the system
- Syncing training packages, units, qualifications, and skillsets from TGA
- Monitoring background tasks

To create an admin user, set the `is_admin` flag to `true` in the database for your user.

If you have changed any ports in your `docker-compose.yml` file, adjust the URLs accordingly.

## echnical Documentation

### [LearnOnline Concept Document](docs/learnonline_concept.md)
This document outlines the vision, target audience, key features, and development roadmap for the LearnOnline.cc platform. It serves as a high-level overview of the project.

### [System Components Technical Specifications](docs/technical/system_components.md)
This document provides detailed technical specifications for the LearnOnline.cc platform, including system components, AI/ML integrations, content delivery mechanisms, and development environment setup.

### [User Interaction Technical Specifications](docs/technical/user_interaction.md)
This document describes the technical details of user interaction features, including real-time progress tracking, points and achievement systems, team management, and performance metrics.

### [Integration Points Technical Specifications](docs/technical/integration_points.md)
This document explains the integration points with external systems, such as the Training.gov.au SOAP API, Gemini API, H5P, and Streamlit, along with error handling and monitoring strategies.

### [Content Generation Technical Specifications](docs/technical/content_generation.md)
This document details the content generation process using AI/ML models, including unit summaries, assessment questions, and learning resources, as well as quality assurance and caching strategies.

### [AQTF Data Integration Technical Specifications](docs/technical/aqtf_integration.md)
This document provides the technical details for integrating AQTF data, including SOAP API operations, database synchronization, XML data processing, and performance optimization.