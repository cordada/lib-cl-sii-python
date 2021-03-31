#!/usr/bin/env python

import logging
import os
import openpyxl
import sys


try:
    import cl_sii  # noqa: F401
except ImportError:
    # If package 'cl-sii' is not installed, try appending the project repo directory to the
    #   Python path, assuming thath we are in the project repo. If not, it will fail nonetheless.
    sys.path.append(os.path.dirname(os.path.abspath(__name__)))
    import cl_sii  # noqa: F401

from cl_sii.libs import xml_utils
from cl_sii.rtc.data_models_aec import AecXml
from cl_sii.rtc.parse_aec import parse_aec_xml


ROW_COLUMN_COUNT = 3
ROW_HEADER = [
    "fecha_firma_dt (YYYY-MM-DDThh:mm:ss)",
    "fecha_cesion_dt (YYYY-MM-DDThh:mm:ss)",
    "TIME ELAPSE (In seconds)",
]
logger = logging.getLogger(__name__)


def read_file_bytes(filepath: str) -> bytes:
    with open(filepath, mode='rb') as file:
        content = file.read()

    return content


def to_aecxml_obj(filepath: str) -> AecXml:
    aec_xml_bytes: bytes = read_file_bytes(filepath)
    xml_doc = xml_utils.parse_untrusted_xml(aec_xml_bytes)
    aec_xml = parse_aec_xml(xml_doc)

    return aec_xml


def write_excel(filename, rows):
    wb = openpyxl.Workbook()
    ws1 = wb.active

    # Append header
    ws1.append(ROW_HEADER)

    for row in rows:
        ws1.append(process_row(row))

    wb.save(filename=filename)


def is_valid_row(row):
    if len(row) == ROW_COLUMN_COUNT:
        return True
    else:
        return False


def process_row(row):
    output_row = []
    for item in row:
        if isinstance(item, str) and item.isdigit():
            output_row.append(int(item))
        else:
            output_row.append(item)

    if not is_valid_row(output_row):
        raise ValueError('Invalid row:', output_row)

    return output_row


def read_aec_files(directory: str):
    for entry in os.scandir(directory):
        if not entry.path.lower().endswith(".xml"):
            logger.warning('Skipping file %s because it\'s extension is not xml', entry.path)
            continue

        try:
            aecxml_obj = to_aecxml_obj(entry.path)
        except ValueError as exc:
            logger.error('Skipping file %s', entry.path, str(exc))
            continue
        elapse = aecxml_obj.fecha_firma_dt - aecxml_obj.fecha_cesion_dt
        file_metadata = [
            aecxml_obj.fecha_firma_dt.isoformat(),
            aecxml_obj.fecha_cesion_dt.isoformat(),
            elapse.total_seconds(),
        ]
        # file_metadata = ",".join()

        yield file_metadata


def main(args=()):
    args = args or sys.argv[1:]

    logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(name)s[%(process)d]: [%(levelname)s] %(message)s',
    )

    logger.info('Args: %s', args)

    aec_directory = str(args[0])
    xlsx_filename = str(args[1])

    files = read_aec_files(aec_directory)
    write_excel(xlsx_filename, files)


if __name__ == '__main__':
    main()
