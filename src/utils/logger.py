import logging
import os
from logging.handlers import RotatingFileHandler

current_dir = os.path.dirname(os.path.abspath(__file__))

root = os.path.join(current_dir, "..", "..")

LOGS_DIR_PROD = os.path.join(root, "logs", "prod")

# LOGS_DIR_DEV = "/app/logs/dev"

loggers = {}


def setup_logger(name: str, level: int, log_file: str) -> logging.Logger:
    log_env_dir = LOGS_DIR_PROD
    if not os.path.exists(log_env_dir):
        os.makedirs(log_env_dir)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    )

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        log_path = os.path.join(log_env_dir, log_file)
        log_handler = RotatingFileHandler(
            log_path, maxBytes=1e6, backupCount=1)
        log_handler.setFormatter(formatter)
        log_handler.setLevel(level)
        logger.addHandler(log_handler)

    return logger


def make_log(name: str, level: int, log_file: str, msg):
    global loggers
    logger = loggers.get(name)

    log_levels = {
        10: logging.DEBUG,
        20: logging.INFO,
        30: logging.WARNING,
        40: logging.ERROR,
        50: logging.CRITICAL,
    }
    if not logger:
        logger = setup_logger(name, level, log_file)
        loggers[name] = logger

    log_level = log_levels.get(level, logging.DEBUG)
    logger.log(log_level, msg)
