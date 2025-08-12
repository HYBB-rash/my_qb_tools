from tools import service


def test_get_tv_show_name_by_id_monkeypatched():
    # 使用猴子补丁替代网络请求
    def fake_fetch_tvshows(tmdb_id: int, **kwargs):
        assert tmdb_id == 123
        return {"name": "Fake Show"}

    orig = service.fetch_tvshows
    try:
        service.fetch_tvshows = fake_fetch_tvshows  # type: ignore[assignment]
        assert service.get_tv_show_name_by_id(123) == "Fake Show"
    finally:
        service.fetch_tvshows = orig  # 还原
