import logging
import os
import sys

def setup_logging(log_level: str = "INFO", log_file: str = "logs/game.log") -> logging.Logger:
    """
    Sets up global application logging to both console and file.
    
    Args:
        log_level: Severity level (e.g. "DEBUG", "INFO", "WARNING")
        log_file: Path to write log messages to
        
    Returns:
        The root logger instance.
    """
    # Ensure logs directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception as e:
            print(f"Failed to create logs directory: {e}", file=sys.stderr)

    # Map level name to logging constants
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Clear existing handlers if any to prevent duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter for log entries
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console stream handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to create file handler for logging: {e}", file=sys.stderr)

    logger.info("Logging initialized at level %s. Log file: %s", log_level, log_file)
    return logger
