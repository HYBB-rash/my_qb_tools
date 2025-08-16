import json
import sqlite3
from dataclasses import dataclass
from typing import Any

from tools.share import sqlite_row_to_dict

"""
meta 模块对应 sqlite 表结构的定义
如果出现联合查询，不需要在这里定义联合查询的结果类型，使用默认的 dict[str, Any] 即可。
"""


@dataclass
class TMDB:
    id: int
    name: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TMDB":
        return cls(id=data["id"], name=data["name"])


@dataclass
class Tags:
    season: int
    tmdb: TMDB

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Tags":
        return cls(season=data["season"], tmdb=TMDB.from_dict(data["tmdb"]))


@dataclass
class Task:
    id: int
    name: str
    category: str
    tags: Tags
    content_path: str
    status: int
    created_at: int
    updated_at: int

    @classmethod
    def from_dict(cls, data: dict[str, Any] | sqlite3.Row) -> "Task":
        return cls(
            id=data["id"],
            name=data["name"],
            category=data["category"],
            tags=Tags.from_dict(json.loads(data["tags"])),
            content_path=data["content_path"],
            status=data["status"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    @classmethod
    def format_for_sqlite(cls, cursor: sqlite3.Cursor, data: tuple[Any, ...]) -> "Task":
        task = sqlite_row_to_dict(cursor, data)
        return Task.from_dict(task)


@dataclass
class Cfg:
    id: int
    season: int
    tmdb_id: int
    cfg: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any] | sqlite3.Row) -> "Cfg":
        return cls(
            id=data["id"],
            season=data["season"],
            tmdb_id=data["tmdb_id"],
            cfg=json.loads(data["cfg"]),
        )

    @classmethod
    def format_for_sqlite(cls, cursor: sqlite3.Cursor, data: tuple[Any, ...]) -> "Cfg":
        cfg = sqlite_row_to_dict(cursor, data)
        return cls.from_dict(cfg)

    @classmethod
    def get_default_cfg(cls):
        with open("./cfg.json") as file:
            return cls(id=0, season=0, tmdb_id=0, cfg=json.load(file))
