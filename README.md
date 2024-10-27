# Jeopardy API

Backend for Jeopardy game.

## Installation

To install the project, go to preferred directory and run

```bash
git clone git@github.com:natuspati/jeopardy-api.git
```

## Environment variables

Create `.env` in the root directory. Copy values from [`deploy/.env.template`](deploy/.env.template)
to `.env` with appropriate environment variables.

An example configration is

```text
# Database
JEOPARDY_DB_HOST="localhost"
JEOPARDY_DB_PORT="5432"
JEOPARDY_DB_USER="jeopardy"
JEOPARDY_DB_PASSWORD="jeopardy"
JEOPARDY_DB_NAME="jeopardy"

# Redis
JEOPARDY_REDIS_HOST="localhost"
JEOPARDY_REDIS_POT="6379"

# Token
JEOPARDY_ACCESS_TOKEN_EXPIRE_MIN="43200"
```


## Local Development

To set up a local development environment, this project utilizes the following tools:

- **Poetry**: For dependency management and packaging.
- **Pre-commit**: To manage and maintain code quality.
- **Docker**: To create and manage containerized applications and dependencies.

**Ensure environment variables are configured as shown in
[Environment variables](#environment-variables).**

### Running the Application in Poetry Shell

To run the application in a Poetry shell, follow these steps:

1. **Install Poetry**: Make sure you have Poetry installed on your machine.
You can follow the [Poetry installation guide](https://python-poetry.org/docs/#installation).
2. **Install dependencies**: Navigate to the project directory and run:
   ```bash
   poetry install
   ```
3. **Activate the Poetry shell**:
   ```bash
   poetry shell
   ```
4. **Run the application**:
   ```bash
   python ./src
   ```

See [`pyproject.toml`](pyproject.toml) for details for python configuration.

### Running the Application in a Docker Container

To run the application, Docker Compose is used to start the containers.

**Ensure `.env` file is configured.**


1. **Run the Docker compose file for local development**:
   ```bash
   docker compose -f deploy/docker-compose.local.yml --project-directory . up -d
   ```
2. **Stop the containers**:
   ```bash
   docker compose -f deploy/docker-compose.local.yml --project-directory . down
   ```

## CI/CD

- **Pre-commit**: Initialize the pre-commit hooks to ensure code quality.
Ensure local python environment is set as explined in
[Running the Application](#running-the-application-in-poetry-shell).
Run the following command to set it up:
  ```bash
  pre-commit install
  ```
- **GitHub Actions**: CI is set up to run on every push and pull request to the main branch.
Workflow YAML files are configured in the [`.github/workflows`](.github/workflows) directory.

### Continuous Deployment (CD)

Continuous Deployment is planned for future implementation.

## Testing

To run tests, make sure the Docker container for the database is running.
Use the following command to change the `PYTHONPATH` to the `src` directory and execute the tests using `pytest`:

```bash
PYTHONPATH=src pytest
```

Make sure to adjust the paths and commands according to your project's structure and requirements.

## Hosting

Hosting solutions are planned for future implementation.
