import logging
from sys import stdout


class BaseFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    pink = "\x1b[38;5;219m"
    aqua = "\x1b[38;5;51m" 
    purple = "\x1b[38;5;135m"
    green = "\x1b[38;5;121m"
    darkgreen = "\x1b[32;1m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, message_format="%(asctime)s: %(levelname)s: %(message)s (%(filename)s:%(lineno)d)"):
        super().__init__()
        self.message_format = message_format
        self.formats = {
            logging.DEBUG: self.pink + self.message_format + self.reset,
            logging.INFO: self.green + self.message_format + self.reset,
            logging.WARNING: self.yellow + self.message_format + self.reset,
            logging.ERROR: self.red + self.message_format + self.reset,
            logging.CRITICAL: self.bold_red + self.message_format + self.reset,
        }

    def format(self, record):
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class BaseLogger(logging.Logger):
    def __init__(self, name, level=logging.DEBUG):
        logging.Logger.__init__(self, name, level)

        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(BaseFormatter())
        self.addHandler(handler)
        
    
class StreamingFormatter(BaseFormatter):
    
    def __init__(self, message_format="%(message)s"):
        super().__init__(message_format)

class StreamingLogger(logging.Logger):
    def __init__(self, name, level=logging.DEBUG):
        logging.Logger.__init__(self, name, level)
        handler = logging.StreamHandler(stream=stdout)
        handler.terminator = ""
        handler.setLevel(level)
        handler.setFormatter(StreamingFormatter())
        self.addHandler(handler)
        
    def flush(self):
        self.handlers[0].flush()
        self.log(logging.INFO, "\n \n")