from typing import Any, Dict, IO, NoReturn, Union
import os
import io
import sys
import datetime

from .console import Console


class Level:

    _levels: Dict[str, Any] = dict()

    def __init__(self, name: str, level: int, stream: IO = sys.stdout) -> NoReturn:
        self.name = name
        self.level = level
        self.stream = stream
        Level._levels[name] = self

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, int):
            return self.level < other
        elif isinstance(other, str):
            return self.level < Level._levels[other].level
        elif isinstance(other, Level):
            return self.level < other.level

        raise ValueError(f'Expected int, str or logging.Level, got {type(other)}.')

    def __le__(self, other: Any) -> bool:
        return self < other or self == other

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, int):
            return self.level > other
        elif isinstance(other, str):
            return self.level > Level._levels[other].level
        elif isinstance(other, Level):
            return self.level > other.level

        raise ValueError(f'Expected int, str or logging.Level, got {type(other)}.')

    def __ge__(self, other: Any) -> bool:
        return self > other or self == other

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, int):
            return self.level == other
        elif isinstance(other, str):
            return self.name == other
        elif isinstance(other, Level):
            return self.level == other.level

        raise ValueError(f'Expected int, str or logging.Level, got {type(other)}.')

    def __hash__(self) -> int:
        return hash((self.name, self.level))

    def __str__(self) -> str:
        return f'<Level name={self.name}({self.level})>'


DEBUG = Level('debug', 0)
INFO = Level('info', 1)
WARNING = Level('warning', 2)
ERROR = Level('error', 3)


class Logger(Console):

    defaults: Dict[str, Any] = dict(
        format='{timestamp} {name} [{level}] {message}',
        level=INFO,
        name='root',
        colors_enabled=False,
    )

    def __init__(self, **kwargs: Any) -> NoReturn:
        self.configure(**Logger.defaults)
        super().__init__(**kwargs)
        self.configure(**kwargs)

        self.levels: Dict[Level, IO] = {
            DEBUG: self._stdout,
            INFO: self._stdout,
            WARNING: self._stderr,
            ERROR: self._stderr,
        }

    def restore_defaults(self) -> NoReturn:
        super().restore_defaults()
        self.configure(**Logger.defaults)

    def configure(self, **kwargs: Any) -> NoReturn:
        # Do not allow users to customise console prefix for Logger instances.
        # This prevents messing up the Logger.format output which users expect.
        kwargs.pop('prefix', None)

        for attr in Logger.defaults:
            if attr in kwargs:
                setattr(self, f'_{attr}', kwargs.pop(attr))

        super().configure(**kwargs)

    def _timestamp(self) -> str:
        return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    def _print(self, stream: IO, level: Level, message: str, **kwargs: Any) -> NoReturn:
        if not self._level:
            return

        if level >= self._level:
            message = self._format.format(
                timestamp=self._timestamp(),
                name=self._name,
                level=level.name,
                message=message,
            )
            super()._print(stream, message, **kwargs)

    def log(self, level: Level, message: str, **kwargs: Any) -> NoReturn:
        self._print(self.levels[level], level, message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> NoReturn:
        self.log(DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> NoReturn:
        self.log(INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> NoReturn:
        self.log(WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> NoReturn:
        self.log(ERROR, message, **kwargs)


class FileLogger(Logger):

    def __init__(self,
                 filename: str = None,
                 out: IO = None,
                 err: IO = None,
                 tee: Union[bool, IO] = None,
                 tee_out: Union[bool, IO] = None,
                 tee_err: Union[bool, IO] = None,
                 **kwargs: Any) -> NoReturn:
        super().__init__(**kwargs)
        self._filename = filename
        self._stdout = out
        self._stderr = err
        self._teeout = None
        self._teeerr = None

        if isinstance(tee_out, bool):
            self._teeout = sys.stdout if tee_out else None
        elif isinstance(tee_out, io.TextIOBase):
            self._teeout = tee_out

        if isinstance(tee_err, bool):
            self._teeerr = sys.stderr if tee_err else None
            print('salut')
        elif isinstance(tee_err, io.TextIOBase):
            self._teeerr = tee_err

        if isinstance(tee, bool):
            self._teeout = sys.stdout if tee else None
            self._teeerr = sys.stderr if tee else None
        elif isinstance(tee, io.TextIOBase):
            self._teeout = tee
            self._teeerr = tee
            print('salut2')

        if filename:
            path = os.path.abspath(filename)
            log_dir = os.path.dirname(path)
            log_file = os.path.basename(path)
            os.makedirs(log_dir, exist_ok=True)
            self._stdout = open(log_file, 'a+')
            self._stderr = self._stdout

        if out and not err:
            self._stdout = out
            self._stderr = out

        if err:
            self._stderr = err

        self.levels: Dict[Level, IO] = {
            DEBUG: self._stdout,
            INFO: self._stdout,
            WARNING: self._stderr,
            ERROR: self._stderr,
        }

    def _print(self, stream: IO, level: Level, message: str, **kwargs: Any) -> NoReturn:
        if not self._level:
            return

        if level > self._level or level == self._level:
            super()._print(stream, level, message, **kwargs)

            tee = self._teeout if level <= INFO else self._teeerr
            if tee:
                super()._print(tee, level, message, **kwargs)
