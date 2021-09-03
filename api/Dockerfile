# syntax=docker/dockerfile:1
FROM python:3.9.6-slim-buster

# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Force the stdout and stderr streams to be unbuffered in container.
# Ensures that Python output is logged to the host terminal.
ENV PYTHONUNBUFFERED=1

# Install OS-level dependencies
RUN pip install -U pip && \
    pip install poetry && \
    apt-get update &&\
    apt-get -y --no-install-recommends install \
    libpq-dev \
    python3-dev\
    gcc

WORKDIR /api

# prepend .venv to $PATH, and create .venv dir in-project
ENV VIRTUAL_ENV="/api/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python -m venv --upgrade-deps .venv

COPY poetry.lock pyproject.toml /api/

# Install project dependencies into .venv directory
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry install --no-dev

## TODO:
# - remove build libraries required for pycopg2
# - explore multi-stage build

# TODO: Fix to only COPY src/ and remove .dockerignore
COPY . .

CMD ["poetry", "run", "src/manage.py", "runserver", "0.0.0.0:8000"]