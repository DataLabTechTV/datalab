FROM astral/uv:python3.13-trixie-slim

RUN apt update && apt install -y git

WORKDIR /datalab
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN uv sync --frozen

COPY . .

RUN uv sync --frozen

ENTRYPOINT ["./infra/apps/docker/mlserver/docker-entrypoint.sh"]
