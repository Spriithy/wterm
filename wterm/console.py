import sys
from typing import Any, IO, NoReturn


class Console:

    def __init__(self, stdout: IO = sys.stdout, stderr: IO = sys.stderr, **kwargs: Any) -> NoReturn:
        self._stdout = stdout
        self._stderr = stderr
        self._tty = kwargs.pop('tty', True)
        self._notty = kwargs.pop('notty', True)
        self._colors_enabled = kwargs.pop('colors_enabled', True)

    def _print(self, stream: IO, message: str, **kwargs: Any) -> NoReturn:
        if message is None:
            return

        stream_tty = stream.isatty()
        print_tty = self._tty and kwargs.pop('tty', True)
        print_notty = self._notty and kwargs.pop('notty', True)

        if (stream_tty and print_tty) or (not stream_tty and print_notty):
            stream.write(message)
            stream.write('\n')

    def debug(self, message: str, **kwargs) -> NoReturn:
        self._print(self._stdout, message, **kwargs)

    def info(self, message: str, **kwargs) -> NoReturn:
        self._print(self._stdout, message, **kwargs)

    def warning(self, message: str, **kwargs) -> NoReturn:
        self._print(self._stderr, f'warning: {message}', **kwargs)

    def error(self, message: str, **kwargs) -> NoReturn:
        self._print(self._stderr, f'error: {message}', **kwargs)
