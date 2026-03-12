# -*- coding: utf-8 -*-
"""Common functions supporting modules for searching and processing
requirements for the given app."""

import logging
import os
from pathlib import Path

DEPENDENCIES_REGEX = "*requirement*"

logger = logging.getLogger(__name__)


def get_list_of_files_and_timestamp(folder_path: str, filters) -> dict:
    """Get a list of files from the given folder and the timestamp of
    their latest change.

    Params:
    folder_path (str)= path to the folder to search
    filters = list of required files(mandatory arg)

    Returns:
    A dict in format '<path_to_file>: <timestamp>'
    """
    files_dict = {}

    if folder_path and Path(folder_path).exists():
        for filter_item in filters:
            for item in Path(folder_path).rglob(filter_item):
                try:
                    if item:
                        timestamp = os.path.getmtime(item)
                        short_item = str(item).split(
                            str(folder_path))
                        if short_item:
                            files_dict[short_item[-1]] = timestamp
                except Exception as e:
                    logger.error(
                        "Problem processing(get timestamp) for file %s,\
                        because %s.", item, e)
                    continue
    return files_dict


def get_all_dependencies_setuptools_approach(
        folder_path: str,
        key: str | None = None
        ) -> set:
    """Get the list of all dependencies using setuptools-style approach.

    This means searching through the folder path and looking for files
    named *dependencies* to process their content. Search is performed
    only at the 'root' level of the folder.

    Args:
    folder_path (str)= the path where to search
    key (str)= the regex key for the requirements files(default is '*requirement*')

    Returns:
    A list of depenencies
    """
    dependencies = []

    if folder_path and Path(folder_path).exists():
        key_regex = DEPENDENCIES_REGEX
        if key:
            key_regex = key
        files = None
        files = Path(folder_path).glob(key_regex)
        if files:
            for file in files:
                try:
                    with open(str(file), "r", encoding='UTF-8') as requirement:
                        for line in requirement.readlines():
                            if line.strip() and not line.strip()\
                                    .startswith("#"):
                                # Line contains
                                dependencies.append(line.strip())
                except Exception as e:
                    logger.error(
                        "Processing file %s to get the list of \
                        dependencies failed(%s).",
                        file, e)
    else:
        logger.info("Cannot search and process dependencie because %s\
                    doesn't exist.", folder_path)
    return set(dependencies)
