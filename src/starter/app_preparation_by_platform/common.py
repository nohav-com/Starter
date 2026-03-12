# -*- coding: utf-8 -*-
"""Common methods."""

import logging
from subprocess import PIPE, Popen

__all__ = ['CommonPreparationByPlatform']

logger = logging.getLogger(__name__)


class CommonPreparationByPlatform():
    def __init__(self):
        """Just pass."""
        pass

    def install(self, name: str, args: list, cwd: str):
        """Install the necessary components.

        Args:
        name (str) = item is to be installed
        args (list) = installation command string
        cwd (str)= the cwd where the installation will run
        """
        try:
            if args and cwd and name:
                logger.info("Installing '%s'.", name)
                with Popen(args, stderr=PIPE, stdout=PIPE, cwd=cwd) as p:
                    stderr = p.stderr.read()
                    if stderr:
                        logger.error(
                            "The 'install' for %s failed(%s).",
                            name, stderr)
                    else:
                        logger.info(
                            "The 'install' for %s finished.",
                            name)
            else:
                logger.warning("""Cannot proceed with the 'install' operation.
                               Some required params are missing
                               name:%s, args:%s, cwd:%s.""",
                               name, args, cwd)
        except Exception as e:
            logger.error("Installation of %s failed(%s).", name, e)
            raise

    def start_of_app(self, name: str, args: list, cwd: str):
        """Start the app.

        Args:
        name (str)= the to be installed
        args (list)= the installation string
        cwd (str)= the cwd where the installation will run
        """
        if name and args and cwd:
            try:
                with Popen(args, stderr=PIPE, stdout=PIPE, cwd=cwd) as p:
                    stderr = p.stderr.read()
                    if stderr:
                        logger.error(
                            "The 'start of app' operation for %s failed(%s).",
                            name, stderr)
                    else:
                        logger.info(
                            "The 'start of app' operation for %s has finished.",
                            name)
            except Exception as e:
                logger.info(
                    "Tried to start '%s' but failed(%s).", args, e)
        else:
            logger.warning("""Cannot proceed with the 'install' operation.
                           Some required params are missing
                           name:%s, args:%s, cwd:%s.""",
                           name, args, cwd)
