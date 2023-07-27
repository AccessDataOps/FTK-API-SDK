## /logging.py

"""

"""

from logging import basicConfig, getLogger, DEBUG, ERROR
from pathlib import Path
from os import getlogin
from sys import platform

##

__all__ = ("logger", "set_logging_level", )

##

if platform == "win32":
	USER_NAME = getlogin()
	LOG_PATH = r"C:\Users\Public\Public Logs\AccessDataLogs\exterro-ftk-sdk.log"
else:
	from os import getuid
	from pwd import getpwuid
	USER_NAME = getpwuid(getuid()).pw_name
	LOG_PATH = r"/var/log/exterro/exterro-ftk-sdk.log"

##

logfile = Path(LOG_PATH)
logfile.parent.mkdir(parents=True, exist_ok=True)
logfile.touch(exist_ok=True)

basicConfig(filename=logfile, format=USER_NAME + ' - %(asctime)s - %(levelname)s:%(message)s')
logger = getLogger("exterro")
logger.setLevel(ERROR)

def set_logging_level(level):
	"""Sets the logging level for the library.

	:param level: The level to set internally.
	:type level: int
	"""
	logger.setLevel(level)