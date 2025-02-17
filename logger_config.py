import logging


def setup_logger(name, log_file="app.log", level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Add handler if not already added
    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger
