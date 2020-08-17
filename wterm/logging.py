from typing import Any, Dict, IO, Tuple, NoReturn
import datetime

from .console import Console, _ansi_colors


class Level:

    _levels: Dict[str, Any] = dict()

    def __init__(self, name: str, level: int) -> NoReturn:
        self.name = name
        self.level = level
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

    def debug(self, message: str, **kwargs: Any) -> NoReturn:
        self._print(self._stdout, DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> NoReturn:
        self._print(self._stdout, INFO, message, **kwargs)

    # log is an alias for info, to allow for easy console.log(...)
    log = info

    def warning(self, message: str, **kwargs: Any) -> NoReturn:
        self._print(self._stderr, WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> NoReturn:
        self._print(self._stderr, ERROR, message, **kwargs)


class FileLogger(Logger):

    defaults: Dict[str, Any] = dict(filename=None)

    def __init__(self, **kwargs: Any) -> NoReturn:
        pass
