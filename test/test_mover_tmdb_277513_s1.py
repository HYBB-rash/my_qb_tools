import os

# 将源码目录加入 sys.path，便于测试直接导入 src 下的包
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tools.move.implementations import factory  # noqa: E402


def test_mover_tmdb_277513_s1_excludes_v2_and_includes_v20():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        src = base / "src"
        dst = base / "dst"
        src.mkdir()
        dst.mkdir()

        # 准备源文件
        cases = {
            # 应当被硬链接
            "我怎么可能成为你的恋人.S01E01.1080p.mkv": True,
            # 包含 v2，应被排除
            "我怎么可能成为你的恋人.S01E02.v2.1080p.mkv": False,
            # 任何 v+数字 都应排除（包括 v20 等）
            "我怎么可能成为你的恋人.S01E03.v20.1080p.mkv": False,
            # 用分隔符包围 v2，同样应被排除（满足 \bv2\b）
            "我怎么可能成为你的恋人.S01E04.(v2).mkv": False,
            # v3/v4/v5 也应当被排除
            "我怎么可能成为你的恋人.S01E05.v3.mkv": False,
            "我怎么可能成为你的恋人.S01E06.v4-Remux.mkv": False,
            "我怎么可能成为你的恋人.S01E07.v5.mkv": False,
            # v30 也应排除（v+数字 的一例）
            "我怎么可能成为你的恋人.S01E08.v30.mkv": False,
            # 大小写不敏感：V12 也应排除
            "我怎么可能成为你的恋人.S01E09.V12.mkv": False,
            # 其他剧名不应匹配
            "别的剧.S01E01.mkv": False,
            # 当时错误发生的剧名
            "[Prejudice-Studio] 我怎么可能成为你的恋人，不行不行！(※不是不可能！？) Watashi ga Koibito ni Nareru Wake Nai jan - 06v2 [WebRip 1080P HEVC 8bit AAC MKV][简繁内封].mkv": False,
            # 同类错误：06v3 也应排除
            "[Prejudice-Studio] 我怎么可能成为你的恋人，不行不行！(※不是不可能！？) Watashi ga Koibito ni Nareru Wake Nai jan - 06v3 [WebRip 1080P HEVC 8bit AAC MKV][简繁内封].mkv": False,
        }

        for name, _ in cases.items():
            (src / name).write_text("x", encoding="utf-8")

        # 获取并执行 mover
        mover = factory.create("tmdb-277513-s1")
        mover(src, dst)

        linked = {p.name for p in dst.iterdir() if p.is_file()}

        expected_linked = {name for name, keep in cases.items() if keep}
        assert linked == expected_linked, (
            f"硬链接结果不符:\n实际:   {sorted(linked)}\n期望: {sorted(expected_linked)}"
        )

        # 进一步校验：被链接的文件与源文件 inode 相同（同一文件系统）
        for name in expected_linked:
            src_stat = os.stat(src / name)
            dst_stat = os.stat(dst / name)
            assert src_stat.st_ino == dst_stat.st_ino, (
                f"{name} 不是硬链接（inode 不一致）"
            )
