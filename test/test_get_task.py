from tools import dba


def test_insert_and_get_by_id():
    tags = {"season": 2, "tmdb": {"id": 111222, "name": "Dummy2"}}
    task_id = dba.insert_task(
        name="pytest_task", category="电视剧", tags=tags, content_path="/tmp/file2"
    ).value
    assert task_id is not None

    task = dba.get_task_by_id(task_id).value
    assert task is not None
    assert task.id == task_id
    assert task.tags.season == 2
    assert task.tags.tmdb.id == 111222
