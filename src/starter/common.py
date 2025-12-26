import logging
import re

logger = logging.getLogger(__name__)


def path_to_valid_path(path_to):
    """Check if given path needs to be chnaged to different
       valid path, because of platform"""
    new_path = path_to
    try:
        if re.search(r"\\", new_path):
            # Replace "\" with "\\"
            new_path = re.sub(r"\\", r"\\\\", new_path, flags=re.IGNORECASE)
    except Exception as e:
        logger.error("Problem with escaping backslashes. {%s}" % e)
    return new_path
