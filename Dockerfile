FROM python:3.14-slim-trixie

WORKDIR /workspace

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends git nodejs npm \
  && npm i -g @openai/codex \
  && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["bash"]
