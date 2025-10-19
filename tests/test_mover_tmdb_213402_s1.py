import os
import sys
import tempfile
from pathlib import Path

# 确保可直接从 src 导入
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tools.move.implementations import factory  # noqa: E402


def test_mover_tmdb_213402_s1_links_expected_files():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        src = base / "src"
        dst = base / "dst"
        src.mkdir()
        dst.mkdir()

        cases = {
            # 中文简体
            "超常技能开启奇幻世界美食之旅.S01E01.1080p.mkv": True,
            # 中文繁体
            "超常技能開啟奇幻世界美食之旅-第02話.mkv": True,
            # 英文常见命名（含分隔符变体）
            "Campfire.Cooking.in.Another.World.with.My.Absurd.Skill.S01E03.mkv": True,
            "Campfire Cooking in Another World with My Absurd Skill - 04.mkv": True,
            # 罗马字/日文
            "Tondemo-Skill-de-Isekai-Hourou-Meshi.E05.mkv": True,
            "とんでもスキルで異世界放浪メシ 第06話.mkv": True,
            # 不应匹配：其他剧
            "别的剧.S01E01.mkv": False,
            "Campfire Recipes S01E01.mkv": False,
        }

        for name in cases:
            (src / name).write_text("x", encoding="utf-8")

        mover = factory.create("tmdb-213402-s1")
        mover(src, dst)

        linked = {p.name for p in dst.iterdir() if p.is_file()}
        expected_linked = {name for name, keep in cases.items() if keep}

        assert linked == expected_linked, (
            f"硬链接结果不符:\n实际:   {sorted(linked)}\n期望: {sorted(expected_linked)}"
        )

        for name in expected_linked:
            src_stat = os.stat(src / name)
            dst_stat = os.stat(dst / name)
            assert src_stat.st_ino == dst_stat.st_ino, (
                f"{name} 不是硬链接（inode 不一致）"
            )
