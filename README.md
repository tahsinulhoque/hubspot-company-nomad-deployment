# HubSpot Company -- Nomad & Consul Deployment

A containerized HubSpot data extraction service deployed on a
single-node HashiCorp Nomad environment with Consul service discovery.

This repository focuses on deploying the existing HubSpot Extraction
Service. The application uses Flask-RESTX, SQLAlchemy, and PostgreSQL,
and provides REST API endpoints for extracting and monitoring HubSpot
company and deal data.

## Project Objectives

-   Containerize the application using the staging Dockerfile.
-   Run the application as a workload managed by HashiCorp Nomad.
-   Register the application with Consul for service discovery.
-   Configure CPU and memory resource constraints.
-   Configure application health checks.
-   Use a static application port.
-   Verify the application through its HTTP endpoint, Nomad UI, and
    Consul.
-   Automate image build and deployment through GitHub Actions.

## Technology Stack

  Component                Technology
  ------------------------ -----------------------------
  Application              Python, Flask-RESTX
  Database                 PostgreSQL
  Containerization         Docker
  Workload orchestration   HashiCorp Nomad
  Service discovery        HashiCorp Consul
  CI/CD                    GitHub Actions
  Container build file     `docker/Dockerfile.staging`

## Application Overview

The service provides a scan-based REST API for HubSpot data extraction.

Main capabilities:

-   Extract HubSpot companies, deals, and pipelines.
-   Track extraction progress using scan IDs.
-   Retrieve extraction results.
-   Export extracted data as CSV.
-   Monitor application and database health.
-   Provide interactive API documentation.

### Important API Endpoints

  Endpoint                  Method   Purpose
  ------------------------- -------- -----------------------------
  `/scan/start`             POST     Start a data extraction
  `/scan/status/{scanId}`   GET      Check extraction progress
  `/scan/result/{scanId}`   GET      Retrieve extraction results
  `/scan/stats`             GET      View service statistics
  `/scan/health`            GET      Check application health

The application listens on container port **5104**.

## Deployment Architecture

The target environment is a single-node Nomad and Consul setup.

``` text
                 GitHub Repository
                        |
                        v
                 GitHub Actions
                        |
                 Build Container Image
                        |
                        v
                 Container Registry
                        |
                        v
             Nomad Client (Single Node)
                        |
                  Docker Workload
                        |
              HubSpot Extraction API
                        |
                   PostgreSQL

             Consul Service Registration
                        |
                 Service Discovery
```

## Nomad and Consul Deployment Requirements

The deployment is intended to include:

-   A Nomad job specification for the application.
-   Docker task configuration using the staging image.
-   Static port allocation for the application.
-   CPU and memory resource reservations/limits.
-   HTTP health checking against `/scan/health`.
-   Consul service registration.
-   Consul health-check integration.
-   Consul DNS-based service discovery.

## CI/CD Workflow

GitHub Actions will automate the deployment lifecycle:

1.  Detect changes pushed to the configured branch.
2.  Build the application container image.
3.  Run configured validation and image checks.
4.  Push the image to the selected container registry.
5.  Deploy or update the Nomad job.
6.  Verify the deployment status.

Sensitive values such as registry credentials, deployment credentials,
database credentials, and HubSpot tokens must be stored as GitHub
Actions secrets or another appropriate secret-management mechanism. They
must not be committed to the repository.

## Current Progress

  Task                                       Status
  ------------------------------------------ ----------
  Repository setup                           Complete
  Application and Dockerfile review          Complete
  Staging Docker image build                 Complete
  Local PostgreSQL availability              Verified
  Local application container health check   Healthy
  Nomad single-node setup                    Pending
  Consul setup and service registration      Pending
  Nomad job deployment                       Pending
  GitHub Actions CI/CD                       Pending
  End-to-end deployment verification         Pending

## Repository Structure

``` text
.
├── api/
├── docker/
│   └── Dockerfile.staging
├── docs/
├── models/
├── postman/
├── requirements/
├── services/
├── tests/
├── tools/
├── utils/
├── app.py
├── config.py
├── loki_logger.py
├── readme.md
└── setup.ps1
```

## Configuration and Secrets

Configure environment-specific values outside source control. The
application deployment requires the appropriate database connection
configuration. HubSpot credentials are required for live HubSpot
extraction operations.

Use `.env.example` as a reference for application configuration keys. Do
not put real credentials in `.env.example`, source files, Nomad job
files, or this README.

## Verification Goals

The deployment will be considered complete when:

-   The application is running as a Nomad-managed workload.
-   The Nomad allocation is healthy.
-   The application health endpoint responds successfully.
-   Consul registers the application as a healthy service.
-   The service can be discovered through Consul DNS.
-   The configured static port is reachable.
-   The GitHub Actions workflow completes a deployment successfully.

## Notes

This repository contains the application and its deployment work. Nomad
job files, Consul configuration, and CI/CD workflow documentation will
be added as those deployment stages are implemented.
