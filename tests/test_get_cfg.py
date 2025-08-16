from tools import dba
from tools.meta import Cfg
from tools.service import get_cfg


def test_get_cfg_roundtrip():
    # Arrange: 插入一条任务与对应 cfg 行
    tags = {"season": 1, "tmdb": {"id": 987654, "name": "Dummy"}}
    task_id = dba.insert_task(
        name="pytest_cfg", category="电视剧", tags=tags, content_path="/tmp/pytest.file"
    ).value
    assert task_id is not None

    # 插入 cfg，与上述 tmdb/season 对应
    default_cfg = {"category_mapping": {"电视剧": str("/tmp/library")}}
    dba.insert_cfg(season=1, tmdb_id=987654, cfg=default_cfg)

    # Act: 读取任务，调用 get_cfg
    task = dba.get_task_by_id(task_id).value
    assert task is not None
    cfg = get_cfg(task)

    # Assert
    assert isinstance(cfg, Cfg)
    assert cfg.tmdb_id == 987654
    assert cfg.season == 1
    assert cfg.cfg["category_mapping"]["电视剧"] == "/tmp/library"
