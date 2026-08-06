# Stage 1: Build dependency environment
FROM ghcr.io/astral-sh/uv:python3.11-alpine AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies using cache mounts for maximum speed
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Stage 2: Final lightweight runtime container
FROM python:3.11-alpine

WORKDIR /code

# Copy the pre-compiled virtual environment from the builder stage
COPY --from=builder /app/.venv /code/.venv

# Copy your source code
COPY ./blogs_api /code/blogs_api

# Prepend the virtual environment binaries to the system PATH
ENV PATH="/code/.venv/bin:$PATH"

# Expose app port and run production server
EXPOSE 8000
CMD ["uvicorn", "blogs_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
