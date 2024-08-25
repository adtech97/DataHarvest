import logging

from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class CustomLogger:

    def __init__(self, file_name, log_level=logging.DEBUG, max_size=1000000, backup_count=5, when='midnight', interval=1):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        #log formatter 
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        #size based file rotation handeling
        rotating_handler = RotatingFileHandler(file_name, maxBytes=max_size, backupCount=backup_count)
        rotating_handler.setFormatter(formatter)

        #timed rotation
        time_handler = TimedRotatingFileHandler(file_name, when=when, interval=interval, backupCount=backup_count)
        time_handler.setFormatter(formatter)

        self.logger.addHandler(rotating_handler)
        self.logger.addHandler(time_handler)
