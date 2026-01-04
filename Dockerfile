
FROM  ghcr.io/astral-sh/uv:alpine3.22
RUN apk add git>=2.49.0 --no-cache

WORKDIR /app

COPY ./pyproject.toml .
COPY ./uv.lock .
COPY ./.python-version .

RUN uv sync -U --no-cache --all-extras

COPY ./src ./src

RUN uv sync -U --no-cache --all-extras

EXPOSE 8000

CMD [ "uv", "run", "subdocx" ]

