FROM python:3.14-slim-trixie

WORKDIR /workspace

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CODEX_HOME=/root/.codex

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    git \
    nodejs \
    npm \
    ripgrep \
  && update-ca-certificates \
  && npm i -g @openai/codex@latest \
  && mkdir -p /root/.codex \
  && rm -rf /var/lib/apt/lists/*

CMD ["bash"]
