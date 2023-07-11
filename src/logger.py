import logging

_format = f"%(asctime)s [%(levelname)s] - %(name)s - %(funcName)s(%(lineno)d) - %(message)s - %(pathname)s - %(msecs)d"

file = 'src/data/hw_logs.log'


file_handler = logging.FileHandler(file)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(_format))

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter(_format))


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


#
# logger = get_logger(name)
#
# logger.debug('Start program!')
# logger.info(f'Client name: {client_1.name}, \n')
# logger.warning(f'Client {client_1.name} spent: {client_1.get_check()}')