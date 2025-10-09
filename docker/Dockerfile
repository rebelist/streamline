ARG PYTHON_VERSION=3.14

FROM python:${PYTHON_VERSION}-slim

LABEL mantainer="Fran <rebelist.software@icloud.com>"

ARG UV_VERSION=0.9

ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TERM=xterm-256color
ENV PATH=/home/streamline/.local/bin:$PATH

RUN groupadd --system rebelist && useradd --system --create-home --gid rebelist streamline

HEALTHCHECK NONE

# Install uv as root first, or manage permissions carefully
RUN pip install --no-cache-dir "uv~=${UV_VERSION}"

USER streamline
WORKDIR /home/streamline/app

COPY --chown=streamline:rebelist ./ .

# Now uv is already installed, so you can just use it
RUN uv sync --locked --no-dev

EXPOSE 8000
ENTRYPOINT ["uv", "run", "fastapi", "run", "src/rebelist/streamline/handlers/api", "--port", "8000"]
