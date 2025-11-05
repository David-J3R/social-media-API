from logging.config import dictConfig

from socialapi.config import DevConfig, config


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,  # to prevent errors
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {  # Add correlation ID filter
                    "()": "asgi_correlation_id.CorrelationIdFilter",  # Configure correlation ID filter
                    "uuid_length": 8 if isinstance(config, DevConfig) else 32,
                    "default_value": "-",
                }
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "(%(correlation_id)s) %(name)s:%(lineno)d - %(message)s",
                },
                "file": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(asctime)s.%(msecs)03dZ | %(levelname)-8s | [%(correlation_id)s] %(name)s:%(lineno)d - %(message)s",  # ISO 8601 format with milliseconds
                },
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",  # Using RichHandler for better console output
                    "level": "DEBUG",  # The level will be controlled in the logger
                    "formatter": "console",
                    "filters": [
                        "correlation_id"
                    ],  # Add correlation ID filter to console handler
                },
                "rotating_file": {  # Handler for rotating file logs
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filters": [
                        "correlation_id"
                    ],  # Add correlation ID filter to file handler
                    "filename": "socialapi.log",
                    "maxBytes": 1024 * 1024 * 5,  # 5 MB
                    "backupCount": 5,
                    "encoding": "utf8",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default", "rotating_file"], "level": "INFO"},
                "socialapi": {
                    "handlers": [
                        "default",
                        "rotating_file",
                    ],  # we could add more handlers if needed
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,  # Prevent to propagate to the root logger
                },
                "database": {"handlers": ["default"], "level": "WARNING"},
                "aiosqlite": {"handlers": ["default"], "level": "WARNING"},
            },
        }
    )
