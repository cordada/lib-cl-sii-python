#!/usr/bin/env python
"""
Example script
==============


Example::

    ./scripts/example.py arg1 arg2 arg3

"""
import os
import sys
from typing import Sequence

try:
    import cl_sii  # noqa: F401
except ImportError:
    # If package 'cl-sii' is not installed, try appending the project repo directory to the
    #   Python path, assuming thath we are in the project repo. If not, it will fail nonetheless.
    sys.path.append(os.path.dirname(os.path.abspath(__name__)))
    import cl_sii  # noqa: F401


def main(args: Sequence[str]) -> None:
    print("Example script.")
    print(f"Args: {args!s}")


if __name__ == '__main__':
    main(sys.argv[1:])
