from __future__ import annotations

import logging
import logging.config
import logging.handlers
import os
import re
import sqlite3
import sys
import time
from pathlib import Path
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Iterator,
    Optional,
    Pattern,
    Sequence,
    TypeVar,
    Union,
)

from dotenv import load_dotenv

from tools.share.tg_bot import TelegramHandler

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "infofmt": {
#             "format": "[%(levelname)s]-[%(asctime)s]-[%(name)s=>%(funcName)s, %(filename)s:%(lineno)d]: %(message)s",
#             "datefmt": "%Y-%m-%d %H:%M:%S",
#         },
#     },
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#             "formatter": "infofmt",
#             "level": "DEBUG",
#         },
#     },
#     "root": {  # 或者指定某个 logger：'loggers': {'your.module': {...}}
#         "level": "DEBUG",
#         "handlers": ["console"],
#     },
# }

# logging.config.dictConfig(LOGGING)


def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # 你之前要的格式：等级 + 时间 + 模块>函数 @ 文件:行 + 消息
    fmt = "[%(levelname)s]-[%(asctime)s]-[%(name)s=>%(funcName)s, %(filename)s:%(lineno)d]: %(message)s"
    formatter = logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")

    # 控制台
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    root.addHandler(ch)

    # 文件日志（默认写入项目根下 log/app.log；也支持通过环境变量指定文件路径）
    try:
        env_log_file = os.getenv("MY_QB_TOOLS_LOG_FILE")
        if env_log_file and env_log_file.strip():
            log_path = Path(env_log_file).expanduser()
            log_dir = log_path.parent
        else:
            project_root = Path(__file__).resolve().parents[2]
            log_dir = project_root / "log"
            log_path = log_dir / "app.log"
        log_dir.mkdir(parents=True, exist_ok=True)
        fh = logging.handlers.RotatingFileHandler(
            filename=str(log_path),
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding="utf-8",
        )
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        root.addHandler(fh)
    except Exception as e:
        # 文件日志失败不应阻塞主流程
        logging.getLogger(__name__).warning("文件日志初始化失败: %s", e)

    load_dotenv()
    # Telegram（从环境变量读，避免泄漏）
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        tg = TelegramHandler(token, chat_id, level=logging.INFO)
        tg.setFormatter(formatter)

        # 如果只想发“恰好 INFO”（不包括 WARNING/ERROR），取消注释下面两行
        # class OnlyInfo(logging.Filter):
        #     def filter(self, record): return record.levelno == logging.INFO
        # tg.addFilter(OnlyInfo())

        root.addHandler(tg)
    else:
        logging.getLogger(__name__).warning(
            "未设置 TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID，已禁用 TG 推送。"
        )

    # 避免 requests 自身日志回流触发推送（可选）
    logging.getLogger("requests").setLevel(logging.WARNING)

    # 捕获未处理异常到日志
    def _excepthook(exc_type, exc, tb):
        logging.getLogger(__name__).exception(
            "未捕获异常", exc_info=(exc_type, exc, tb)
        )

    try:
        sys.excepthook = _excepthook
    except Exception:
        pass

    return logging.getLogger(__name__)


LOGGER = setup_logging()


def sqlite_row_to_dict(cursor: sqlite3.Cursor, data: tuple[Any, ...]) -> dict[str, Any]:
    row = sqlite3.Row(cursor, data)
    return {key: row[key] for key in row.keys()}


def format_timestamp(ts: int) -> str:
    """
    Formats a timestamp into a human-readable string.
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


T = TypeVar("T", bound=Callable)
E = TypeVar("E")
Builder = Callable[..., E]  # 负责“构建实例”的可调用，比如类本身或函数


class UnknownKeyError(KeyError):
    def __init__(self, key: str, available: Iterable[str]):
        super().__init__(f"未知实现: {key!r}. 可选: {sorted(available)}")


class Factory(Generic[T]):
    def __init__(self) -> None:
        self._registry: dict[str, T] = {}
        self._default: Optional[T] = None

    def register(self, name: str):
        key = name.lower()

        def deco(b: T) -> T:
            self._registry[key] = b
            return b

        return deco

    def set_default(self, builder: T | str):
        """可传 builder 或已注册的名称"""
        if isinstance(builder, str):
            self._default = self._registry[builder.lower()]
        else:
            self._default = builder

    def create(self, name: str | None, /) -> T:
        """根据 name 构建实例；支持额外参数传给构造器"""
        if name:
            key = name.lower()
            if key in self._registry:
                return self._registry[key]
            if self._default is None:
                raise UnknownKeyError(key, self._registry.keys())
        if self._default is None:
            raise UnknownKeyError("(None)", self._registry.keys())
        return self._default

    def available(self) -> list[str]:
        return sorted(self._registry.keys())


def iter_files_by_regex(
    root: Union[str, Path],
    pattern: Union[str, Pattern[str]],
    *,
    match_on: str = "name",  # "name" | "relative" | "path"
    flags: int = 0,  # re.IGNORECASE 等
    ignore_dirs: Sequence[Union[str, Pattern[str]]] = (),
    follow_symlinks: bool = False,
    return_str: bool = False,
    normalize_posix: bool = True,  # 将路径统一为 / 便于写正则
) -> Iterator[Union[Path, str]]:
    """
    遍历 root 下所有文件，返回满足正则的文件路径（生成器）。
    - pattern: 正则字符串或已编译的 Pattern
    - match_on:
        "name"     -> 仅匹配文件名
        "relative" -> 匹配相对 root 的路径
        "path"     -> 匹配绝对路径
    - ignore_dirs: 要忽略的目录名称/正则（仅对目录名生效）
    """
    root = Path(root)

    regex = re.compile(pattern, flags) if isinstance(pattern, str) else pattern

    compiled_ignores: list[Pattern[str]] = []
    for ig in ignore_dirs:
        compiled_ignores.append(ig if isinstance(ig, re.Pattern) else re.compile(ig))

    def ignored(dirname: str) -> bool:
        return any(r.search(dirname) for r in compiled_ignores)

    for dirpath, dirnames, filenames in os.walk(
        root, topdown=True, onerror=lambda e: None, followlinks=follow_symlinks
    ):
        # 修剪需要忽略的目录
        dirnames[:] = [d for d in dirnames if not ignored(d)]

        for fname in filenames:
            p = Path(dirpath) / fname
            if match_on == "name":
                target = fname
            elif match_on == "relative":
                rel = p.relative_to(root)
                target = rel.as_posix() if normalize_posix else str(rel)
            elif match_on == "path":
                target = p.as_posix() if normalize_posix else str(p)
            else:
                raise ValueError("match_on 必须是 'name' | 'relative' | 'path'")

            if regex.search(target):
                yield str(p) if return_str else p


def find_files_by_regex(
    root: Union[str, Path], pattern: Union[str, Pattern[str]], **kwargs
) -> list[Path]:
    """便捷版：一次性返回列表（基于上面的生成器）。"""
    return [Path(path) for path in iter_files_by_regex(root, pattern, **kwargs)]
