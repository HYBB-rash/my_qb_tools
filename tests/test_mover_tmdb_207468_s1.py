import os
import sys
import tempfile
from pathlib import Path

# 确保可直接从 src 导入
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tools.move.implementations import factory  # noqa: E402


def test_mover_tmdb_207468_s1_links_expected_files():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        src = base / "src"
        dst = base / "dst"
        src.mkdir()
        dst.mkdir()

        cases = {
            # 中文（简体，阿拉伯数字）
            "怪兽8号.S01E01.1080p.mkv": True,
            # 繁体（阿拉伯数字）
            "怪獸8號.S01E02.1080p.mkv": True,
            # 中文（简体，汉字数字）
            "怪兽八号 - S01E03.mkv": True,
            # 日文
            "怪獣8号.S01E04.mkv": True,
            # 英文（No. 带点）
            "Kaiju No. 8 - S01E05.mkv": True,
            # 英文（No 无点，连接符分隔）
            "Kaiju-No-8.S01E06.mkv": True,
            # 非本剧
            "别的剧.S01E01.mkv": False,
        }

        for name, _ in cases.items():
            (src / name).write_text("x", encoding="utf-8")

        mover = factory.create("tmdb-207468-s1")
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

