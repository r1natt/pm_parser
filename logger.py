import logging
from colorlog import ColoredFormatter

STREAM_LOG_LEVEL = logging.INFO
FILE_LOG_LEVEL = logging.DEBUG

LOGFORMAT = "%(log_color)s[%(levelname)s] %(asctime)s %(name)s %(filename)s:%(lineno)s %(funcName)s() - %(message)s%(reset)s"
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

fileh = logging.FileHandler("./logs/smpp.log")
fileh.setLevel(FILE_LOG_LEVEL)
fileh.setFormatter(logger_formatter)

logger = logging.getLogger("smpp")
logger.setLevel(logging.DEBUG)
logger.addHandler(fileh)
logger.addHandler(streamh)

api_fileh = logging.FileHandler("./logs/reqs.log")
api_fileh.setLevel(FILE_LOG_LEVEL)
api_fileh.setFormatter(logger_formatter)

api_logger = logging.getLogger("API")
api_logger.setLevel(logging.DEBUG)
api_logger.addHandler(api_fileh)
api_logger.addHandler(streamh)
