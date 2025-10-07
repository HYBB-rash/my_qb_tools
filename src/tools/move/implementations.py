from pathlib import Path

from tools.move.interfaces import Mover
from tools.share import LOGGER, Factory, find_files_by_regex

factory: Factory[Mover] = Factory()


# 280100-垂涎 第1季
@factory.register("tmdb-280100-s1")
def mover_tmdb_280100_s1(where: Path, to: Path) -> None:
    # 常见命名：中文原名（垂涎）以及别名 ABO
    # 为避免误匹配“垂涎欲滴”等更长词组：
    # - 对“垂涎”要求后接分隔符/结尾（如 空格/点/下划线/连字符/括号/方括号）
    # - ABO 作为独立词匹配（大小写不敏感）
    mover = default_move(r"(?i)(垂涎(?=[\s._\-\[\(]|$)|\bABO\b)")
    return mover(where, to)


# 280110-正义使者 - 我的英雄学院之非法英雄 第1季
@factory.register("tmdb-280110-s1")
def mover_tmdb_280110_s1(where: Path, to: Path) -> None:
    # 常见别名：中文简繁/英文/日文
    # CN: 正义使者 / 正義使者；我的英雄学院之非法英雄 / 我的英雄學院之非法英雄（兼容“之”可选与分隔符）
    # EN: My Hero Academia: Vigilantes / My Hero Academia Illegals（允许分隔符/冒号变体）
    # JP: ヴィジランテ（含）/ 僕のヒーローアカデミア ILLEGALS
    sep = r"[\s._-]*"
    pattern = rf"(?i)(正[义義]使者|我的英雄[学學]院(?:之)?{sep}非法英雄|My{sep}Hero{sep}Academia(?:{sep}:?{sep})?(?:Vigilantes|Illegals)|Vigilantes{sep}My{sep}Hero{sep}Academia|僕のヒーローアカデミア{sep}ILLEGALS|ヴィジランテ)"
    mover = default_move(pattern)
    return mover(where, to)


# 65930-我的英雄学院 第1季
@factory.register("tmdb-65930-s1")
def mover_tmdb_65930_s1(where: Path, to: Path) -> None:
    # 常见别名：中文简繁/英文/罗马字/日文
    # CN: 我的英雄学院 / 我的英雄學院
    # EN: My Hero Academia（排除 Vigilantes/Illegals 等衍生词）
    # Romaji: Boku no Hero Academia
    # JP: 僕のヒーローアカデミア
    sep = r"[\s._-]*"
    pattern = (
        rf"(?i)("
        rf"My{sep}Hero{sep}Academia(?!{sep}(?:Vigilantes|Illegals))|"
        rf"Boku{sep}no{sep}Hero{sep}Academia|"
        rf"我的英雄[学學]院|"
        rf"僕のヒーローアカデミア"
        rf")"
    )
    mover = default_move(pattern)
    return mover(where, to)


# 271649-琉璃的宝石 第1季
@factory.register("tmdb-271649-s1")
def mover_tmdb_271649_s1(where: Path, to: Path) -> None:
    # 常见别名：中文简繁/日文/英文
    # CN: 琉璃的宝石 / 琉璃的寶石（允许常见分隔符）
    # JP: 瑠璃の宝石 / 瑠璃ノ宝石
    # EN: Ruri no Houseki / Ruri's Jewels
    sep = r"[\s._\-']*"
    pattern = (
        rf"(?i)("
        rf"琉璃的{sep}[宝寶]{sep}石|"
        rf"瑠璃[のノ]{sep}宝石|"
        rf"Ruri{sep}no{sep}Houseki|"
        rf"Ruri{sep}'?s{sep}Jewels?"
        rf")"
    )
    mover = default_move(pattern)
    return mover(where, to)


# 272059-凸变英雄X 第1季
@factory.register("tmdb-272059-s1")
def mover_tmdb_272059_s1(where: Path, to: Path) -> None:
    # 常见别名：中文简繁 + 可选分隔符与空格
    # CN: 凸变英雄X / 凸變英雄X / 凸变英雄 X / 凸變英雄-X 等
    sep = r"[\s._-]*"
    pattern = rf"(?i)凸[变變]英雄{sep}X"
    mover = default_move(pattern)
    return mover(where, to)


