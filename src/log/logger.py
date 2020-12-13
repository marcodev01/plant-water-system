import logging
from logging import Logger


def setup_logger(name: str, log_file: str, level: int=logging.INFO) -> Logger:
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%d-%m-%y %H:%M:%S')

    handler = logging.FileHandler(log_file, mode='a')        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
