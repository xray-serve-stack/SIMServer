from __future__ import annotations

from typing import Optional

import inspect
import logging
import sys
from logging import LogRecord


class SIMServerLogger:
    """
    Configure the SimServer logger.

    Usage:
        from SimServer import logging

        logging.setup(logging.DEBUG)
        logging.debug("...")
    """

    NAME = "SimServer"

    @staticmethod
    def setup(
        level: int = logging.INFO,
        log_file: Optional[str] = None,
    ) -> None:

        logger = logging.getLogger(SIMServerLogger.NAME)

        logger.setLevel(level)
        logger.handlers.clear()
        logger.propagate = False

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(caller)s - %(message)s",
            datefmt="%H:%M:%S",
        )

        class CallerFilter(logging.Filter):
            def filter(self, record: LogRecord) -> bool:

                #
                # INFO/WARNING/ERROR
                # Fast path.
                #

                if record.levelno > logging.DEBUG:
                    record.caller = f"{record.module}.{record.funcName}"
                    return True

                #
                # DEBUG
                # Expensive path.
                #

                record.caller = "<unknown>"

                for frame_info in inspect.stack()[1:]:
                    frame = frame_info.frame

                    module = frame.f_globals.get("__name__", "")

                    #
                    # Skip logging internals.
                    #

                    if module.startswith("logging"):
                        continue

                    #
                    # Skip this module.
                    #

                    if module == __name__:
                        continue

                    func = frame.f_code.co_name

                    if "self" in frame.f_locals:
                        cls = frame.f_locals["self"].__class__.__name__
                        record.caller = f"{cls}.{func}"
                        break

                    record.caller = f"{module}.{func}"
                    break

                return True

        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)
        console.addFilter(CallerFilter())

        logger.addHandler(console)

        if log_file:
            file = logging.FileHandler(
                log_file,
                encoding="utf-8",
            )

            file.setFormatter(formatter)
            file.addFilter(CallerFilter())

            logger.addHandler(file)
