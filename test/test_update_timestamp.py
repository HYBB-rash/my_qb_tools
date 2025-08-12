import time

from share import LOGGER
from tools.dba import get_task_by_id, insert_task, update_task_status


def test_updated_at_increases_and_status_changes():
    # 1) 插入一条测试任务
    name = "__timestamp_test__"
    category = "test"
    tags = {"season": 1, "tmdb": {"id": 999999, "name": "TEMP"}}
    content_path = "C:/tmp/does_not_need_to_exist.mp4"

    task_id = insert_task(name, category, tags, content_path).value
    assert task_id is not None, "插入任务失败，返回了 None 的 rowid"

    # 2) 读取初始 updated_at
    task_before = get_task_by_id(task_id).value
    assert task_before is not None, "没有读到刚插入的任务"
    before_ts = task_before.updated_at
    LOGGER.info(f"初始 updated_at: {before_ts}")

    # 3) 等待 1s，确保时间戳可比较
    time.sleep(1)

    # 4) 更新状态并再次读取
    update_task_status(task_id, 1)
    task_after = get_task_by_id(task_id).value
    assert task_after is not None, "更新后没有读到任务"
    after_ts = task_after.updated_at
    LOGGER.info(f"更新后 updated_at: {after_ts}")

    # 5) 断言：时间戳应变大，状态应为 1
    assert after_ts > before_ts, f"updated_at 未更新: before={before_ts}, after={after_ts}"
    assert task_after.status == 1, f"状态未更新为 1，当前: {task_after.status}"

    LOGGER.info("OK: updated_at 已随着状态变化更新")
