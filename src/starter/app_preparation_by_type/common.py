"""Common functions supporting modules for searching and processing 
   requirements for given app.
"""
import logging
import os
from pathlib import Path

DEPENDENCIES_REGEX = "*requirement*"

logger = logging.getLogger(__name__)


def get_list_of_files_and_timestamp(folder_path, filters) -> dict:
    """Get list of files from given folder and timestamp of
       their latest change.

    Params:
    folder_path = path to folder to search
    filters = list of required files(mandatory arg)

    Returns:
    Dict in format '<path_to_file>: <timestamp>'
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
                        "Problem with processing(get timestamp) file %s,\
                        because %s", item, e)
                    continue
    return files_dict


def get_all_dependencies_setuptools_approach(
        folder_path,
        key=None
        ) -> set:
    """Get the list of all dependencies using setuptools's style approach.

    That means search through folderpath and try to find all files name
    *dependencies* and process content of this files. Searching only
    on 'root' level of the folder.

    Args:
    folder_path = where to search
    key = regex key for requirements file(default '*requirement*')

    Returns:
    List of depenencies
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
                                # Line contains something
                                dependencies.append(line.strip())
                except Exception as e:
                    logger.error(
                        "Processing file %s to get list of \
                        dependencies failed(%s).",
                        file, e)
    else:
        logger.info("Cannot search and process dependencies, because %s\
                    doesn't exist.", folder_path)
    return set(dependencies)
