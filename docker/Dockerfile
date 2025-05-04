### Arguments ###
ARG PYTHON_VERSION=3.13
ARG POETRY_VERSION=2.0.1

### Build Stage ###
FROM python:${PYTHON_VERSION}-slim AS builder
ARG POETRY_VERSION

WORKDIR /app
COPY ../pyproject.toml poetry.lock /app/
# @todo Do we need poetry?
RUN pip install --no-cache-dir poetry==${POETRY_VERSION} \
    && poetry config virtualenvs.create false  \
    && poetry install --without dev --no-ansi --no-interaction \
    && poetry export --without-hashes --without dev -f requirements.txt -o requirements.txt

### Runtime Stage ###
FROM python:${PYTHON_VERSION}-alpine AS runtime

LABEL mantainer="Fran <rebelist.software@icloud.com>"

ENV PYTHONUNBUFFERED=1
RUN addgroup -S rebelist && adduser -S streamline -G rebelist

USER streamline
WORKDIR /home/streamline/app

COPY --chown=streamline:rebelist ../src .
COPY --from=builder /app/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --user -r requirements.txt

EXPOSE 8000
ENTRYPOINT ["python", "-m", "fastapi", "run", "src/streamline/handlers/api", "--port", "8000"]
