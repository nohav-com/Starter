"""Common methods"""
import logging
import os
import sys
from subprocess import Popen, PIPE
from threading import Thread

__all__ = ['CommonPreparationByPlatform']

logger = logging.getLogger(__name__)


class CommonPreparationByPlatform():
    def __init__(self):
        pass

    def install(self, name, args, cwd):
        """Install what needs to be installed.add()

        Params:
        name = what is to be installed
        args = installation string
        cwd = cwd where to run installation
        """
        try:
            if args and cwd and name:
                # Foreplay
                progress = None
                term = '\n'
                if progress is not None:
                    progress('Installing %s ...%s' % (name, term), 'main')
                else:
                    sys.stderr.write('Installing %s ...%s' % (name, term))
                    sys.stderr.flush()
                # Lets install it
                progress = None
                os.chdir(cwd)
                p = Popen(args,
                          stdout=PIPE,
                          stderr=PIPE,
                          cwd=cwd)
                t1 = Thread(target=self.reader, args=(p.stdout, 'stdout'))
                t1.start()
                t2 = Thread(target=self.reader, args=(p.stderr, 'stderr'))
                t2.start()
                p.wait()
                t1.join()
                t2.join()
                if progress is not None:
                    progress('done.', 'main')
                else:
                    sys.stderr.write('done.\n')
        except Exception as e:
            logger.error("Installation of {%s} failed. {%s}" % (args, e))

    def reader(self, stream, context):
        """
        Read lines from a subprocess' output stream and either pass to a
        progress callable (if specified) or write progress information
        to sys.stderr.
        """
        progress = None
        while True:
            s = stream.readline()
            if not s:
                break
            if progress is not None:
                # progress(s, context)
                progress(s, context)
            else:
                try:
                    sys.stderr.write(s.decode('utf-8'))
                    sys.stderr.flush()
                except Exception:
                    # Better ask for forgiveness than permission
                    sys.stderr.write(s.decode('windows-1250'))
                    sys.stderr.flush()
        stream.close()
