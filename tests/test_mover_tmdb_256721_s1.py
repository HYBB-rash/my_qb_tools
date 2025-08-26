import os
import sys
import tempfile
from pathlib import Path

# 确保可直接从 src 导入
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tools.move.implementations import factory  # noqa: E402


def test_mover_tmdb_256721_s1_links_expected_files():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        src = base / "src"
        dst = base / "dst"
        src.mkdir()
        dst.mkdir()

        cases = {
            # 中文主名（常见）
            "咔嗒咔嗒.S01E01.1080p.mkv": True,
            # 变体：哒/嗒 + 分隔符
            "咔哒-咔哒.S01E02.mkv": True,
            # 混合分隔符
            "咔嗒_咔嗒.S01E03.mkv": True,
            # 不应匹配：仅一个“咔嗒”
            "咔嗒.S01E01.mkv": False,
            # 其他剧名
            "别的剧.S01E01.mkv": False,
        }

        for name, _ in cases.items():
            (src / name).write_text("x", encoding="utf-8")

        mover = factory.create("tmdb-256721-s1")
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

