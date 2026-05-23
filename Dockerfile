FROM python:3.14-slim-trixie

WORKDIR /workspace

RUN apt-get update \
  && apt-get install -y --no-install-recommends git nodejs npm \
  && npm i -g @openai/codex \
  && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["bash"]
