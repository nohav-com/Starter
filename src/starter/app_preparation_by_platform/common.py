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

    def install(self, name, args, cwd):
        """Install what needs to be installed.

        Args:
        name = what is to be installed
        args = installation string
        cwd = cwd where to run installation
        """
        try:
            if args and cwd and name:
                logger.info("Installing '%s'.", name)
                with Popen(args, stderr=PIPE, stdout=PIPE, cwd=cwd) as p:
                    stderr = p.stderr.read()
                    if stderr:
                        logger.error(
                            "Operation 'install' of %s failed(%s).",
                            name, stderr)
                    else:
                        logger.info(
                            "Operation 'install' of %s finished.",
                            name)
            else:
                logger.warning("""Cannot proceed with operation 'install'.
                               Some required params are missing
                               name:%s, args:%s, cwd:%s""",
                               name, args, cwd)
        except Exception as e:
            logger.error("Installation of %s failed(%s).", name, e)
            raise

    def start_of_app(self, name, args, cwd):
        """Start the app.

        Args:
        name = what is to be installed
        args = installation string
        cwd = cwd where to run installation
        """
        if name and args and cwd:
            try:
                with Popen(args, stderr=PIPE, stdout=PIPE, cwd=cwd) as p:
                    stderr = p.stderr.read()
                    if stderr:
                        logger.error(
                            "Operation 'start of app' of %s failed(%s).",
                            name, stderr)
                    else:
                        logger.info(
                            "Operation 'start of app' of %s finished.",
                            name)
            except Exception as e:
                logger.info(
                    "Try to start '%s' and failed(%s).", args, e)
        else:
            logger.warning("""Cannot properly start app.
                           Some required params are missing
                           name:%s, args:%s, cwd:%s""",
                           name, args, cwd)
