from pathlib import Path

from share import LOGGER, Factory, find_files_by_regex
from tools.move.interfaces import Mover

factory: Factory[Mover] = Factory()


@factory.register("tmdb-243224-s1")
def mover_tmdb_243224_s1(where: Path, to: Path) -> None:
    mover = default_move(r"凡人修仙传")
    return mover(where, to)


def default_move(regex) -> Mover:
    def move(where: Path, to: Path):
        LOGGER.info(f"从: {where}")
        LOGGER.info(f"硬链接到: {to}")

        if where.is_file():
            hardlink(where, to)
            return

        hard_link_list = find_files_by_regex(where, regex)

        for _, path in enumerate(hard_link_list):
            hardlink(path, to)

    return move


def hardlink(where: Path, to: Path) -> None:
    to.joinpath(where.name).hardlink_to(where)


# C:\Users\Herman\AppData\Local\Programs\tinyMediaManagerV5\tinyMediaManagerCMD.exe
