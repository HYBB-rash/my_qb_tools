import os
import tempfile
from pathlib import Path

from tools.move.implementations import hardlink


def test_hardlink_creates_link():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        src_dir = tmp / "src"
        dst_dir = tmp / "dst"
        src_dir.mkdir()
        dst_dir.mkdir()

        src_file = src_dir / "sample.txt"
        src_file.write_text("hello", encoding="utf-8")

        # 调用待测函数
        hardlink(src_file, dst_dir)

        dst_file = dst_dir / src_file.name
        assert dst_file.exists(), "目标硬链接文件不存在"

        # 校验 inode（在同一文件系统下），并验证内容一致
        src_stat = os.stat(src_file)
        dst_stat = os.stat(dst_file)
        assert src_stat.st_ino == dst_stat.st_ino, "不是硬链接（inode 不一致）"
        assert dst_file.read_text(encoding="utf-8") == "hello"
