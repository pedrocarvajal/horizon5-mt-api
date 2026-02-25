FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements/production.txt requirements/production.txt
COPY requirements/base.txt requirements/base.txt
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements/production.txt

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN groupadd -r django && useradd -r -g django django

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

ARG SUPERCRONIC_VERSION=0.2.33
ARG SUPERCRONIC_ARCH=linux-amd64
RUN curl -fsSL "https://github.com/aptible/supercronic/releases/download/v${SUPERCRONIC_VERSION}/supercronic-${SUPERCRONIC_ARCH}" -o /usr/local/bin/supercronic \
    && chmod +x /usr/local/bin/supercronic

WORKDIR /app

COPY --from=builder /build/wheels /tmp/wheels
RUN pip install --no-cache-dir /tmp/wheels/* && rm -rf /tmp/wheels

COPY . .

RUN python manage.py collectstatic --noinput 2>/dev/null || true

RUN chown -R django:django /app

USER django

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
