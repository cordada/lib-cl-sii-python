#!/usr/bin/env python
"""
Clean DTE XML files.


Example for a single file::

    ./scripts/clean_dte_xml_file.py file \
        'tests/test_data/sii-dte/DTE--76354771-K--33--170.xml' \
        'tests/test_data/sii-dte/DTE--76354771-K--33--170-clean.xml'


Example for all files in a directory::

    ./scripts/clean_dte_xml_file.py dir 'tests/test_data/sii-dte/'


"""
import difflib
import os
import pathlib
import sys
from typing import Iterable


try:
    import cl_sii  # noqa: F401
except ImportError:
    # If package 'cl-sii' is not installed, try appending the project repo directory to the
    #   Python path, assuming thath we are in the project repo. If not, it will fail nonetheless.
    sys.path.append(os.path.dirname(os.path.abspath(__name__)))
    import cl_sii  # noqa: F401

import cl_sii.dte.parse
from cl_sii.libs import xml_utils


# TODO: log messages instead of print.


def clean_dte_xml_file(input_file_path: str, output_file_path: str) -> Iterable[bytes]:
    with open(input_file_path, mode='rb') as f:
        file_bytes = f.read()

    xml_doc = xml_utils.parse_untrusted_xml(file_bytes)

    xml_doc_cleaned, modified = cl_sii.dte.parse.clean_dte_xml(
        xml_doc,
        set_missing_xmlns=True,
        remove_doc_personalizado=True,
    )

    # TODO: add exception with a nice message for the caller.
    cl_sii.dte.parse.validate_dte_xml(xml_doc_cleaned)

    with open(output_file_path, 'w+b') as f:
        xml_utils.write_xml_doc(xml_doc_cleaned, f)

    with open(output_file_path, mode='rb') as f:
        file_bytes_rewritten = f.read()

    # note: another way to compute the difference in a similar format is
    #   `diff -Naur $input_file_path $output_file_path`
    file_bytes_diff_gen = difflib.diff_bytes(
        dfunc=difflib.unified_diff, a=file_bytes.splitlines(), b=file_bytes_rewritten.splitlines()
    )

    return file_bytes_diff_gen


def main_single_file(input_file_path: str, output_file_path: str) -> None:
    file_bytes_diff_gen = clean_dte_xml_file(
        input_file_path=input_file_path, output_file_path=output_file_path
    )

    for diff_line in file_bytes_diff_gen:
        print(diff_line)


def main_dir_files(input_files_dir_path: str) -> None:
    for p in pathlib.Path(input_files_dir_path).iterdir():
        if not p.is_file():
            continue

        # e.g. 'an example.xml' -> 'an example.clean.xml'
        input_file_path = str(p)
        output_file_path = str(p.with_suffix(f'.clean{p.suffix}'))

        print(f"\n\nWill clean file '{input_file_path}' and save it to '{output_file_path}'.")
        file_bytes_diff_gen = clean_dte_xml_file(
            input_file_path=input_file_path, output_file_path=output_file_path
        )

        print("Difference between input and output files:")
        diff_line = None
        for diff_line in file_bytes_diff_gen:
            print(diff_line)
        if diff_line is None:
            print("No difference.")


if __name__ == '__main__':
    if sys.argv[1] == 'file':
        main_single_file(input_file_path=sys.argv[2], output_file_path=sys.argv[3])
    elif sys.argv[1] == 'dir':
        main_dir_files(input_files_dir_path=sys.argv[2])
    else:
        raise ValueError(f"Invalid option: '{sys.argv[1]}'")
