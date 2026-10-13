from pathlib import Path
import argparse
import uvicorn
import logging as python_logging
from simserver import logging

from .server import SIMServer


BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
log_file = LOG_DIR / "app.log"


# CERTS_DIR = BASE_DIR / "certs"
# SERVER_CERT = CERTS_DIR / "server.crt"
# SERVER_KEY = CERTS_DIR / "server.key"


def main() -> None:
    logging.setup(python_logging.DEBUG, str(log_file))

    # HOST:PORT
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    # APP
    server = SIMServer()

    # RUN
    uvicorn.run(
        server.app,
        host=args.host,
        port=args.port,
        # ssl_certfile=str(SERVER_CERT),
        # ssl_keyfile=str(SERVER_KEY),
    )


if __name__ == "__main__":
    main()
