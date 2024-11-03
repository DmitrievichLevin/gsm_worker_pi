"""Global System Mobile Communication Interface"""
from __future__ import annotations

import logging
import os
import time
from abc import ABCMeta
from abc import abstractmethod
from typing import Any
from typing import Callable
from typing import cast
from typing import TypedDict

from serial import Serial
from serial import SerialException

from .sql_cursor import SQLCursor


class IComm(TypedDict):
    """Command Object(SQL Row)"""
    execution_time: int
    sent_time: int
    queue_no: int
    phone: str
    protocol: str
    context: str
    message: str


class GSM(Serial, SQLCursor):
    """GSM Concrete Class

    Args:
        SQLCursor (SQL): SQL Cursor

    Raises:
        KeyError: Invalid Serial Bus ID
        e: General Exception
    """
    serial: Serial
    baudrate: int = 115200
    tty_id: str

    def init(self) -> None:
        """Initialize Serial Device

       Raises:
           KeyError: Invalid Serial Bus ID
           e: General Exception
       """
        try:
            tty_id = os.environ.get('serial_bus_id')
            self.tty_id = cast(str, tty_id)
            super().__init__(tty_id, self.baudrate)
        except SerialException as e_s:
            _logmsg = f"Expected Serial Device {tty_id}, but found None."
            logging.error(_logmsg)
            self.handle_error(e_s)
        except Exception as e:
            _logmsg = f"Error Initializing Serial Device\n{e}"
            logging.error(_logmsg)
            self.handle_error(e)

    def handle_error(self, e: Exception) -> None:
        """Handle GSM Error

        # Return to Queue
        # Notify Manager of Failed Worker
        # Assign Queue to another Worker until this Worker is Running again.
        # TODO - Handle Error(RabbitMQ)

        Args:
            e (Exception): GSM Error
        """
        pass

    def send(self, command: type[IGSM_COMMAND], *args: tuple[Any], **kwargs: dict[str, Any]) -> bool:
        """Send GSM Command.

        Args:
            command (type[IGSM_COMMAND]): IGSM_COMMAND Subclass.

        Returns:
            bool: Success or failue of GSM Communication.
        """
        return command.command(self, *args, **kwargs)

    def send_at(self, command: str, timeout: int = 1) -> str:
        rec_buff = bytearray()
        wr_buff = f'AT+{command}\r\n'.encode()
        self.write(wr_buff)
        time.sleep(timeout)
        while True:
            time.sleep(0.05)
            line = self.readline()
            if not line:
                break
            rec_buff.extend(line)

        return bytes(rec_buff).decode()

    def health_check(self) -> None:
        """Check Health of GSM Serial Device"""
        if not self.send(HEALTHCHECK_GSM):
            _logmsg = f"No response from, GSM Device {self.tty_id}."
            self.handle_error(Exception(_logmsg))


def log_gsm(response: str) -> None:
    """LOG GSM Commands

    Args:
        response (str): response from write.
    """
    if 'ERROR' in response:
        logging.error(response)
    else:
        logging.debug(response)


def __command_decorator(dec_com: Callable[[type[IGSM_COMMAND]], str | tuple[str]]) -> Callable[[type[IGSM_COMMAND], GSM], str | tuple[str]]:
    """Pre/Post Command Decorator

    Args:
        serial(GSM): Serial Mincom Device.
        command(str | tuple[str]): attribute commands.
    """
    def wrapper(_cls: type[IGSM_COMMAND], gsm: GSM) -> str:
        command = dec_com(_cls)
        results: list[str] = []
        if command:
            if isinstance(command, (list, tuple)):
                for com in command:
                    res = gsm.send_at(com)
                    log_gsm(res)
                    results.append(res)
                return 'OK' if all(['OK' in res for res in results]) else 'ERROR'
            else:
                res = gsm.send_at(command)
                log_gsm(res)
                return 'OK' if 'OK' in res else res

        return 'OK'

    return wrapper


class IGSM_COMMAND(metaclass=ABCMeta):
    """GSM Command Base Class(Static)

    Raises:
        NotImplementedError: Command not implemented.
    """
    pre: str | tuple[str]
    post: str | tuple[str]

    @__command_decorator
    @classmethod
    def pre_command(cls: type[IGSM_COMMAND]) -> str | tuple[str]:
        """Pre Command

        Returns:
            str: 'OK' | 'ERROR'
        """
        return cls.pre

    @classmethod
    @abstractmethod
    def command(cls, gsm: GSM, *args: tuple[Any], **kwargs: dict[str, Any]) -> bool:
        """Minicom Command

        Returns:
            bool: Command Success.
        """
        raise NotImplementedError

    @__command_decorator
    @classmethod
    def post_command(cls: type[IGSM_COMMAND]) -> str | tuple[str]:
        """Post Command

        Returns:
            str: 'OK' | 'ERROR'
        """
        return cls.post


class HEALTHCHECK_GSM(IGSM_COMMAND):
    """Check Health Of GSM Device

    Returns:
        bool: Serial Device Heartbeat.
    """
    @classmethod
    def command(cls, gsm: GSM, *_args: tuple[Any], **_kwargs: dict[str, Any]) -> bool:
        res = gsm.send_at("CPSI?")

        return 'Online' in res
