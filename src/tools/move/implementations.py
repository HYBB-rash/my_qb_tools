from pathlib import Path

from tools.move.interfaces import Mover
from tools.share import LOGGER, Factory, find_files_by_regex

factory: Factory[Mover] = Factory()


# 79166-碧蓝之海 第2季
@factory.register("tmdb-79166-s2")
def mover_tmdb_79166_s2(where: Path, to: Path) -> None:
    # 常见别名：中文简繁/英文/日文
    # CN: 碧蓝之海 / 碧藍之海
    # EN: Grand Blue / Grand Blue Dreaming（常见做种命名，如 Grand.Blue）
    # JP: ぐらんぶる（拓展匹配）
    sep = r"[\s._-]*"
    pattern = rf"(?i)(碧[蓝藍]之海|Grand{sep}Blue(?:{sep}Dreaming)?|ぐらんぶる)"
    mover = default_move(pattern)
    return mover(where, to)


# 254476-献鱼 第1季
@factory.register("tmdb-254476-s1")
def mover_tmdb_254476_s1(where: Path, to: Path) -> None:
    # 兼容简繁体：献鱼 / 獻魚
    mover = default_move(r"(?i)[献獻][鱼魚]")
    return mover(where, to)


# 278870-你的降临 第1季
@factory.register("tmdb-278870-s1")
def mover_tmdb_278870_s1(where: Path, to: Path) -> None:
    # 常见别名：中文简繁/英文
    # CN: 你的降临 / 你的降臨（兼容常见分隔符）
    # EN: Hell Upon Me（常见做种命名，如 Hell.Upon.Me）
    sep = r"[\s._-]*"
    pattern = rf"(?i)(你的{sep}降[临臨]|Hell{sep}Upon{sep}Me)"
    mover = default_move(pattern)
    return mover(where, to)


# 240411-胆大党 第1季
@factory.register("tmdb-240411-s1")
def mover_tmdb_240411_s1(where: Path, to: Path) -> None:
    # 常见别名：中文/日文/英文
    # CN: 胆大党
    # JP: ダンダダン
    # EN: Dandadan / DAN DA DAN
    mover = default_move(r"(?i)(胆大党|ダンダダン|dan\s*da\s*dan|dandadan)")
    return mover(where, to)


# 246862-新·吊带袜天使 第1季
@factory.register("tmdb-246862-s1")
def mover_tmdb_246862_s1(where: Path, to: Path) -> None:
    # 匹配：
    # - 中文：新·吊带袜天使（兼容不同间隔符，如 · ・ ･，以及可无分隔符）
    # - 英文：Panty &/and Stocking (with Garterbelt)
    # 注意：不匹配仅有“吊带袜天使”（避免旧版混入）
    mover = default_move(
        r"(?i)(新[·･・]?\s*吊带袜天使|Panty\s*(?:&|and)\s*Stocking(?:\s*with\s*Garterbelt)?)"
    )
    return mover(where, to)


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


# 244808-拔作岛
@factory.register("tmdb-244808-s1")
def mover_tmdb_244808_s1(where: Path, to: Path) -> None:
    mover = default_move(r"青蓝岛")
    return mover(where, to)


# 281058-沉默·魔女 第1季
@factory.register("tmdb-281058-s1")
def mover_tmdb_281058_s1(where: Path, to: Path) -> None:
    # 常见别名：中文/英文
    # CN: 沉默·魔女 / 沉默魔女 / 沉默魔女的秘密（兼容不同间隔符：· ・ ･，以及可无分隔符）
    # EN: Silent Witch
    sep = r"[\s._-]*"
    pattern = rf"(?i)(沉默[·･・]?\s*魔女|沉默魔女的秘密|Silent{sep}Witch)"
    mover = default_move(pattern)
    return mover(where, to)


# 137065-明日方舟
@factory.register("tmdb-137065-s3")
def mover_tmdb_137065_s3(where: Path, to: Path) -> None:
    mover = default_move(r"Arknights_ Rise from Ember")
    return mover(where, to)


# 123249-更衣人偶坠入爱河 第1季
@factory.register("tmdb-123249-s1")
def mover_tmdb_123249_s1(where: Path, to: Path) -> None:
    # 常见别名：日文/英文/中文
    # Sono Bisque Doll wa Koi wo Suru / My Dress-Up Darling / 更衣人偶坠入爱河
    mover = default_move(r"(戀上換裝娃娃|更衣人偶|Bisque Doll|Dress[\- ]?Up Darling)")
    return mover(where, to)


# 213830-转生为第七王子，随心所欲的魔法学习之路 第1季
@factory.register("tmdb-213830-s1")
def mover_tmdb_213830_s1(where: Path, to: Path) -> None:
    # 默认规则：匹配中文简称/关键词及常见英文别名
    # CN: 转生为第七王子 / 第七王子
    # EN: 7th Prince / Seventh Prince
    mover = default_move(r"(转生为第七王子|第七王子|7th\s*Prince|Seventh\s*Prince)")
    return mover(where, to)


# 82739-青春猪头少年不会梦到兔女郎学姐 第1季
@factory.register("tmdb-82739-s1")
def mover_tmdb_82739_s1(where: Path, to: Path) -> None:
    # 常见别名：
    # CN: 青春猪头少年 / 兔女郎学姐 / 青豚
    # EN: Rascal Does Not Dream (of Bunny Girl Senpai) / Bunny Girl Senpai
    # Romaji: Seishun Buta Yarou
    mover = default_move(
        r"(青春豬頭少年|青春猪头少年|兔女郎学姐|青豚|Bunny\s*Girl\s*Senpai|Rascal\s*Does\s*Not\s*Dream|Seishun\s*Buta\s*Yarou)"
    )
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


# 278196-光死去的夏天 第1季
@factory.register("tmdb-278196-s1")
def mover_tmdb_278196_s1(where: Path, to: Path) -> None:
    # 常见别名：中文/日文/英文/罗马字
    # CN: 光死去的夏天 / 光死去的夏日（兼容“夏天/夏日”）
    # JP: 光が死んだ夏
    # EN: The Summer Hikaru Died
    # Romaji: Hikari/Hikaru ga Shinda Natsu
    # 允许单词之间出现空格/点/下划线/连字符
    sep = r"[\s._-]*"
    pattern = (
        rf"(?i)(光が死んだ夏|光死去的夏[天日]|"
        rf"The{sep}Summer{sep}Hikaru{sep}Died|"
        rf"Hikari{sep}ga{sep}Shinda{sep}Natsu|"
        rf"Hikaru{sep}ga{sep}Shinda{sep}Natsu)"
    )
    mover = default_move(pattern)
    return mover(where, to)


# 272118-小城日常 第1季
@factory.register("tmdb-272118-s1")
def mover_tmdb_272118_s1(where: Path, to: Path) -> None:
    # 常见命名：中文原名
    mover = default_move(r"小城日常")
    return mover(where, to)
