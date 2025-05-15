### Arguments ###
ARG PYTHON_VERSION=3.13.3
ARG POETRY_VERSION=2.1.3

### Build Stage ###
FROM python:${PYTHON_VERSION}-slim AS builder
ARG POETRY_VERSION

WORKDIR /app
COPY ../pyproject.toml poetry.lock /app/

RUN pip install --no-cache-dir poetry==${POETRY_VERSION} \
    && poetry config virtualenvs.create false  \
    && poetry install --without dev --no-ansi --no-interaction \
    && poetry export --without-hashes --without dev -f requirements.txt -o requirements.txt

### Runtime Stage ###
FROM python:${PYTHON_VERSION}-alpine AS runtime

LABEL mantainer="Fran <rebelist.software@icloud.com>"

ENV PYTHONUNBUFFERED=1
ENV TERM=xterm-256color
RUN addgroup -S rebelist && adduser -S streamline -G rebelist

USER streamline
WORKDIR /home/streamline/app

COPY --from=builder /app/requirements.txt ./requirements.txt
COPY --chown=streamline:rebelist ../ .

RUN pip install --no-cache-dir --user -r requirements.txt

EXPOSE 8000
ENTRYPOINT ["python", "-m", "fastapi", "run", "src/streamline/handlers/api", "--port", "8000"]
