#!/usr/bin/env python
"""
Example script
==============

Does X and Y, and then Z.

Example
-------

For example, to do X, run::

    ./scripts/example.py arg1 arg2 arg3

"""
import logging
import os
import sys
from datetime import datetime
from typing import Sequence


try:
    import cl_sii  # noqa: F401
except ImportError:
    # If package 'cl-sii' is not installed, try appending the project repo directory to the
    #   Python path, assuming thath we are in the project repo. If not, it will fail nonetheless.
    sys.path.append(os.path.dirname(os.path.abspath(__name__)))
    import cl_sii  # noqa: F401


logger = logging.getLogger(__name__)
root_logger = logging.getLogger()


###############################################################################
# logging config
###############################################################################

_loggers = [logger, logging.getLogger('cl_sii')]
for _logger in _loggers:
    _logger.addHandler(logging.StreamHandler())
    _logger.setLevel(logging.INFO)

root_logger.setLevel(logging.WARNING)


###############################################################################
# script
###############################################################################


def main(args: Sequence[str]) -> None:
    start_ts = datetime.now()

    logger.debug("Example script. Args: %s", args)

    try:
        print("Action: do something")
    except FileNotFoundError:
        logger.exception("Process aborted: a file could not be opened.", exc_info=True)
    except KeyboardInterrupt:
        logger.error("Process interrupted by user.")
    except Exception:
        logger.exception("Process aborted.")
    finally:
        try:
            print("Action: clean up resources and connections")
            logger.info("Cleaned up resources and connections.")
        except Exception:
            logger.exception("Failed to clean up resources and connections.")

        finish_ts = datetime.now()
        duration = finish_ts - start_ts

        logger.info(f"start: {start_ts.isoformat()}")
        logger.info(f"finish: {finish_ts.isoformat()}")
        logger.info(f"duration: {duration!s}")


if __name__ == '__main__':
    main(sys.argv[1:])
