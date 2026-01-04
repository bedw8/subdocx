from .main import app as api
import warnings
import sys  # pyright: ignore
from typing import Annotated
from pydantic import Field, PlainSerializer
from pydantic_settings import BaseSettings
from pydantic.networks import IPv4Address

from box import Box


class Settings(BaseSettings, cli_parse_args=True, cli_prog_name="subdocx"):
    host: Annotated[IPv4Address, Field(), PlainSerializer(lambda x: str(x))] = "0.0.0.0"
    port: int = 8000


try:
    import uvicorn

    _has_uvicorn = True
except ImportError:
    _has_uvicorn = False


def cli():
    if not _has_uvicorn:
        warnings.warn("Install uvicorn to run the server directly.")
        exit()

    # args = Box(Settings().model_dump())
    args = Box(Settings().model_dump())

    uvicorn.run(api, host=args.host, port=args.port)


if __name__ == "__main__":
    cli()
