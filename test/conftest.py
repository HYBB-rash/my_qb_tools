import sys
from pathlib import Path


# 将源码目录加入 sys.path，便于测试直接导入 src 下的包
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

