import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


def get_logger() -> logging.Logger:
    import inspect

    frame = inspect.currentframe().f_back
    module_name = frame.f_globals.get("__name__", "__main__")
    return logging.getLogger(module_name)
