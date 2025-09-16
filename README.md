# Simple JSON Webhook Server

A lightweight Flask application that accepts JSON webhook requests and echoes them back.

## Features

- Accepts POST requests with JSON payloads
- Echoes back the received JSON
- Health check endpoint
- Containerized with Docker
- Production-ready with Gunicorn
- Automated Docker Hub publishing via GitHub Actions

## Building and Running

### Using Docker

1. Build the Docker image:
```bash
docker build -t json-webhook-server .
```

2. Run the container:
```bash
docker run -p 3002:3002 json-webhook-server
```

### Pulling from Docker Hub

The image is automatically published to Docker Hub on every push to the main branch. You can pull it using:

```bash
docker pull yourusername/simple-json-server:latest
```

### Testing the Webhook

You can test the webhook using curl:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"test": "data"}' http://localhost:3002/
```

### Health Check

Check the health of the service:

```bash
curl http://localhost:3002/health
```

## Environment Variables

- `PORT`: Server port (default: 3002)
- `HOST`: Server host (default: 0.0.0.0)

## API Endpoints

- `POST /`: Accepts JSON payloads and echoes them back
- `GET /health`: Health check endpoint

## Development

### Setting up GitHub Actions for Docker Hub Publishing

1. Create a Docker Hub account if you don't have one
2. Create an access token in Docker Hub (Account Settings -> Security -> New Access Token)
3. Add the following secrets to your GitHub repository (Settings -> Secrets and variables -> Actions):
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: Your Docker Hub access token

The GitHub Action will automatically:
- Build the Docker image on every push and pull request
- Push the image to Docker Hub on pushes to main branch
- Tag the image with:
  - Branch name
  - PR number (for pull requests)
  - Semantic version (if you use git tags)
  - Git SHA

### Running Locally

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

## Running with Docker Compose (Recommended)

```bash
docker-compose up
```

To run in detached mode:
```bash
docker-compose up -d
```

To stop the service:
```bash
docker-compose down
```

## Running Locally

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```