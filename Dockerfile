
FROM  ghcr.io/astral-sh/uv:alpine3.22
RUN apk add git

WORKDIR /subdocx

COPY pyproject.toml .
RUN uv sync -U --no-cache

COPY subdocx .
RUN uv pip install -e .

EXPOSE 8000

CMD [ "uv", "run", "fastapi", "run","subdocx.api" ]

