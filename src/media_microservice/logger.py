"""Lambda Logging Module"""
import logging


def start_log(method: str) -> None:
    """LOG HTTP Method Info

    Args:
        method (str): http method
    """
    class StacktraceLogFormatter(logging.Formatter):
        """Log Formatter Subclass

        - Add HTTP Method
        """

        def format(self, record: logging.LogRecord) -> str:
            try:
                time = self.formatTime(record, self.datefmt)
                exc = self.formatException(record.exc_info) if record.exc_info else None
                s = record.getMessage()

                message = f"{time} <HTTP> {record.HTTP_METHOD}: {s} \n"  # type: ignore[attr-defined]
                if record.levelno > 30:
                    message = message + f"\nOrigin:\n {exc}"
                return "".join(
                    [message[i: i + 75] + "\n\t" for i in range(0, len(message), 75)]
                )
            except Exception as e:
                return f"Logging Error: {e}"

    class LogFilter(object):
        """Log Filter"""

        def __init__(self, level: int) -> None:
            self.__level = level

        def filter(self, log_record: logging.LogRecord) -> bool:
            """Filter Func

            - Set HTTP_METHOD attribute on log-record for logging.

            Args:
                log_record (logging.LogRecord): log record.

            Returns:
                bool: record is <= set-level
            """
            setattr(log_record, 'HTTP_METHOD', method)
            result: bool = log_record.levelno <= self.__level
            return result

    formatter = StacktraceLogFormatter()

    log_handler = logging.Handler(logging.DEBUG)
    log_handler.addFilter(LogFilter(logging.DEBUG))
    log_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[log_handler],
        force=True,
    )
