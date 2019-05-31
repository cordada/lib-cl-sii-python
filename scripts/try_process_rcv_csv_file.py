#!/usr/bin/env python
"""
TODO
==============

Does X and Y, and then Z.

Example
-------

TOD
For example, to do X, run::

    ./scripts/example.py arg1 arg2 arg3

"""
import logging
import os
import sys
from datetime import datetime

try:
    import cl_sii  # noqa: F401
except ImportError:
    # If package 'cl-sii' is not installed, try appending the project repo directory to the
    #   Python path, assuming thath we are in the project repo. If not, it will fail nonetheless.
    sys.path.append(os.path.dirname(os.path.abspath(__name__)))
    import cl_sii  # noqa: F401

import cl_sii.rcv.parse_csv
from cl_sii.libs import rows_processing
from cl_sii.rut import Rut


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

def main_rcv_compra_registro(
    receptor_rut: Rut,
    receptor_razon_social: str,
    input_file_path: str,
    n_rows_offset: int = 0,
    max_n_rows: int = 10000,
) -> None:
    start_ts = datetime.now()

    errors = []
    try:
        g = cl_sii.rcv.parse_csv.parse_rcv_compra_registro_csv_file(
            receptor_rut,
            receptor_razon_social,
            input_file_path,
            n_rows_offset,
            max_n_rows)

        row_ix = 0
        for dte_data, row_ix, row_data, row_errors in g:
            print(f"row_ix: {row_ix}; {dte_data}; {row_errors}")

            # Save errors.
            if row_errors:
                errors.append((row_ix, row_errors))

        n_rows_proccesed = row_ix

        if n_rows_proccesed == 0:
            logger.warning("No rows were processed.")
        else:
            logger.info(f"Rows processed: {n_rows_proccesed}")
        if errors:
            logger.error("Errors processing rows:\n%s", repr(errors))
    except FileNotFoundError:
        logger.exception(
            "Process aborted: a file could not be opened.")
    except rows_processing.MaxRowsExceeded:
        logger.warning(
            "Process stopped: the max number of data rows limit was reached.", exc_info=True)
    except KeyboardInterrupt:
        logger.error("Process interrupted by user.")
    except Exception:
        logger.exception("Process aborted.")
    finally:
        try:
            # "Action: clean up resources and connections"
            logger.info("Cleaned up resources and connections.")
        except Exception:
            logger.exception("Failed to clean up resources and connections.")

        finish_ts = datetime.now()
        duration = finish_ts - start_ts

        logger.info(f"start: {start_ts.isoformat()}")
        logger.info(f"finish: {finish_ts.isoformat()}")
        logger.info(f"duration: {duration!s}")


def main_rcv_compra_no_incluir(
    receptor_rut: Rut,
    receptor_razon_social: str,
    input_file_path: str,
    n_rows_offset: int = 0,
    max_n_rows: int = 10000,
) -> None:
    start_ts = datetime.now()

    errors = []
    try:
        g = cl_sii.rcv.parse_csv.parse_rcv_compra_no_incluir_csv_file(
            receptor_rut,
            receptor_razon_social,
            input_file_path,
            n_rows_offset,
            max_n_rows)

        row_ix = 0
        for dte_data, row_ix, row_data, row_errors in g:
            print(f"row_ix: {row_ix}; {dte_data}; {row_errors}")

            # Save errors.
            if row_errors:
                errors.append((row_ix, row_errors))

        n_rows_proccesed = row_ix

        if n_rows_proccesed == 0:
            logger.warning("No rows were processed.")
        else:
            logger.info(f"Rows processed: {n_rows_proccesed}")
        if errors:
            logger.error("Errors processing rows:\n%s", repr(errors))
    except FileNotFoundError:
        logger.exception(
            "Process aborted: a file could not be opened.")
    except rows_processing.MaxRowsExceeded:
        logger.warning(
            "Process stopped: the max number of data rows limit was reached.", exc_info=True)
    except KeyboardInterrupt:
        logger.error("Process interrupted by user.")
    except Exception:
        logger.exception("Process aborted.")
    finally:
        try:
            # "Action: clean up resources and connections"
            logger.info("Cleaned up resources and connections.")
        except Exception:
            logger.exception("Failed to clean up resources and connections.")

        finish_ts = datetime.now()
        duration = finish_ts - start_ts

        logger.info(f"start: {start_ts.isoformat()}")
        logger.info(f"finish: {finish_ts.isoformat()}")
        logger.info(f"duration: {duration!s}")


