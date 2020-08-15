from typing import Any, Dict, IO, Tuple, List, NoReturn
from .console import Console


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


DEBUG = Level('debug', 0)
INFO = Level('info', 1)
WARNING = Level('warning', 2)
ERROR = Level('error', 3)


class Logger(Console):

    defaults: Dict[str, Any] = dict(
        format='{timestamp} {name} {level} - {message}',
        level=INFO,
    )

    def __init__(self, name: str, **kwargs: Any) -> NoReturn:
        super(Logger, self).__init__(**kwargs)
        self._name = name
