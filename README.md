# HubSpot Company - Nomad Deployment

A deployment-focused implementation of the HubSpot Company Extraction Service using Docker, HashiCorp Nomad, Consul service discovery, and GitHub Actions CI/CD.

## Project Overview

This project automates the build, image publishing, and deployment of the HubSpot Company application to a single-node Nomad environment. GitHub Actions runs on a self-hosted Linux runner in WSL Ubuntu, builds the staging Docker image, pushes it to Docker Hub, and submits the Nomad job specification for deployment.

### Technology Stack

- **Application:** Flask served by Gunicorn
- **Containerization:** Docker
- **Container build file:** `docker/Dockerfile.staging`
- **Orchestration:** HashiCorp Nomad (single-node)
- **Service discovery and health checks:** HashiCorp Consul
- **CI/CD:** GitHub Actions
- **CI/CD execution environment:** Self-hosted Linux runner on WSL Ubuntu
- **Image registry:** Docker Hub
- **Database:** PostgreSQL running externally in Docker Desktop

## Architecture Diagram

The diagram below shows the implemented deployment flow, including the GitHub Actions self-hosted runner, Docker Hub image publishing, Nomad deployment, Consul registration and health checks, Consul DNS discovery, and the external PostgreSQL database.

![HubSpot Company Nomad Deployment Architecture](screenshots/HubSpot%20Nomad%20Deployment%20Architecture.png)

## Deployment Flow

1. The developer pushes application or deployment changes to the GitHub repository's `main` branch.
2. GitHub Actions assigns the workflow to the online self-hosted runner running in WSL Ubuntu.
3. The runner checks out the repository and builds the Docker image using `docker/Dockerfile.staging`.
4. The runner authenticates to Docker Hub and pushes the image with the `staging` tag and the Git commit SHA tag.
5. The workflow submits `nomad/hubspot-company.nomad.hcl` to the Nomad API.
6. Nomad schedules and runs the application container using the configured resource limits and static port.
7. Nomad registers the application service with Consul.
8. Consul performs the configured HTTP health check and makes the service discoverable through Consul DNS.

## Repository Structure

Relevant deployment files and folders:

```text
.
├── .github/
│   └── workflows/
│       └── nomad-deploy.yml
├── docker/
│   └── Dockerfile.staging
├── nomad/
│   └── hubspot-company.nomad.hcl
├── screenshots/
│   └── HubSpot Nomad Deployment Architecture.png
└── README.md
```

The application source code and its supporting directories are retained in the repository.

## Docker Image

The staging image is built from:

```text
docker/Dockerfile.staging
```

The image is published to Docker Hub using these tags:

```text
tahsinuldev/hubspot-company-nomad-deployment:staging
tahsinuldev/hubspot-company-nomad-deployment:<github-commit-sha>
```

The Nomad job uses the staging image and is configured to pull the image when deploying.

## Nomad and Consul Environment

The deployment uses the existing single-node Nomad and Consul agents running in WSL Ubuntu.

### Web interfaces

- **Nomad UI:** `http://127.0.0.1:4646/ui`
- **Consul UI:** `http://127.0.0.1:8500/ui`

### Environment verification

Run these commands from Windows PowerShell:

```powershell
wsl -e bash -lc "nomad node status"
wsl -e bash -lc "nomad server members"
wsl -e bash -lc "consul members"
```

## Nomad Job Specification

The job specification is stored at:

```text
nomad/hubspot-company.nomad.hcl
```

The job configuration includes:

| Configuration | Value |
|---|---|
| Job name | `hubspot-company` |
| Datacenter | `dc1` |
| Job type | `service` |
| Task group count | `1` |
| Task driver | Docker |
| Static host port | `5104` |
| Container port | `5104` |
| CPU reservation | `500 MHz` |
| Memory reservation | `768 MiB` |
| Consul service name | `hubspot-company` |
| Health check type | HTTP |
| Health check path | `/scan/health` |
| Health check interval | `10s` |
| Health check timeout | `2s` |

### Validate and submit the job

The following example uses the repository's current Windows location mounted inside WSL. Update the path if the repository is stored elsewhere.

```powershell
wsl -e bash -lc "nomad job validate /mnt/c/Users/DCL/Desktop/hubspot-company-nomad-deployment/nomad/hubspot-company.nomad.hcl"
wsl -e bash -lc "nomad job run /mnt/c/Users/DCL/Desktop/hubspot-company-nomad-deployment/nomad/hubspot-company.nomad.hcl"
```

Check the job status:

```powershell
wsl -e bash -lc "nomad job status hubspot-company"
```

Inspect a specific allocation:

```powershell
wsl -e bash -lc "nomad alloc status <allocation-id>"
```

## Consul Service Registration and Health Checks

Nomad registers the `hubspot-company` service with Consul. The service is registered on port `5104`, and Consul checks the application's `/scan/health` endpoint over HTTP.

List registered services:

```powershell
wsl -e bash -lc "consul catalog services"
```

Inspect the service health:

```powershell
wsl -e bash -lc "curl -s 'http://127.0.0.1:8500/v1/health/service/hubspot-company?passing=false'"
```

A successful check reports `passing` and an HTTP response of `200 OK`.

## Consul DNS Discovery

The service is discoverable through the Consul DNS name:

```text
hubspot-company.service.consul
```

Query the Consul DNS server from WSL:

```bash
dig @127.0.0.1 -p 8600 hubspot-company.service.consul
```

