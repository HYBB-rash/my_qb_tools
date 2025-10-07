import os
import sys
import tempfile
from pathlib import Path

# 确保可直接从 src 导入
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tools.move.implementations import factory  # noqa: E402


def test_mover_tmdb_65930_s2_links_expected_files():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        src = base / "src"
        dst = base / "dst"
        src.mkdir()
        dst.mkdir()

        cases = {
            # 中文常见命名
            "我的英雄学院.S02E01.1080p.mkv": True,
            "我的英雄學院 第二季 02.mkv": True,
            # 英文常见命名（含不同季节写法）
            "My Hero Academia - S02E03.mkv": True,
            "My.Hero.Academia.Season.2.E04.2160p.mkv": True,
            # 罗马字与 2nd Season 命名
            "Boku-no-Hero-Academia.2nd.Season.-05.mkv": True,
            # 日文常见命名
            "僕のヒーローアカデミア 第ニ期 第06話.mkv": True,
            # 季度标记在前
            "S02E07 - 僕のヒーローアカデミア.mkv": True,
            # 不应匹配：其他季度/衍生作品/其他剧
            "My Hero Academia - S01E01.mkv": False,
            "My Hero Academia Season 3 Episode 01.mkv": False,
            "My Hero Academia Vigilantes - S02E01.mkv": False,
            "别的剧.S02E01.mkv": False,
        }

        for name in cases:
            (src / name).write_text("x", encoding="utf-8")

        mover = factory.create("tmdb-65930-s2")
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
