__version__ = '0.0.6'

from .console import Console
from .logging import Logger, FileLogger

console = Console()

__all__ = [
    'console',
    'Console',
    'Logger',
    'FileLogger',
]