def main_rcv_compra_reclamado(
    receptor_rut: Rut,
    receptor_razon_social: str,
    input_file_path: str,
    n_rows_offset: int = 0,
    max_n_rows: int = 10000,
) -> None:
    start_ts = datetime.now()

    errors = []
    try:
        g = cl_sii.rcv.parse_csv.parse_rcv_compra_reclamado_csv_file(
            receptor_rut,
            receptor_razon_social,
            input_file_path,
            n_rows_offset,
            max_n_rows)

        row_ix = 0
        for dte_data, row_ix, row_data, row_errors in g:
            print(f"row_ix: {row_ix}; {dte_data}; {row_errors}")

            # Save errors.
            if row_errors:
                errors.append((row_ix, row_errors))

        n_rows_proccesed = row_ix

        if n_rows_proccesed == 0:
            logger.warning("No rows were processed.")
        else:
            logger.info(f"Rows processed: {n_rows_proccesed}")
        if errors:
            logger.error("Errors processing rows:\n%s", repr(errors))
    except FileNotFoundError:
        logger.exception(
            "Process aborted: a file could not be opened.")
    except rows_processing.MaxRowsExceeded:
        logger.warning(
            "Process stopped: the max number of data rows limit was reached.", exc_info=True)
    except KeyboardInterrupt:
        logger.error("Process interrupted by user.")
    except Exception:
        logger.exception("Process aborted.")
    finally:
        try:
            # "Action: clean up resources and connections"
            logger.info("Cleaned up resources and connections.")
        except Exception:
            logger.exception("Failed to clean up resources and connections.")

        finish_ts = datetime.now()
        duration = finish_ts - start_ts

        logger.info(f"start: {start_ts.isoformat()}")
        logger.info(f"finish: {finish_ts.isoformat()}")
        logger.info(f"duration: {duration!s}")


def main_rcv_compra_pendiente(
    receptor_rut: Rut,
    receptor_razon_social: str,
    input_file_path: str,
    n_rows_offset: int = 0,
    max_n_rows: int = 10000,
) -> None:
    start_ts = datetime.now()

    errors = []
    try:
        g = cl_sii.rcv.parse_csv.parse_rcv_compra_pendiente_csv_file(
            receptor_rut,
            receptor_razon_social,
            input_file_path,
            n_rows_offset,
            max_n_rows)

        row_ix = 0
        for dte_data, row_ix, row_data, row_errors in g:
            print(f"row_ix: {row_ix}; {dte_data}; {row_errors}")

            # Save errors.
            if row_errors:
                errors.append((row_ix, row_errors))

        n_rows_proccesed = row_ix

        if n_rows_proccesed == 0:
            logger.warning("No rows were processed.")
        else:
            logger.info(f"Rows processed: {n_rows_proccesed}")
        if errors:
            logger.error("Errors processing rows:\n%s", repr(errors))
    except FileNotFoundError:
        logger.exception(
            "Process aborted: a file could not be opened.")
    except rows_processing.MaxRowsExceeded:
        logger.warning(
            "Process stopped: the max number of data rows limit was reached.", exc_info=True)
    except KeyboardInterrupt:
        logger.error("Process interrupted by user.")
    except Exception:
        logger.exception("Process aborted.")
    finally:
        try:
            # "Action: clean up resources and connections"
            logger.info("Cleaned up resources and connections.")
        except Exception:
            logger.exception("Failed to clean up resources and connections.")

        finish_ts = datetime.now()
        duration = finish_ts - start_ts

        logger.info(f"start: {start_ts.isoformat()}")
        logger.info(f"finish: {finish_ts.isoformat()}")
        logger.info(f"duration: {duration!s}")


def main_rcv_venta(
    emisor_rut: Rut,
    emisor_razon_social: str,
    input_file_path: str,
    n_rows_offset: int = 0,
    max_n_rows: int = 10000,
) -> None:
    start_ts = datetime.now()

    errors = []
    try:
        g = cl_sii.rcv.parse_csv.parse_rcv_venta_csv_file(
            emisor_rut,
            emisor_razon_social,
            input_file_path,
            n_rows_offset,
            max_n_rows)

        row_ix = 0
        for dte_data, row_ix, row_data, row_errors in g:
            print(f"row_ix: {row_ix}; {dte_data}; {row_errors}")

            # Save errors.
            if row_errors:
                errors.append((row_ix, row_errors))

        n_rows_proccesed = row_ix

        if n_rows_proccesed == 0:
            logger.warning("No rows were processed.")
        else:
            logger.info(f"Rows processed: {n_rows_proccesed}")
        if errors:
            logger.error("Errors processing rows:\n%s", repr(errors))
    except FileNotFoundError:
        logger.exception(
            "Process aborted: a file could not be opened.")
    except rows_processing.MaxRowsExceeded:
        logger.warning(
            "Process stopped: the max number of data rows limit was reached.", exc_info=True)
    except KeyboardInterrupt:
        logger.error("Process interrupted by user.")
    except Exception:
        logger.exception("Process aborted.")
    finally:
        try:
            # "Action: clean up resources and connections"
            logger.info("Cleaned up resources and connections.")
        except Exception:
            logger.exception("Failed to clean up resources and connections.")

        finish_ts = datetime.now()
        duration = finish_ts - start_ts

        logger.info(f"start: {start_ts.isoformat()}")
        logger.info(f"finish: {finish_ts.isoformat()}")
        logger.info(f"duration: {duration!s}")


