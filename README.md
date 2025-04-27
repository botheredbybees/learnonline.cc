# LearnOnline.cc

## Introduction

LearnOnline.cc is a gamified vocational training platform using the Australian Quality Training Framework (AQTF) data to provide structured, nationally recognized training content with game mechanics to enhance learner engagement and motivation.

I was previously the developer of NTISthis, a website that leveraged AQTF qualifications to generate assessment templates for vocational education. While NTISthis provided valuable tools for educators, the operational costs became unsustainable, leading me to discontinue the service.

Now, with LearnOnline.cc, I'm experimenting with vibe programming using a mix of tools and AI assistants These include notbooklm, clive, roo, Copilot, Claude, and Cline. I hope to find what best fits my workflow. Meanwhile, the codebase may appear a bit chaotic at times, reflecting this experimental process.

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

Once the Docker containers are running, you can access the various services in your browser at the following endpoints:

- **Frontend:**  
  [http://localhost:8080](http://localhost:8080)  
  The main user interface for LearnOnline.cc.

- **Backend API (Swagger/OpenAPI docs):**  
  [http://localhost:8000/docs](http://localhost:8000/docs)  
  Interactive API documentation and testing.

- **Streamlit Dashboard:**  
  [http://localhost:8501](http://localhost:8501)  
  Data visualization and analytics.

- **Grafana (Monitoring Dashboards):**  
  [http://localhost:3001](http://localhost:3001)

- **Prometheus (Metrics):**  
  [http://localhost:9090](http://localhost:9090)

- **Kibana (Log Visualization):**  
  [http://localhost:5601](http://localhost:5601)

- **MinIO Console (Object Storage):**  
  [http://localhost:9001](http://localhost:9001)

- **Elasticsearch (API):**  
  [http://localhost:9200](http://localhost:9200)

If you have changed any ports in your `docker-compose.yml` file, adjust the URLs accordingly.

## Technical Documentation

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

## Licence

LearnOnline.cc is released under a [https://www.apache.org/licenses/LICENSE-2.0](Apache-2.0 license) . 