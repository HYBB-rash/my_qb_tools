from dataclasses import dataclass

from tools.move.implementations import factory

MOVE_FACTORY = factory


@dataclass(eq=False)
class MoveFunctionNotFound(Exception):
    season: int
    tmdb_id: int

    def __str__(self) -> str:
        return f"tmdb-{self.tmdb_id}-s{self.season} 没有找到函数实现"
