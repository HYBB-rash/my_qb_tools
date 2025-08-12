from pathlib import Path
from typing import Callable

Mover = Callable[[Path, Path], None]
