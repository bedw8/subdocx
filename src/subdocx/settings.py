from typing import Annotated

from pydantic import Field, PlainSerializer
from pydantic.networks import IPv4Address
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings, cli_parse_args=True, cli_prog_name="subdocx"):
    host: Annotated[IPv4Address, Field(), PlainSerializer(lambda x: str(x))] = "0.0.0.0"
    port: int = 8000


class PDFSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    uniserver_url: str | None = Field(default=None, validation_alias="UNISERVER_URL")
    uniserver_port: int | None = Field(default=None, validation_alias="UNISERVER_PORT")

    @property
    def request_url(self) -> str:
        return f"http://{self.uniserver_url}:{self.uniserver_port}/request"
