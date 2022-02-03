#!/usr/bin/env python
"""
Canonicalize XML files.


Convert XML to its C14N 2.0 serialised form (see also: https://www.w3.org/TR/xml-c14n2/).


Example for a single file::

    ./scripts/canonicalize_xml_file.py file \
        'tests/test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2.xml' \
        'tests/test_data/sii-rtc/AEC--76354771-K--33--170--SEQ-2-canonicalized-c14n.xml'


Example for all files in a directory::

    ./scripts/canonicalize_xml_file.py dir 'tests/test_data/sii-rtc/'
"""

from __future__ import annotations

import difflib
import os
import pathlib
import sys
import xml.etree.ElementTree
from typing import BinaryIO, Iterable, TextIO, Union


try:
    import cl_sii  # noqa: F401
except ImportError:
    # If package 'cl-sii' is not installed, try appending the project repo directory to the
    #   Python path, assuming thath we are in the project repo. If not, it will fail nonetheless.
    sys.path.append(os.path.dirname(os.path.abspath(__name__)))
    import cl_sii  # noqa: F401


# TODO: log messages instead of print.


def canonicalize_xml_file(
    input_file_path: pathlib.Path,
    output_file_path: pathlib.Path,
) -> Iterable[bytes]:
    if sys.version_info < (3, 8):
        raise NotImplementedError('Python version ≥ 3.8 required')

    f: Union[TextIO, BinaryIO]

    with open(input_file_path, mode='rb') as f:
        file_bytes = f.read()

    with open(output_file_path, 'wt') as f:
        xml.etree.ElementTree.canonicalize(xml_data=file_bytes, out=f)

    with open(output_file_path, mode='rb') as f:
        file_bytes_rewritten = f.read()

    # Note: Another way to compute the difference in a similar format is
    #   `diff -Naur $input_file_path $output_file_path`
    file_bytes_diff_gen = difflib.diff_bytes(
        dfunc=difflib.unified_diff,
        a=file_bytes.splitlines(),
        b=file_bytes_rewritten.splitlines(),
    )

    return file_bytes_diff_gen


def main_single_file(input_file_path: pathlib.Path, output_file_path: pathlib.Path) -> None:
    file_bytes_diff_gen = canonicalize_xml_file(
        input_file_path=input_file_path,
        output_file_path=output_file_path,
    )

    for diff_line in file_bytes_diff_gen:
        print(diff_line)


def main_dir_files(input_files_dir_path: pathlib.Path) -> None:
    for p in input_files_dir_path.iterdir():
        if not p.is_file():
            continue

        # e.g. 'an example.xml' -> 'an example.clean.xml'
        input_file_path = p
        output_file_path = p.with_suffix(f'.clean{p.suffix}')

        print(f"\n\nWill clean file '{input_file_path}' and save it to '{output_file_path}'.")
        file_bytes_diff_gen = canonicalize_xml_file(
            input_file_path=input_file_path,
            output_file_path=output_file_path,
        )

        print("Difference between input and output files:")
        diff_line = None
        for diff_line in file_bytes_diff_gen:
            print(diff_line)
        if diff_line is None:
            print("No difference.")


if __name__ == '__main__':
    if sys.argv[1] == 'file':
        main_single_file(
            input_file_path=pathlib.Path(sys.argv[2]),
            output_file_path=pathlib.Path(sys.argv[3]),
        )
    elif sys.argv[1] == 'dir':
        main_dir_files(
            input_files_dir_path=pathlib.Path(sys.argv[2]),
        )
    else:
        raise ValueError(f"Invalid option: '{sys.argv[1]}'")
