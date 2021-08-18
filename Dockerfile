FROM python:3.9.6-slim-buster

# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Force the stdout and stderr streams to be unbuffered in container.
# Ensures that Python output is logged to the host terminal.
ENV PYTHONUNBUFFERED=1

# Install CLI dependencies
RUN pip install -U pip && \
    pip install poetry

WORKDIR /code

# prepend .venv to $PATH
ENV VIRTUAL_ENV="/code/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python -m venv --upgrade-deps .venv

COPY poetry.lock pyproject.toml /code/

# Install project dependencies to a in-project .venv directory
ARG POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry install

COPY . .

CMD ["poetry", "run", "server/manage.py", "runserver", "0.0.0.0:8000"]