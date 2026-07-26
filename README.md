# Cloud Architecture Manager

## Overview

Cloud Architecture Manager discovers AWS-compatible infrastructure, stores a
profile of each architecture, and recommends the best saved architecture for a
workload described by the user.

The project is split into four parts:

- `aws_parser` discovers resources from an AWS-compatible endpoint and produces
  a normalized architecture document.
- `aws_parser_mocks` provides ten isolated LocalStack environments used for
  development, database seeding, and integration tests.
- `server` exposes the parser, saved architectures, and recommendation engine
  through FastAPI and persists data in SQLite.
- `frontend` is a React and TypeScript application that collects workload
  requirements and presents the top three recommendations.

The normal data flow is:

```text
LocalStack or AWS-compatible endpoint
    -> aws_parser
    -> architecture profile and scores
    -> SQLite
    -> FastAPI recommendation endpoint
    -> React results podium
```

## How to deploy

### Prerequisites

- A cloud container platform, or Docker Engine with Docker Compose when using
  the included Compose file

Build and start the containerized frontend and server from the repository root:

```text
docker compose up --build
```

The services are exposed at:

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- Interactive API documentation: `http://localhost:8000/docs`

Run the stack in the background with:

```text
docker compose up --build --detach
```

Stop it with:

```text
docker compose down
```

When a server container starts without a SQLite database, its entrypoint
deploys the bundled LocalStack mocks, parses them, writes the seed records, and
removes the mock containers and named volumes before starting FastAPI. An
existing database is left unchanged.

The container image includes Docker CLI and Compose, but a container cannot
control the host Docker daemon by default. First-time seeding from inside the
server container requires Docker daemon access configured for the deployment
environment. Docker Desktop is not a cloud prerequisite. A managed deployment
should provide initialization through a trusted build or deployment job rather
than mounting a host Docker socket into the public API container.

## How to deploy locally

### Prerequisites

- Docker Desktop or Docker Engine, for the mock AWS environments used during
  initial seeding
- Python 3.10 or newer
- Node.js 24 or newer

Create and activate a Python virtual environment, then install the local
packages and development dependencies:

```text
python -m venv .venv
python -m pip install --requirement requirements-dev.txt
```

Install the frontend dependencies:

```text
cd frontend
npm ci
cd ..
```

Start the API from the repository root:

```text
python -m server.main
```

In another terminal, start the frontend:

```text
cd frontend
npm run dev
```

The application is then available at:

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- Interactive API documentation: `http://localhost:8000/docs`

On the first API startup, a missing database is created and seeded from the
mock AWS architectures. The temporary containers and volumes are removed after
seeding.

## AWS parser

The `aws_parser` package scans the services available at an AWS-compatible
endpoint. It returns an `Architecture` model containing the supplied
architecture name, discovered resources, relationships, endpoint metadata,
warnings, and per-service discovery errors.

### Install locally

```text
python -m pip install --editable ./aws_parser
```

Install it together with the optional mock package:

```text
python -m pip install --editable ./aws_parser --editable ./aws_parser_mocks
```

### Use from Python

```python
from aws_parser import parse

architecture = parse(
    endpoint="http://localhost:4566",
    name="customer-portal",
    region="us-east-1",
    services={"s3", "dynamodb"},
)
```

### Use the CLI

The CLI discovers LocalStack containers in a Docker Compose project and uses
each container name as its architecture name:

```text
aws-parser --project aws-parser-mocks
```

Restrict discovery to selected services by repeating `--service`:

```text
aws-parser --project aws-parser-mocks --service s3 --service dynamodb
```

### Build and test

```text
python -m pip install build
python -m build aws_parser
python -m pytest aws_parser/tests
```

Built distributions are written to `aws_parser/dist`.

### Considerations

- A regular `parse()` call requires an architecture name from the caller. Mock
  parsing derives the name from the Docker container instead.
- The parser records discovered infrastructure facts and does not infer
  workload purpose. Profile scoring and recommendations belong to the server.
- Unsupported or unreachable services can produce warnings and partial
  architecture data, so callers should inspect the discovery metadata.
- Custom endpoints must expose the AWS-compatible APIs needed by the requested
  services.

## AWS parser mocks

The `aws_parser_mocks` package contains a Docker Compose definition, LocalStack
initialization assets, deployment helpers, and test utilities. Each bundled
use case runs in its own container and is parsed independently.

The included use cases cover web applications, public APIs, ecommerce,
real-time analytics, batch processing, event processing, media delivery,
internal tools, IoT ingestion, and ML inference.

### Deploy the mocks

```text
docker compose --parallel 10 \
  --file aws_parser_mocks/aws_parser_mocks/assets/docker-compose.yml \
  --project-name aws-parser-mocks \
  up --detach --wait
```

PowerShell accepts the same command on one line:

```powershell
docker compose --parallel 10 --file aws_parser_mocks/aws_parser_mocks/assets/docker-compose.yml --project-name aws-parser-mocks up --detach --wait
```

The Python helper deploys and parses the mocks:

```python
from aws_parser import parse_mocks, teardown_mocks

try:
    architectures = parse_mocks()
finally:
    teardown_mocks()
```

