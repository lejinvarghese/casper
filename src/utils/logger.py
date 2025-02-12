from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    Formatter,
    Logger,
    StreamHandler,
)
from sys import stdout

m_colors = {
    "red": (255, 69, 0),
    "green": (0, 250, 154),
    "yellow": (252, 255, 156),
    "warning": (255, 165, 0),
    "aqua": (127, 255, 212),
    "blue": (100, 149, 237),
    "pink": (255, 105, 180),
    "white": (255, 240, 245),
    "ghost": (240, 255, 240),
}


class BaseFormatter(Formatter):
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

    def __init__(
        self,
        message_format="%(asctime)s: %(levelname)s: %(message)s (%(filename)s:%(lineno)d)",
    ):
        super().__init__()
        self.message_format = message_format
        self.formats = {
            DEBUG: self.aqua + self.message_format + self.reset,
            INFO: self.green + self.message_format + self.reset,
            WARNING: self.yellow + self.message_format + self.reset,
            ERROR: self.red + self.message_format + self.reset,
            CRITICAL: self.bold_red + self.message_format + self.reset,
        }

    def format(self, record):
        log_fmt = self.formats.get(record.levelno)
        formatter = Formatter(log_fmt)
        return formatter.format(record)


class BaseLogger(Logger):
    def __init__(self, name, level=DEBUG):
        Logger.__init__(self, name, level)

        handler = StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(BaseFormatter())
        self.addHandler(handler)


class StreamingFormatter(BaseFormatter):
    def __init__(self, message_format="%(message)s"):
        super().__init__(message_format)


class StreamingLogger(Logger):
    def __init__(self, name, level=DEBUG):
        Logger.__init__(self, name, level)
        handler = StreamHandler(stream=stdout)
        handler.terminator = ""
        handler.setLevel(level)
        handler.setFormatter(StreamingFormatter())
        self.addHandler(handler)

    def flush(self):
        self.handlers[0].flush()
        self.log(INFO, "\n \n")
