from typing import Any, Dict, IO, NoReturn
import sys
import datetime

from .console import Console, _ansi_colors


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

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, int):
            return self.level > other
        elif isinstance(other, str):
            return self.level > Level._levels[other].level
        elif isinstance(other, Level):
            return self.level > other.level

        raise ValueError(f'Expected int, str or logging.Level, got {type(other)}.')

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, int):
            return self.level == other
        elif isinstance(other, str):
            return self.name == other
        elif isinstance(other, Level):
            return self.level == other.level

        raise ValueError(f'Expected int, str or logging.Level, got {type(other)}.')

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


DEBUG = Level('debug', 0, sys.stdout)
INFO = Level('info', 1, sys.stdout)
WARNING = Level('warning', 2, sys.stderr)
ERROR = Level('error', 3, sys.stderr)


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

        for color in _ansi_colors:
            delattr(self, color)

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

        if level > self._level or level == self._level:
            message = self._format.format(
                timestamp=self._timestamp(),
                name=self._name,
                level=level.name,
                message=message,
            )
            super()._print(stream, message, **kwargs)

    def log(self, level: Level, message: str, **kwargs: Any) -> NoReturn:
        self._print(level.stream, level, message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> NoReturn:
        self.log(DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> NoReturn:
        self.log(INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> NoReturn:
        self.log(WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> NoReturn:
        self.log(ERROR, message, **kwargs)


class FileLogger(Logger):

    defaults: Dict[str, Any] = dict(filename=None)

    def __init__(self, **kwargs: Any) -> NoReturn:
        pass