# 207468-怪兽8号 第1季
@factory.register("tmdb-207468-s1")
def mover_tmdb_207468_s1(where: Path, to: Path) -> None:
    # 常见别名：中文简繁/日文/英文
    # CN: 怪兽8号 / 怪獸8號 / 怪兽八号（数字/汉字“八”均可；号/號 兼容）
    # JP: 怪獣8号
    # EN: Kaiju No. 8（允许 No 后有无点、分隔符变体）
    sep = r"[\s._-]*"
    pattern = rf"(?i)(怪[兽獸獣][8八][号號]|Kaiju{sep}No\.?{sep}8)"
    mover = default_move(pattern)
    return mover(where, to)


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


# 256721-咔嗒咔嗒 第1季
@factory.register("tmdb-256721-s1")
def mover_tmdb_256721_s1(where: Path, to: Path) -> None:
    # 兼容：
    # - 中文：咔嗒咔嗒 / 咔哒咔哒（允许中间出现空格/点/下划线/连字符）
    # - 英文：Gachiakuta / Gachi Akuta（允许空格/点/下划线/连字符分隔）
    sep = r"[\s._-]*"
    pattern = rf"(?i)(咔[嗒哒]{sep}咔[嗒哒]|Gachi{sep}akuta)"
    mover = default_move(pattern)
    return mover(where, to)


# 256920-许我耀眼 第1季
@factory.register("tmdb-256920-s1")
def mover_tmdb_256920_s1(where: Path, to: Path) -> None:
    # 常见别名：中文简繁/大乔小乔/拼音/英文
    # CN: 许我耀眼 / 許我耀眼；大乔小乔 / 大喬小喬（允许常见分隔符）
    # Pinyin: Xu Wo Yao Yan / Da Qiao Xiao Qiao
    # EN: Let Me Shine / Love's Ambition
    sep = r"[\s._-]*"
    pattern = (
        rf"(?i)("
        rf"许{sep}我{sep}耀{sep}眼|"
        rf"許{sep}我{sep}耀{sep}眼|"
        rf"大{sep}[乔喬]{sep}小{sep}[乔喬]|"
        rf"Xu{sep}Wo{sep}Yao{sep}Yan|"
        rf"Da{sep}Qiao{sep}Xiao{sep}Qiao|"
        rf"Let{sep}Me{sep}Shine|"
        rf"Love'?s{sep}Ambition"
        rf")"
    )
    mover = default_move(pattern)
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


@factory.register("tmdb-280945-s1")
def mover_tmdb_280945_s1(where: Path, to: Path) -> None:
    # 暴君的厨师 第1季
    # 兼容：简繁体 + 常见分隔符（空格/点/下划线/连字符）
    sep = r"[\s._-]*"
    # 英文别名：Bon.Appetit.Your.Majesty（允许分隔符变体）
    mover = default_move(rf"(?i)(暴君的{sep}[厨廚]{sep}[师師]|Bon{sep}Appetit{sep}Your{sep}Majesty)")
    return mover(where, to)


@factory.register("tmdb-243224-s1")
def mover_tmdb_243224_s1(where: Path, to: Path) -> None:
    mover = default_move(r"凡人修仙传")
    return mover(where, to)


# 253093-与晋长安 第1季
@factory.register("tmdb-253093-s1")
def mover_tmdb_253093_s1(where: Path, to: Path) -> None:
    # 兼容简繁体：与晋长安 / 與晉長安
    mover = default_move(r"(?i)[与與][晋晉][长長]安")
    return mover(where, to)


# 106449-凡人修仙传 第1季
@factory.register("tmdb-106449-s1")
def mover_tmdb_106449_s1(where: Path, to: Path) -> None:
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


# 82739-青春猪头少年不会梦到兔女郎学姐 第2季
@factory.register("tmdb-82739-s2")
def mover_tmdb_82739_s2(where: Path, to: Path) -> None:
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
