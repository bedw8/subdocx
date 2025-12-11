from .main import app
import warnings

try:
    import uvicorn

    _has_uvicorn = True
except ImportError:
    _has_uvicorn = False

if __name__ == "__main__":
    if not _has_uvicorn:
        warnings.warn("Install uvicorn to run the server directly.")
        exit()

    uvicorn.run(app, host="0.0.0.0", port=8000)
