import logging
from colorlog import ColoredFormatter

STREAM_LOG_LEVEL = logging.DEBUG
FILE_LOG_LEVEL = logging.DEBUG
ERROR_FILE_LOG_LEVEL = logging.ERROR

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

g_fileh = logging.FileHandler("./logs/general.log")
g_fileh.setLevel(FILE_LOG_LEVEL)
g_fileh.setFormatter(logger_formatter)

r_fileh = logging.FileHandler("./logs/reqs.log")
r_fileh.setLevel(FILE_LOG_LEVEL)
r_fileh.setFormatter(logger_formatter)

e_fileh = logging.FileHandler("./logs/error.log")
e_fileh.setLevel(ERROR_FILE_LOG_LEVEL)
e_fileh.setFormatter(logger_formatter)

general_log = logging.getLogger("general")
general_log.setLevel(logging.DEBUG)
general_log.addHandler(g_fileh)
general_log.addHandler(e_fileh)
general_log.addHandler(streamh)

reqs_log = logging.getLogger("reqs")
reqs_log.setLevel(logging.DEBUG)
reqs_log.addHandler(r_fileh)
reqs_log.addHandler(e_fileh)

# logger.debug("test")
# logger.info("test")
# logger.warning("test")
# logger.error("test")
# logger.critical("test")
