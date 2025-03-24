import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

def setup_logging(logs_dir: str, log_level: dict=logging.INFO) -> logging.RootLogger:
    """
    Set up the logging parameters
    Create 3 handlers: 1 for console and 1 for log file at log_level and an additionnal one for error in another log file

    log_level: a dict among INFO, DEBUG, WARNING, ERROR, CRITICAL
    """
    # 2 logs: default and error
    app_log_file = os.path.join(logs_dir, 'flaskr.log')
    error_log_file = os.path.join(logs_dir, 'error.log')
    
    # Format logging message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers (avoid duplicating logs)
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # Create console handler to control logging to console during runtime
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Log the consol output to log file too
    # Use a rotating file handler to split output into 10Mb files
    file_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=10*1024*1024,  # individual file size : 10MB
        backupCount=2  # max number of file to keep
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Log errors separately
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=2
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # Return the configured logger
    return root_logger