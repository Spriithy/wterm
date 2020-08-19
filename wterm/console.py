from typing import Any, Dict, IO, List, NoReturn, Tuple, Union
from functools import partialmethod
import sys
import re

_ansi_re: re.Pattern = re.compile(r"\033\[[;?0-9]*[a-zA-Z]")

_ansi_colors: Dict[str, int] = dict(
    black=30,
    red=31,
    green=32,
    yellow=33,
    blue=34,
    magenta=35,
    cyan=36,
    white=37,
    reset=39,
    bright_black=90,
    bright_red=91,
    bright_green=92,
    bright_yellow=93,
    bright_blue=94,
    bright_magenta=95,
    bright_cyan=96,
    bright_white=97,
)

_ansi_reset_all: str = '\033[0m'


def _interpret_color(color: Union[int, Tuple, List], offset: int = 0) -> str:
    if isinstance(color, int):
        return f'{38 + offset};5;{color:d}'

    if isinstance(color, (tuple, list)):
        r, g, b = color
        return f'{38 + offset};2;{r:d};{g:d};{b:d}'

    return str(_ansi_colors[color] + offset)


_style_keys: List[str] = ['bg', 'fg', 'bold', 'dim', 'underline', 'blink', 'reverse', 'reset']


class Console:

    defaults: Dict[str, Any] = dict(
        stdout=sys.stdout,
        stderr=sys.stderr,
        tty=True,
        notty=True,
        prefix=None,
        colors_enabled=True,
        endl='\n',
        debug_prefix=None,
        info_prefix=None,
        warning_prefix='[warning] ',
        error_prefix='[error] ',
    )

    def __init__(self, **kwargs: Any) -> NoReturn:
        for (attr, value) in Console.defaults.items():
            setattr(self, f'_{attr}', value)

        self.configure(**kwargs)

    def restore_defaults(self) -> NoReturn:
        self.configure(**Console.defaults)

    def configure(self, **kwargs: Any) -> NoReturn:
        for attr in Console.defaults:
            if attr in kwargs:
                setattr(self, f'_{attr}', kwargs.pop(attr))

    def _print(self, stream: IO, message: str, **kwargs: Any) -> NoReturn:
        if None in (stream, message):
            return

        stream_tty = stream.isatty()
        print_tty = kwargs.pop('tty', True) if self._tty else kwargs.pop('tty', False)
        print_notty = kwargs.pop('notty', True) if self._notty else kwargs.pop('notty', False)

        if (stream_tty and print_tty) or (not stream_tty and print_notty):
            prefix = None

            if kwargs.pop('prefix', self._prefix):
                if callable(self._prefix):
                    prefix = self._prefix()
                elif self._prefix:
                    prefix = str(self._prefix)

            message = f'{prefix} {message}' if prefix else message

            if not stream.isatty() or not kwargs.pop('colors_enabled', self._colors_enabled):
                message = self.strip_style(message)
            else:
                style_args = {k: v for (k, v) in kwargs.items() if k in _style_keys}
                if len(style_args) > 0:
                    message = self.style(message, **style_args)

            stream.write(message)
            endl = kwargs.pop('endl', self._endl)
            stream.write(endl)

    def log(self, message: str, **kwargs: Any) -> NoReturn:
        self._print(self._stdout, message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> NoReturn:
        message = f'{self._debug_prefix}{message}' if self._debug_prefix else message
        self._print(self._stdout, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> NoReturn:
        message = f'{self._info_prefix}{message}' if self._info_prefix else message
        self._print(self._stdout, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> NoReturn:
        message = f'{self._warning_prefix} {message}' if self._warning_prefix else message
        self._print(self._stderr, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> NoReturn:
        message = f'{self._error_prefix} {message}' if self._error_prefix else message
        self._print(self._stderr, message, **kwargs)

    def strip_style(self, message: str) -> str:
        return _ansi_re.sub('', message)

    def style(
        self,
        message: str,
        fg: str = None,
        bg: str = None,
        bold: bool = None,
        dim: bool = None,
        underline: bool = None,
        blink: bool = None,
        reverse: bool = None,
        reset: bool = True,
    ) -> str:
        if not isinstance(message, str):
            message = str(message)

        bits = []

        if fg:
            try:
                bits.append(f'\033[{_interpret_color(fg)}m')
            except KeyError:
                raise TypeError(f'Unknown color {fg!r}')

        if bg:
            try:
                bits.append(f'\033[{_interpret_color(bg, 10)}m')
            except KeyError:
                raise TypeError(f'Unknown color {bg!r}')

        if bold is not None:
            bits.append(f'\033[{1 if bold else 22}m')

        if dim is not None:
            bits.append(f'\033[{2 if dim else 22}m')

        if underline is not None:
            bits.append(f'\033[{4 if underline else 24}m')

        if blink is not None:
            bits.append(f'\033[{5 if blink else 25}m')

        if reverse is not None:
            bits.append(f'\033[{7 if reverse else 27}m')

        bits.append(message)
        if reset:
            bits.append(_ansi_reset_all)

        return ''.join(bits)


def _init_console() -> NoReturn:
    if hasattr(Console, '_init'):
        return

    for color in _ansi_colors:
        setattr(Console, color, partialmethod(Console.style, fg=color))

    setattr(Console, '_init', True)


_init_console()
