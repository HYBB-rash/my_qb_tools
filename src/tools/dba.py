import json
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from share import LOGGER, format_timestamp, sqlite_row_to_dict
from share.result import Ok, Result, err
from tools.meta import Cfg, Task

load_dotenv()
DB_PATH = Path("data")
DB_FILE = DB_PATH / "app.db"


SCHEMA = """
PRAGMA encoding = 'UTF-8';   -- 默认就是 UTF-8
PRAGMA encoding;             -- 查询当前编码

CREATE TABLE IF NOT EXISTS task(
    id           INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    category     TEXT NOT NULL DEFAULT '',
    tags         TEXT NOT NULL CHECK (json_valid(tags)),
    content_path TEXT NOT NULL,
    status       INTEGER NOT NULL DEFAULT 0,  -- 0: 未开始, 1: 进行中, 2: 已完成, 3: 已取消
    created_at   INTEGER NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER)),
    updated_at   INTEGER NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER))
);

CREATE TABLE IF NOT EXISTS cfg(
    id      INTEGER PRIMARY KEY,
    season  INTEGER NOT NULL DEFAULT 1,            -- 1: 第一季, 2: 第二季, ...
    tmdb_id INTEGER NOT NULL,                      -- TMDB ID
    cfg     TEXT NOT NULL CHECK (json_valid(cfg))  -- 配置内容
);

CREATE TABLE IF NOT EXISTS locks(
    id         INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,                                                     -- 锁的名称. name 对应的是事件，事件可重复发生，且我希望留痕，不担心表膨胀，所以用 token 来区分锁的唯一性, 不使用 name 唯一性
    token      TEXT NOT NULL UNIQUE,                                              -- 防止其他程序来关掉锁
    is_locked  INTEGER NOT NULL DEFAULT  1 CHECK (is_locked IN (0,1)),            -- 是否锁定
    locked_at  INTEGER NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER)),  -- 锁定时间
    expires_at INTEGER NOT NULL                                                   -- timeout 
);

CREATE INDEX IF NOT EXISTS idx_locks_name_active ON locks(name, is_locked, expires_at DESC);
CREATE INDEX IF NOT EXISTS idx_locks_expires_at ON locks(expires_at);
"""


def get_connection():
    if not DB_PATH.exists():
        DB_PATH.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite_row_to_dict

    # 检查数据库是否存在，如果不存在则创建
    locks_table = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='locks'"
    ).fetchone()
    if locks_table is None:
        LOGGER.info(f"数据库不存在，正在创建 {DB_FILE}...")
        connection.executescript(SCHEMA)  # 初始化数据库（如果不存在）
        connection.commit()

    connection.execute("PRAGMA busy_timeout=5000")
    return connection


def insert_task(
    name: str, category: str, tags: dict, content_path: str
) -> Ok[int | None]:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO task (name, category, tags, content_path) VALUES (?, ?, ?, ?)",
            (name, category, json.dumps(tags, ensure_ascii=False), content_path),
        )
        return Ok(cur.lastrowid)


def get_task_by_id(task_id: int) -> Ok[Task | None]:
    with get_connection() as conn:
        conn.row_factory = Task.format_for_sqlite
        cur = conn.execute("SELECT * FROM task WHERE id = ?", (task_id,))

        return Ok(cur.fetchone())


def update_task_status(task_id: int, status: int):
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE task SET status = ?, updated_at = ? WHERE id = ?",
            (status, int(time.time()), task_id),
        )

        if cur.rowcount is None or cur.rowcount == 0:
            raise RuntimeError("改变状态失败")


@dataclass(eq=False)
class LockNotExpiredError(Exception):
    name: str
    token: str
    expires_at: int

    def __str__(self) -> str:
        return f"锁: '{self.name}' 尚未过期 (过期时间={format_timestamp(self.expires_at)}，原时间戳：{self.expires_at})."


@dataclass(eq=False)
class LockExpiredError(Exception):
    name: str
    token: str
    expires_at: int

    def __str__(self) -> str:
        return f"锁: '{self.name}' 已经过期 (过期时间={format_timestamp(self.expires_at)}，原时间戳：{self.expires_at}), 但该锁仍未被释放."


def get_lock(
    name: str, ttl: int = 60
) -> Result[str, LockNotExpiredError | LockExpiredError]:
    token = str(uuid.uuid4())
    now = int(time.time())
    with get_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")

        cur_1 = conn.execute(
            "SELECT id, token, name, expires_at FROM locks WHERE name = ? and is_locked = 1 LIMIT 1",
            (name,),
        )
        row = cur_1.fetchone()
        if row is not None:
            if row["expires_at"] > now:
                return err(
                    LockNotExpiredError(
                        name=row["name"],
                        token=row["token"],
                        expires_at=row["expires_at"],
                    )
                )
            else:
                return err(
                    LockExpiredError(
                        name=row["name"],
                        token=row["token"],
                        expires_at=row["expires_at"],
                    )
                )

        cur_2 = conn.execute(
            """
            INSERT INTO locks (name, token, locked_at, expires_at)
            VALUES (?, ?, ?, ?)
            """,
            (name, token, now, now + ttl),
        )

        if cur_2.rowcount is None:
            conn.rollback()
            raise RuntimeError(f"Failed to acquire lock for {name}.")

        conn.commit()

    return Ok(token)


def release_lock(name: str, token: str) -> Ok[None]:
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE locks SET is_locked = 0 WHERE name = ? AND token = ?", (name, token)
        )
        if cur.rowcount == 0:
            raise RuntimeError(
                f"Failed to release lock for {name}. Lock may not exist or token mismatch."
            )
    return Ok(None)


def get_least_task() -> Ok[Task | None]:
    with get_connection() as conn:
        conn.row_factory = Task.format_for_sqlite
        cur = conn.execute(
            "SELECT * FROM task WHERE status = 0 ORDER BY created_at ASC LIMIT 1"
        )
        task = cur.fetchone()
        return Ok(task)


def get_cfg(task: Task) -> Ok[Cfg | None]:
    with get_connection() as conn:
        conn.row_factory = Cfg.format_for_sqlite
        cur = conn.execute(
            "SELECT * FROM cfg WHERE tmdb_id = ? AND season = ?",
            (task.tags.tmdb.id, task.tags.season),
        )
        cfg = cur.fetchone()
        return Ok(cfg)


def get_cfg_by_idx(tmdb_id: int, season: int) -> Ok[Cfg | None]:
    with get_connection() as conn:
        conn.row_factory = Cfg.format_for_sqlite
        cur = conn.execute(
            "SELECT * FROM cfg WHERE tmdb_id = ? AND season = ?",
            (tmdb_id, season),
        )
        cfg = cur.fetchone()
        return Ok(cfg)


def insert_cfg(season: int, tmdb_id: int, cfg: dict[str, Any]):
    with get_connection() as conn:
        conn.row_factory = Cfg.format_for_sqlite
        conn.execute(
            "INSERT INTO cfg (season, tmdb_id, cfg) VALUES (?, ?, ?)",
            (season, tmdb_id, json.dumps(cfg, ensure_ascii=False)),
        )
