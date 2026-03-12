# -*- coding: utf-8 -*-
"""Common functions."""

import logging
import re

logger = logging.getLogger(__name__)


def escape_string(string_to_escape) -> str:
    """Check if the given string needs to be 'escaped' or 'backslashed'
    because of the platform.

    Args:
    string_to_escape = the string to escape

    Returns:
    The escaped string
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
        logger.error("Problem with escaping backslashes: %s.", e)
    return new_string
