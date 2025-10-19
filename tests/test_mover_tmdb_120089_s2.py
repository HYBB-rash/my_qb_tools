import os
import sys
import tempfile
from pathlib import Path

# 确保可直接从 src 导入
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tools.move.implementations import factory  # noqa: E402


def test_mover_tmdb_120089_s2_links_expected_files():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        src = base / "src"
        dst = base / "dst"
        src.mkdir()
        dst.mkdir()

        cases = {
            # 中文常见命名
            "间谍过家家.S02E01.1080p.mkv": True,
            "間諜過家家 第二季 02.mkv": True,
            # 英文常见命名（含 x/× 与 Season 表达）
            "Spy.x.Family.S02E03.mkv": True,
            "SPY×FAMILY - Season 2 Episode 04.mkv": True,
            "SPY_X_FAMILY.2nd.Season.E05.mkv": True,
            # 日文常见命名
            "スパイファミリー 第2期 第06話.mkv": True,
            # 不应匹配：其他季/剧场版等
            "Spy x Family - S03E01.mkv": False,
            "SPY×FAMILY CODE White.mkv": False,
            "别的剧.S02E01.mkv": False,
        }

        for name in cases:
            (src / name).write_text("x", encoding="utf-8")

        mover = factory.create("tmdb-120089-s2")
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
