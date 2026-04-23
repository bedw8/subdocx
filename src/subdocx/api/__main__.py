from .main import app as api
import warnings

from subdocx.settings import APISettings


try:
    import uvicorn

    _has_uvicorn = True
except ImportError:
    _has_uvicorn = False


def cli():
    if not _has_uvicorn:
        warnings.warn("Install uvicorn to run the server directly.")
        exit()

    args = APISettings()
    uvicorn.run(api, host=str(args.host), port=args.port)


if __name__ == "__main__":
    cli()