if __name__ == '__main__':
    # main(
    #     receptor_rut=Rut(sys.argv[1], validate_dv=True),
    #     receptor_razon_social=sys.argv[2],
    #     input_file_path=sys.argv[3],
    #     n_rows_offset=int(sys.argv[4]),
    #     max_n_rows=int(sys.argv[5]),
    # )
    # main_rcv_compra_registro(
    #     receptor_rut=Rut('76389992-6', validate_dv=True),
    #     receptor_razon_social='ST CAPITAL S.A.',
    #     input_file_path='wip/rcv/RCV_COMPRA_REGISTRO_76389992-6_201904.csv',
    #     n_rows_offset=0,
    #     # max_n_rows=int(sys.argv[5]),
    # )
    # main_rcv_compra_registro(
    #     receptor_rut=Rut('76555835-2', validate_dv=True),
    #     receptor_razon_social='Fynpal SpA',
    #     input_file_path='wip/rcv/fynpal/RCV_COMPRA_REGISTRO_76555835-2_201805.csv',
    #     n_rows_offset=0,
    #     # max_n_rows=int(sys.argv[5]),
    # )
    # main_rcv_compra_pendiente(
    #     receptor_rut=Rut('76555835-2', validate_dv=True),
    #     receptor_razon_social='Fynpal SpA',
    #     input_file_path='wip/rcv/fynpal/RCV_COMPRA_PENDIENTE_76555835-2_201905.csv',
    #     n_rows_offset=0,
    #     # max_n_rows=int(sys.argv[5]),
    # )
    # main_rcv_compra_pendiente(
    #     receptor_rut=Rut('96874030-K', validate_dv=True),
    #     receptor_razon_social='EMPRESAS LA POLAR S.A.',
    #     input_file_path='wip/rcv/data-lapolar/RCV_COMPRA_PENDIENTE_96874030_201905.csv',
    #     n_rows_offset=0,
    #     # max_n_rows=int(sys.argv[5]),
    # )
    # main_rcv_compra_no_incluir(
    #     receptor_rut=Rut('96874030-K', validate_dv=True),
    #     receptor_razon_social='EMPRESAS LA POLAR S.A.',
    #     input_file_path='wip/rcv/data-lapolar/RCV_COMPRA_NO_INCLUIR_96874030-K_201807.csv',
    #     n_rows_offset=0,
    #     # max_n_rows=int(sys.argv[5]),
    # )
    # main_rcv_compra_reclamado(
    #     receptor_rut=Rut('96874030-K', validate_dv=True),
    #     receptor_razon_social='EMPRESAS LA POLAR S.A.',
    #     input_file_path='wip/rcv/data-lapolar/RCV_COMPRA_RECLAMADO_96874030-K_201805.csv',
    #     n_rows_offset=0,
    #     # max_n_rows=int(sys.argv[5]),
    # )
    main_rcv_compra_reclamado(
        receptor_rut=Rut('76389992-6', validate_dv=True),
        receptor_razon_social='ST CAPITAL S.A.',
        input_file_path='wip/rcv/st-capital/RCV_COMPRA_RECLAMADO_76389992-6_201905.csv',
        n_rows_offset=0,
        # max_n_rows=int(sys.argv[5]),
    )

    # main_rcv_venta(
    #     emisor_rut=Rut(sys.argv[1], validate_dv=True),
    #     emisor_razon_social=sys.argv[2],
    #     input_file_path=sys.argv[3],
    #     n_rows_offset=int(sys.argv[4]),
    #     # max_n_rows=int(sys.argv[5]),
    # )
    # main_rcv_venta(
    #     emisor_rut=Rut('76389992-6', validate_dv=True),
    #     emisor_razon_social='ST CAPITAL S.A.',
    #     input_file_path='wip/rcv/RCV_VENTA_76389992-6_201904.csv',
    #     n_rows_offset=0,
    #     # max_n_rows=int(sys.argv[5]),
    # )
