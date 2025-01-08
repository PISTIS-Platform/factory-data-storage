import logging

logging_configured = False
logger = None  # Define logger as a global variable

def setup_logging():
    global logging_configured, logger  # Declare logger as a global variable

    if not logging_configured:
        # Create the root logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # Define the log format including file name
        log_format = "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s"
        log_formatter = logging.Formatter(log_format)

        # Create a console handler and attach the formatter
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)

        # Add the console handler to the logger
        logger.addHandler(console_handler)

        logging_configured = True

    return logger

