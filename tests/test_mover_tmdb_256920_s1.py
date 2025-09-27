import os
import sys
import tempfile
from pathlib import Path

# 确保可直接从 src 导入
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tools.move.implementations import factory  # noqa: E402


def test_mover_tmdb_256920_s1_links_expected_files():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        src = base / "src"
        dst = base / "dst"
        src.mkdir()
        dst.mkdir()

        cases = {
            # 中文（简体）
            "许我耀眼.S01E01.1080p.mkv": True,
            # 中文（繁体）+ 分隔符
            "許_我-耀_眼.EP02.mkv": True,
            # 大乔小乔 别名（简繁 + 分隔符）
            "大乔-小乔.S01E03.mkv": True,
            "大喬小喬.EP04.mkv": True,
            # 拼音命名
            "Da.Qiao.Xiao.Qiao.S01E05.mkv": True,
            "Xu_Wo_Yao_Yan.S01E06.mkv": True,
            # 英文别名
            "Let-Me-Shine.S01E07.mkv": True,
            "Love's.Ambition.S01E08.mkv": True,
            # 其他剧名：不应匹配
            "让我耀眼.S01E01.mkv": False,
            "Let_Me_Sleep.S01E09.mkv": False,
        }

        for name in cases:
            (src / name).write_text("x", encoding="utf-8")

        mover = factory.create("tmdb-256920-s1")
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
