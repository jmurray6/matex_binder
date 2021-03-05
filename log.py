import logging
import sys

logging.basicConfig(
    level=logging.INFO, 
    format='[{%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(filename='tmp6a.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('LOGGER_NAME')