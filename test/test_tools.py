from share.result import Ok
from tools.dba import get_lock, release_lock


def test_lock_acquire_and_release():
    lock_name = "test_lock"

    result = get_lock(lock_name, ttl=3)
    assert isinstance(result, Ok), f"期望成功获取锁，实际: {result}"
    token = result.value

    # 释放锁应成功
    rel = release_lock(lock_name, token)
    assert isinstance(rel, Ok)

    # 再次获取应成功（因为已释放）
    result2 = get_lock(lock_name, ttl=1)
    assert isinstance(result2, Ok)
    _ = release_lock(lock_name, result2.value)
