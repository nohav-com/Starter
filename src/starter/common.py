import logging
import re

logger = logging.getLogger(__name__)


def escape_string(string_to_escape):
    """Check if given string needs to be 'escape/backslashed',
    because of platform.add()

    Args:
    string_to_escape = string to escape

    Returns:
    Escaped string
    """
    new_string = string_to_escape
    try:
        if new_string and re.search(r"\\", new_string):
            # Replace "\" with "\\"
            new_string = re.sub(
                r"\\",
                r"\\\\",
                new_string,
                flags=re.IGNORECASE)
    except Exception as e:
        logger.error("Problem with escaping backslashes. %s", e)
    return new_string
