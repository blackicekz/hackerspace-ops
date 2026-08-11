# syntax=docker/dockerfile:1
FROM python:3.13-slim@sha256:ffb752e139c0a19692a43af8d8523b274222dd68eebad5d583b45c2201c6e30a AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/workspace

WORKDIR /workspace

COPY src/ ./src/

CMD ["python", "-m", "src"]

FROM runtime AS development

RUN pip install --no-cache-dir mypy==1.17.1 ruff==0.12.8

COPY pyproject.toml ./
COPY scripts/ ./scripts/
COPY tests/ ./tests/
COPY specs/ ./specs/
COPY AGENTS.md README.md ./

ENTRYPOINT ["/bin/sh", "./scripts/dev"]
CMD ["check"]