The verified DNS lookup returned the current application allocation address. Allocation IP addresses may change when Nomad replaces or reschedules an allocation, so treat observed addresses as runtime values rather than fixed configuration.

## Application Health Endpoint

The application health endpoint is:

```text
http://<allocation-address>:5104/scan/health
```

The endpoint was verified from WSL and returned:

- **HTTP status:** `200 OK`
- **Application status:** `healthy`
- **Database status:** `healthy`
- **Service name:** `HubSpot Extraction Service`
- **Application version reported by the endpoint:** `2.0.0`

To test the current allocation, obtain its current address from Nomad and run:

```powershell
wsl -e bash -lc "curl -i http://<allocation-address>:5104/scan/health"
```

The allocation address used during verification was `172.23.28.192`; it is not guaranteed to remain the same after a reschedule or redeployment.

## GitHub Actions CI/CD

The workflow is stored at:

```text
.github/workflows/nomad-deploy.yml
```

It is configured to run on pushes to the `main` branch and supports manual execution through `workflow_dispatch`.

### Pipeline stages

1. Checkout repository.
2. Set up Docker Buildx.
3. Log in to Docker Hub.
4. Build the staging image using `docker/Dockerfile.staging`.
5. Push the `staging` and commit-SHA image tags to Docker Hub.
6. Deploy the Nomad job using `nomad/hubspot-company.nomad.hcl`.
7. Verify the Nomad job status.

### Required GitHub repository secrets

Configure the following under **Repository → Settings → Secrets and variables → Actions**:

| Secret name | Value |
|---|---|
| `DOCKERHUB_USERNAME` | `tahsinuldev` |
| `DOCKERHUB_TOKEN` | Docker Hub access token with repository read/write permissions |

The secret names must match the references in the workflow exactly. Do not commit access tokens, passwords, or other credentials to the repository.

### Self-hosted runner

The configured runner name is:

```text
hubspot-nomad-runner
```

It runs on WSL Ubuntu and provides the environment used by the workflow to build and push the image and submit the Nomad deployment.

Start the runner from WSL Ubuntu:

```bash
cd ~/actions-runner
./run.sh
```

Keep the runner process running while GitHub Actions jobs need it. GitHub should show the runner as `Idle` when it is online and waiting for a job.

The runner environment must have access to Docker Engine, the Nomad CLI, and the running Nomad agent.

## External PostgreSQL Database

The PostgreSQL database used by the application runs in Docker Desktop outside the Nomad-managed application allocation. The application container connects to it using:

```text
host.docker.internal:5432
```

The database connection is supplied to the application through the `DATABASE_URL` environment variable in the Nomad job configuration. Keep database credentials out of source control and use secure secret handling for any real deployment.

## CI/CD and Deployment Results

The GitHub Actions workflow named **Build, Push & Deploy** completed successfully.

The successful workflow run included:

- Checkout Repository
- Set up Docker Buildx
- Login to Docker Hub
- Build and Push Docker Image
- Deploy to Nomad
- Verify Nomad Deployment

The Nomad job status reported:

| Deployment item | Verified result |
|---|---|
| Job status | `running` |
| Deployment status | `successful` |
| Desired allocations | `1` |
| Healthy allocations | `1` |
| Unhealthy allocations | `0` |
| Active allocation at verification | `23fb5bbd` |

The allocation ID and IP address are runtime values and may change after subsequent deployments.

## Acceptance Criteria Verification

| # | Acceptance criterion | Verification |
|---:|---|---|
| 1 | GitHub Actions CI/CD pipeline automates deployment to Nomad | Successful `Build, Push & Deploy` workflow |
| 2 | Nomad job specification for the application | `nomad/hubspot-company.nomad.hcl` validated and submitted |
| 3 | CPU and memory resource constraints | `500 MHz` CPU and `768 MiB` memory configured |
| 4 | Service health checks | HTTP check on `/scan/health`, interval `10s`, timeout `2s` |
| 5 | Consul service registration | `hubspot-company` registered with Consul |
| 6 | Static port allocation | Static port `5104` configured |
| 7 | Service discoverable via Consul DNS | `hubspot-company.service.consul` DNS lookup verified |

## Evidence Screenshots

Store actual project screenshots in the `screenshots/` directory. Suggested evidence filenames:

```text
screenshots/
├── HubSpot Nomad Deployment Architecture.png
├── nomad-ui.png
├── nomad-clients.png
├── consul-ui.png
├── consul-nodes.png
├── nomad-deployment-success.png
├── consul-health-check-passing.png
└── application-health-200.png
```

Only include screenshots that have actually been captured.

## Operational Notes

- Keep the self-hosted runner online while a GitHub Actions job is running.
- Keep the Nomad and Consul agents running during deployment and verification.
- Never commit Docker Hub tokens, HubSpot credentials, database passwords, or other secrets.
- The application endpoint was verified from WSL using the current allocation address. Windows `localhost:5104` was not confirmed as reachable in this setup.
- Retrieve the current allocation address after a reschedule or redeployment; do not rely on a previous allocation IP.
- Validate and commit changes to the Nomad job specification so the repository configuration remains aligned with the deployed configuration.

---

**Project:** HubSpot Company — Nomad Deployment  
**GitHub repository:** `tahsinulhoque/hubspot-company-nomad-deployment`  
**Docker Hub image:** `tahsinuldev/hubspot-company-nomad-deployment:staging`
