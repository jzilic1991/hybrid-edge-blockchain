import logging
import os
import sys


def setup_logging(log_path="logs/simulation.log"):
    """Configure root logger with file and stdout handlers."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    handlers = [
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout)
    ]

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers,
        force=True
    )

    return logging.getLogger()
