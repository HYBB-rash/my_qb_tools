import tempfile
from pathlib import Path

from tools.service import ensure_tvshow_nfo_in_dir


def test_ensure_tvshow_nfo_in_dir_writes_file():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td) / "ShowRoot"
        base.mkdir()

        nfo = ensure_tvshow_nfo_in_dir(base, tmdb_id=123456, title="Dummy Title")

        assert nfo.exists()
        content = nfo.read_text(encoding="utf-8")
        assert "<tvshow>" in content
        assert "uniqueid" in content and "123456" in content
