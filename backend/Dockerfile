FROM python:3.13.17-slim@sha256:d98cc29d3266e535dd9da1099688d9cb3ca4753813571e071763d17725460962

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_NO_PROGRESS=1

WORKDIR /workspace

RUN groupadd --gid 10001 genesis \
    && useradd --uid 10001 --gid 10001 --no-create-home genesis \
    && python -m pip install --disable-pip-version-check --no-cache-dir uv==0.13.7

COPY pyproject.toml uv.lock ./backend/
RUN uv sync --project backend --frozen --no-dev

COPY __init__.py ./backend/__init__.py
COPY app ./backend/app
COPY core ./backend/core

RUN mkdir /data && chown -R genesis:genesis /data /workspace

USER 10001:10001

EXPOSE 8000

CMD ["/workspace/backend/.venv/bin/uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
