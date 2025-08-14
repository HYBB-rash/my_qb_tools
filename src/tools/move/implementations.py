from pathlib import Path

from share import LOGGER, Factory, find_files_by_regex
from tools.move.interfaces import Mover

factory: Factory[Mover] = Factory()


@factory.register("tmdb-243224-s1")
def mover_tmdb_243224_s1(where: Path, to: Path) -> None:
    mover = default_move(r"凡人修仙传")
    return mover(where, to)


# 253955-定风波 第一季
@factory.register("tmdb-253955-s1")
def mover_tmdb_253955_s1(where: Path, to: Path) -> None:
    mover = default_move(r"定风波")
    return mover(where, to)


# 83095-盾之勇者 第4季
@factory.register("tmdb-83095-s4")
def mover_tmdb_83095_s4(where: Path, to: Path) -> None:
    mover = default_move(r"盾之勇者")
    return mover(where, to)


# 292554-定孕成婚 第1季
@factory.register("tmdb-292554-s1")
def mover_tmdb_292554_s1(where: Path, to: Path) -> None:
    mover = default_move(r"Kon")
    return mover(where, to)


# 277513-我怎么可能成为你的恋人，不行不行！ 第1季
@factory.register("tmdb-277513-s1")
def mover_tmdb_277513_s1(where: Path, to: Path) -> None:
    # 排除所有版本号形式：v + 数字（大小写不敏感），例如 v2、v3、v10、v123 等
    # 注意：不依赖词边界，以便匹配诸如 "-06v2" 的场景
    mover = default_move(r"(?i)^(?!.*v\d+).*我怎么可能成为你的恋人")
    return mover(where, to)


# 86031-石纪元
@factory.register("tmdb-86031-s4")
def mover_tmdb_86031_s4(where: Path, to: Path) -> None:
    mover = default_move(r"Dr.STONE")
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
