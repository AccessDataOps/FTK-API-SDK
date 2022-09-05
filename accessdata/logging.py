## /logging.py

"""

"""

from logging import basicConfig, getLogger, DEBUG
from pathlib import Path
from os import getlogin
from sys import platform

##

__all__ = ("logger", "set_logging_level", )

##

if platform == "win32":
	USER_NAME = getlogin()
	LOG_PATH = r"C:\ProgramData\AccessData\SDK\accessdata-sdk.log"
else:
	LOG_PATH = r"accessdata-sdk.log"

##

logfile = Path(LOG_PATH)
logfile.parent.mkdir(parents=True, exist_ok=True)
logfile.touch(exist_ok=True)

basicConfig(filename=logfile, format='%(asctime)s - %(levelname)s:%(message)s')
logger = getLogger("accessdata")
logger.setLevel(DEBUG)

def set_logging_level(level):
	"""Sets the logging level for the library.

	:param level: The level to set internally.
	:type level: int
	"""
	logger.setLevel(level)
