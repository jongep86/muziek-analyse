# Build: uv on Debian 13 (trixie) installs the Python dependencies into /app/.venv.
# Runtime: plain python slim on the same Debian and Python, so the venv runs unchanged.
# Every FROM is pinned by digest; Renovate ("docker base images") keeps them fresh.

FROM denoland/deno:bin-2.9.8@sha256:b507583d3c68ba69f3ed2ce5969ae5b8b70f43421c781279c7aea06435263543 AS deno

FROM ghcr.io/astral-sh/uv:0.13.8-python3.13-trixie-slim@sha256:9a9f205ad2f9aaf63597afef4042c455392f9253937028264b98226e91c09518 AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv /app/.venv \
    && VIRTUAL_ENV=/app/.venv uv pip install -r requirements.txt gunicorn

FROM python:3.13-slim-trixie@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90

# ffmpeg: yt-dlp converts to mp3 with it and librosa decodes webm/m4a through it.
# apt-get upgrade picks up Debian security fixes released after the base image.
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# The app runs from the venv; the base image's pip (and its vendored urllib3, msgpack,
# setuptools) is not needed at runtime and only adds findings.
RUN rm -rf /usr/local/bin/pip* /usr/local/lib/python3.13/site-packages/pip* \
        /usr/local/lib/python3.13/ensurepip

# deno: yt-dlp needs a JS runtime for YouTube's player challenges.
COPY --from=deno /deno /usr/local/bin/deno

RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --home-dir /home/app --create-home --shell /usr/sbin/nologin app

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --chown=root:root . .
RUN mkdir -p /app/data/tracks /app/data/output /app/data/uploads \
    && chown -R app:app /app/data

# Everything the app writes goes to /app/data (the volume) or /tmp, so the root
# filesystem can be mounted read-only with a tmpfs or emptyDir on /tmp.
ENV PATH=/app/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATA_DIR=/app/data \
    PORT=5050 \
    HOME=/home/app \
    XDG_CACHE_HOME=/tmp/.cache \
    NUMBA_CACHE_DIR=/tmp/numba \
    DENO_DIR=/tmp/deno

USER 1000:1000
EXPOSE 5050

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
    CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5050/healthz', timeout=4).status == 200 else 1)"]

CMD ["gunicorn", "--bind", "0.0.0.0:5050", "--workers", "1", "--threads", "4", "--timeout", "300", "--worker-tmp-dir", "/tmp", "--no-control-socket", "app:app"]
