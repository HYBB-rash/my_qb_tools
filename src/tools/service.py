import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from share import LOGGER, UnknownKeyError
from share.result import Err, Ok, Result
from tools import dba
from tools.meta import Cfg, Task
from tools.move import MOVE_FACTORY, MoveFunctionNotFound

BASE = "https://api.themoviedb.org/3"


load_dotenv()


def fetch_tmdb():
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})

    def _(kind: str, tmdb_id: int, **kwargs) -> dict[str, Any]:
        token = os.getenv("TMDB_API_TOKEN", None)
        response = session.get(
            f"{BASE}/{kind}/{tmdb_id}",
            params={
                "language": "zh-CN",
                **kwargs,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()

    return _


def fetch_tvshows(
    tmdb_id: int, language: str = "zh-CN", watch_region: str = "CN", **kwargs
) -> dict[str, Any]:
    TV_APPENDS = ",".join(
        [
            "alternative_titles",
            "credits",
            "images",
            "keywords",
            "content_ratings",
            "recommendations",
            "similar",
            "videos",
            "external_ids",
            "watch/providers",
            "translations",
        ]
    )

    fetcher = fetch_tmdb()
    return fetcher(
        "tv",
        tmdb_id,
        language=language,
        watch_region=watch_region,
        append_to_response=TV_APPENDS,
        **kwargs,
    )


def fetch_movie(
    tmdb_id: int, language: str = "zh-CN", watch_region: str = "CN", **kwargs
) -> dict[str, Any]:
    MOVIE_APPENDS = ",".join(
        [
            "alternative_titles",
            "credits",
            "images",
            "keywords",
            "release_dates",
            "recommendations",
            "similar",
            "videos",
            "external_ids",
            "watch/providers",
            "translations",
        ]
    )

    fetcher = fetch_tmdb()
    return fetcher(
        "movie",
        tmdb_id,
        language=language,
        watch_region=watch_region,
        append_to_response=MOVIE_APPENDS,
        **kwargs,
    )


@dataclass
class CfgNotFoundException(Exception):
    task: Task

    def __str__(self) -> str:
        return f"根据提供的 task 信息，找不到库内的cfg配置信息. Task: {self.task}."


def get_cfg(task: Task) -> Cfg:
    result = dba.get_cfg(task)

    if result.value is None:
        raise CfgNotFoundException(task)

    return result.value


def create_task(name: str, category: str, tags: dict, content_path: str) -> int:
    result = dba.insert_task(name, category, tags, content_path)
    if result.value is None:
        LOGGER.error("意外错误，插入不可能失败")
        raise RuntimeError("创建任务时发现返回的 row id 是 None，非期望值")

    return result.value


@dataclass(eq=False)
class TaskNotFoundException(Exception):
    arguments: dict

    def __str__(self) -> str:
        return f"使用 {self.arguments} 参数在表中查询，没有找到对应的 task ."


def get_task(id: int) -> Result[Task, TaskNotFoundException]:
    result = dba.get_task_by_id(id)

    if result.value is None:
        return Err(TaskNotFoundException(arguments={"id": id}))

    return Ok(result.value)


def pop_task() -> Result[Task, TaskNotFoundException]:
    task = dba.get_least_task().value

    if task is None:
        return Err(TaskNotFoundException({"args": "pop"}))

    return Ok(task)


def change_task_staus_doing(task: Task):
    dba.update_task_status(task.id, 1)


def change_task_status_done(task: Task):
    dba.update_task_status(task.id, 2)
    LOGGER.info("本次硬链接+重命名任务完成")


def move_file(task: Task, cfg: Cfg) -> None:
    LOGGER.info("开始硬链接到指定位置")
    category_mapping = cfg.cfg["category_mapping"]
    assert isinstance(category_mapping, dict), (
        "配置有错误，类目映射文件夹应该是一个dict类型"
    )

    root_dir = category_mapping.get(task.category)
    assert isinstance(root_dir, str), "路径一定是字符串"

    tmdb_id = cfg.tmdb_id
    tv_show_name = get_tv_show_name_by_id(tmdb_id)

    season = f"season {task.tags.season}"

    destination = Path(root_dir).joinpath(tv_show_name).joinpath(season)
    LOGGER.debug(f"目标地址: {destination}")

    if destination.exists() and not destination.is_dir():
        raise NotADirectoryError(f"{destination} 已存在但不是文件夹")

    destination.mkdir(parents=True, exist_ok=True)

    ensure_tvshow_nfo_in_dir(
        Path(root_dir).joinpath(tv_show_name), tmdb_id, tv_show_name
    )

    content_path = Path(task.content_path)
    if not content_path.exists():
        raise RuntimeError(f"task 对应的文件路径并不存在, path: {content_path}")

    try:
        mover = MOVE_FACTORY.create(f"tmdb-{tmdb_id}-s{task.tags.season}")
        mover(content_path, destination)
    except UnknownKeyError:
        LOGGER.error("没有找到对应的实现，请检查参数是否正确")
        raise MoveFunctionNotFound(task.tags.season, tmdb_id)


def ensure_tvshow_nfo_in_dir(
    dir_path: Path | str, tmdb_id: int, title: str | None = None
) -> Path:
    """
    确保指定目录下存在 tvshow.nfo：
    - 已存在：跳过并返回 tvshow.nfo 的路径
    - 不存在：写入一个最小的 NFO，只包含 TMDB 的 uniqueid（可选附加 title）

    参数:
        dir_path: 需要检查/写入的剧集根目录路径
        tmdb_id:  TMDB 的剧集 ID
        title:    可选的剧名；若提供，将一并写入 &lt;title&gt;

    返回:
        写入/已存在的 tvshow.nfo 的 Path
    """
    base = Path(dir_path)
    if not base.exists():
        raise FileNotFoundError(f"目录不存在: {base}")
    if not base.is_dir():
        raise NotADirectoryError(f"不是目录: {base}")

    nfo_path = base / "tvshow.nfo"
    if nfo_path.exists():
        LOGGER.debug("tvshow.nfo 已存在，跳过: %s", nfo_path)
        return nfo_path

    # 仅在需要写入时创建父目录（通常目录已存在）
    nfo_path.parent.mkdir(parents=True, exist_ok=True)

    xml_content = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        "<tvshow>\n"
        f'  <uniqueid type="tmdb" default="true">{tmdb_id}</uniqueid>\n'
        "</tvshow>\n"
    )

    # 以 UTF-8 无 BOM 写入，换行统一为 \n
    nfo_path.write_text(xml_content, encoding="utf-8", newline="\n")
    LOGGER.info("已写入 tvshow.nfo → %s (tmdb=%s)", nfo_path, tmdb_id)
    return nfo_path


@dataclass(eq=False)
class TVShowNameNotFound(Exception):
    id: int

    def __str__(self) -> str:
        return f"提供的 tmdb 查询返回的 name 为空: tmdb_id: {self.id}"


def get_tv_show_name_by_id(
    tmdb_id: int,
) -> str:
    tv_show = fetch_tvshows(tmdb_id=tmdb_id)
    title = tv_show.get("name") or tv_show.get("original_name")
    assert title is not None, (
        "剧名不可能查不到，通过tmdb的api如果没有查到http会直接报错。如果真的有一天走到这里，就快点确认tmdb是不是改了什么东西。"
    )

    return title


def get_tmm_cmd() -> Path | None:
    """
    自用工具，处于开发成本考虑，暂时就只去支持Windows, 后续支持根据 Path 找命令
    """
    local = Path("C:/Users/Herman/AppData/Local/Programs/")
    tmm_command = Path(local) / "tinyMediaManagerV5" / "tinyMediaManagerCMD.exe"
    if tmm_command.exists():
        return tmm_command
    raise RuntimeError("tmm 命令没有找到。暂时只支持Windows。")


def scrape_and_rename():
    LOGGER.info("开始刮削&&重命名")
    tmm_cmd = get_tmm_cmd()

    step1 = [str(tmm_cmd), "tvshow", "-u", "--scrapeUnscraped", "-r"]
    # step2 = [str(tmm_cmd), "tvshow", "--scrapeAll"]

    return_code = subprocess.run(step1, check=False)
    LOGGER.info(f"tmm 程序退出码: {return_code}")
    # subprocess.run(step2, check=False)


def create_cfg(season: int, tmdb_id: int, cfg: dict[str, Any] | None = None):
    if cfg is None:
        with open("./cfg.json") as file:
            cfg = json.load(file)

    if cfg is None or not isinstance(cfg, dict):
        raise RuntimeError("加载出问题了，检查提供的默认配置是否有问题")

    dba.insert_cfg(season, tmdb_id, cfg)
