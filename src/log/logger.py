import logging
from logging import Logger
from logging.handlers import RotatingFileHandler


def setup_logger(name: str, log_file: str, level: int=logging.INFO) -> Logger:
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%d-%m-%y %H:%M:%S')

    handler = RotatingFileHandler(log_file, mode='a', maxBytes=4000000, backupCount=4)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
