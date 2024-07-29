import logging
import requests
from colorlog import ColoredFormatter

STREAM_LOG_LEVEL = logging.INFO
FILE_LOG_LEVEL = logging.DEBUG

LOGFORMAT = "%(log_color)s[%(levelname)s] %(asctime)s %(filename)s:%(funcName)s():(%(lineno)s) - %(message)s%(reset)s"
logger_formatter = ColoredFormatter(
        LOGFORMAT,
        log_colors={
            'DEBUG': 'white',
            # INFO имеет белый цвет по умолчанию
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        })

streamh = logging.StreamHandler()
streamh.setLevel(STREAM_LOG_LEVEL)
streamh.setFormatter(logger_formatter)

fileh = logging.FileHandler("./logs/general.log")
fileh.setLevel(FILE_LOG_LEVEL)
fileh.setFormatter(logger_formatter)

general_log = logging.getLogger("general")
general_log.setLevel(logging.DEBUG)
general_log.addHandler(fileh)
general_log.addHandler(streamh)

fileh = logging.FileHandler("./logs/reqs.log")
fileh.setLevel(FILE_LOG_LEVEL)
fileh.setFormatter(logger_formatter)

reqs_log = logging.getLogger("reqs")
reqs_log.setLevel(logging.DEBUG)
reqs_log.addHandler(fileh)
reqs_log.addHandler(streamh)

# logger.debug("test")
# logger.info("test")
# logger.warning("test")
# logger.error("test")
# logger.critical("test")
