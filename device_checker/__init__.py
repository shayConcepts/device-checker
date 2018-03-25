import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from device_checker.__info__ import APP_NAME, APP_VERSION

# -- Paths

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
_program_files = os.environ.get('PROGRAMFILES')
if ROOT_PATH.startswith(_program_files):
    ROOT_PATH = os.path.dirname(ROOT_PATH)
    WRITE_PATH = os.environ['APPDATA']
    WRITE_PATH = str(Path(WRITE_PATH, 'shayConcepts', APP_NAME))
else:
    WRITE_PATH = ROOT_PATH
    if getattr(sys, 'frozen', False):
        ROOT_PATH = os.path.dirname(ROOT_PATH)

_log_path = str(Path(WRITE_PATH, 'device_checker.log'))


def get_root_path(*args) -> str:
    """
    Return ROOT program path

    :return: ROOT program path
    """

    return str(Path(ROOT_PATH, *args))


def get_write_path(*args) -> str:
    """
    Get path to write files

    :return: Path to write files
    """

    return str(Path(WRITE_PATH, *args))


def _create_write_path():
    """
    Create WRITE_PATH
    """

    path = get_write_path()
    Path(path).mkdir(parents=True, exist_ok=True)


_create_write_path()
# --

# -- Logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(name)-6s %(levelname)-8s %(message)s')

# Console logging
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# File logging
handler = RotatingFileHandler(_log_path, mode='a', maxBytes=10 * 1024 * 1024, backupCount=1, encoding='utf-8', delay=0)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

logger.setLevel(logging.DEBUG)
# --

logger.info("{} v{}".format(APP_NAME, APP_VERSION))
logger.debug("_program_files: '{}'".format(_program_files))
logger.debug("log path: '{}'".format(_log_path))
logger.info("ROOT_PATH: '{}'".format(ROOT_PATH))
logger.info("WRITE_PATH: '{}'".format(WRITE_PATH))