### Teardown

Remove the mock containers, networks, orphaned resources, and named volumes:

```text
docker compose \
  --file aws_parser_mocks/aws_parser_mocks/assets/docker-compose.yml \
  --project-name aws-parser-mocks \
  down --volumes --remove-orphans
```

### Build and test

Install the parser first because the mock package depends on it:

```text
python -m pip install --editable ./aws_parser
python -m pip install --editable ./aws_parser_mocks
python -m build aws_parser_mocks
python -m pytest aws_parser_mocks/tests
```

Built distributions are written to `aws_parser_mocks/dist`.

### Considerations

- The full fixture set starts ten LocalStack containers, which requires
  sufficient Docker resources and available host ports.
- `parse_mocks()` does not own the complete lifecycle. Pair it with
  `teardown_mocks()` in a `finally` block so cleanup happens after both success
  and failure.
- Teardown removes the named mock volumes. The fixtures are reproducible, but
  any manual changes inside those volumes are lost.
- Container names become architecture names, so stable Compose project and
  service names matter.
- Docker-dependent integration tests are skipped when Docker is unavailable.

## Server

The `server` package provides the FastAPI application, SQLAlchemy models,
SQLite persistence, architecture profiling, and recommendation ranking.

At application initialization, a missing `server/architectures.sqlite` database
is seeded from the mock architectures. Every record stores its insertion
timestamp, architecture data, profile values, and explainable scoring metadata.

Important endpoints include:

- `GET /architectures` returns all saved architectures.
- `GET /architectures/{id}` returns one architecture, with optional data and
  profile metadata flags.
- `POST /architectures/parse` parses and saves a named architecture.
- `POST /architectures/recommendations` returns up to three ranked matches.

### Install and run locally

Create and activate a virtual environment, then install the local packages and
server development dependencies:

```text
python -m venv .venv
python -m pip install --requirement requirements-dev.txt
```

Run the server:

```text
python -m server.main
```

The default address is `http://127.0.0.1:8000`. Override it with the
`SERVER_HOST` and `SERVER_PORT` environment variables.

Seed the database without starting the API:

```text
python -m server.init_db
```

This command also tears down the mock containers and volumes after seeding.

### Build and deploy with Docker

Build only the server image:

```text
docker build --file server/Dockerfile --tag cloud-architecture-manager-server .
```

Start the server-only Compose project:

```text
docker compose --file server/compose.yaml up --build
```

The server image builds and installs both local parser packages automatically
and exposes port 8000.

### Test

```text
python -m pytest server/tests
python -m ruff check .
```

The integration test starts isolated LocalStack containers when Docker is
available and removes them after the test session.

### Considerations

- Container database initialization is handled by the image entrypoint before
  FastAPI starts. Local execution uses the same initialization through
  FastAPI's lifespan hook.
- A first-time seed therefore requires a reachable Docker daemon. The server
  image includes Docker tooling, but daemon access must be enabled deliberately
  because it grants broad host control.
- SQLite fits the current local, single-node workflow. A production deployment
  with multiple writers would need stronger concurrency support and a database
  migration strategy.
- An unreachable architecture source is reported as `502 Bad Gateway`; it is
  an upstream availability problem rather than an internal server failure.
- Architecture names are required for ordinary parse requests. The optional
  detail flags on `GET /architectures/{id}` default to `false`.
- Profile scores use explainable heuristics with separately configured
  weights. Recommendations include an overall match and alternatives focused
  on operational and budget fit.
- Set `ARCHITECTURES_DATABASE_PATH` to move the SQLite database outside the
  default `server` directory.

## Frontend

The frontend is a single-screen React and TypeScript application built with
Vite. It gathers the complete recommendation profile, calls FastAPI, and
displays the top three results as an animated podium.

During local development, Vite proxies `/architectures` requests to
`http://localhost:8000`. In the production container, Nginx serves the compiled
application and proxies the same path to the `server` Compose service.

### Install and run locally

```text
cd frontend
npm ci
npm run dev
```

Vite prints the local development URL, normally `http://localhost:5173`.

### Build locally

```text
cd frontend
npm run lint
npm run build
```

The build first runs the TypeScript compiler and then writes production assets
to `frontend/dist`.

Preview the production build locally:

```text
npm run preview
```

### Build and deploy with Docker

Build only the frontend image:

```text
docker build --file frontend/Dockerfile \
  --tag cloud-architecture-manager-frontend \
  frontend
```

The image uses Node.js only during the build stage. The runtime contains Nginx
and the static production assets; it does not contain or install any Python
packages.

For a working API proxy, run the frontend as part of the root Compose project:

```text
docker compose up --build
```

### Considerations

- The recommendation form sends all nine criteria expected by the API; none
  are optional.
- The frontend should run with the backend available. Vite proxies API traffic
  to `localhost:8000`, while the production Nginx image targets the Compose
  service at `server:8000`.
- The result screen emphasizes ranked architecture names and match
  explanations. Endpoint addresses remain available from the API but are not
  displayed.
- Podium, crown, transition, and result-entry animations respect reduced-motion
  preferences.
- This is currently a one-screen client without authentication, routing, or
  browser-side persistence.
