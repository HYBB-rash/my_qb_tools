from typing import Any

from tools import service
from tools.dba import (
    LockExpiredError,
    LockNotExpiredError,
    get_lock,
    release_lock,
)
from tools.service import (
    change_task_status_done,
    change_task_staus_doing,
    create_task,
    get_cfg,
    move_file,
    pop_task,
    scrape_and_rename,
)
from tools.share import LOGGER
from tools.share.result import Err, Ok, Result


def enqueue(
    name: str,
    category: str,
    tags: dict[str, Any],
    content_path: str,
):
    LOGGER.debug(
        f"入队信息, name: {name}, category: {category}, tags: {tags}, content_path: {content_path}"
    )
    result = create_task(name, category, tags, content_path)
    LOGGER.info(f"任务已添加到数据库，ID: {result}")


def execute() -> Result[None, LockExpiredError]:
    result = get_lock("execute_achive", ttl=300)
    if isinstance(result, Err):
        error = result.error
        if isinstance(error, LockNotExpiredError):
            LOGGER.info(f"锁未过期: {error}")
            return Ok(None)
        elif isinstance(error, LockExpiredError):
            LOGGER.error(f"锁已过期: {error}")
            raise error
        raise RuntimeError(f"获取锁失败: {error}")
    lock_token = result.value

    match pop_task():
        case Ok(value=task):
            change_task_staus_doing(task)
            cfg = get_cfg(task)
            move_file(task, cfg)
            scrape_and_rename()
            change_task_status_done(task)
        case Err(error=e):
            LOGGER.debug(f"{e}. 没有任务，跳过...")

    return release_lock("execute_achive", lock_token)


def create_cfg(season: int, tmdb_id: int, cfg: dict[str, Any] | None = None):
    result = get_lock("create_cfg", ttl=300)
    if isinstance(result, Err):
        error = result.error
        if isinstance(error, LockNotExpiredError):
            LOGGER.info(f"锁未过期: {error}")
            return Ok(None)
        elif isinstance(error, LockExpiredError):
            LOGGER.error(f"锁已过期: {error}")
            raise error
        raise RuntimeError(f"获取锁失败: {error}")
    lock_token = result.value

    service.create_cfg(season, tmdb_id, cfg)

    return release_lock("create_cfg", lock_token)
