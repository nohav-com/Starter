"""Common functions supporting modules for searching and processing 
   requirements for given app.
"""
import logging
import os
from pathlib import Path

DEPENDENCIES_REGEX = "*requirement*"

logger = logging.getLogger(__name__)


def get_list_of_files_and_timestamp(folder_path, filters=[]) -> dict:
    """Get list of files from given folder and timestamp of
       their latest change.

    Params:
    folder_path = path to folder to search

    Returns:
    Dict in format '<path_to_file>: <timestamp>'
    """
    files_dict = {}

    if folder_path and Path(folder_path).exists():
        for filter in filters:
            for item in Path(folder_path).rglob(filter):
                try:
                    if item:
                        timestamp = os.path.getmtime(item)
                        short_item = str(item).split(
                            str(folder_path))
                        if short_item:
                            files_dict[short_item[-1]] = timestamp
                except Exception as e:
                    logger.info(
                        "Problem with processing file {%s}, because {%s}" 
                        % {item, e})
                    continue
    return files_dict


def get_all_dependencies_setuptools_approach(folder_path) -> set:
    """Get the list of all dependencies using setuptools's style approach.

    That means search through folderpath and try to find all files name
    *dependencies* and process content of this files. Searching only
    on 'root' level of the folder.
    """
    # List if dict form <dependencie>: <version>
    dependencies = []

    if folder_path and Path(folder_path).exists():
        # Search just 'root', level
        files = Path(folder_path).glob(DEPENDENCIES_REGEX)
        if files:
            for file in files:
                with open(str(file), "r") as requirement:
                    for line in requirement.readlines():
                        if line.strip() and not line.strip().startswith("#"):
                            # Line contains something
                            dependencies.append(line.strip())
    else:
        logger.warning("Cannot search and process dependencies, because {%s}\
                        doesn't exist." % folder_path)
    return set(dependencies)
