from src.store import SeenStore


def test_new_job_is_new(tmp_path):
    store = SeenStore(path=tmp_path / "seen.json")
    assert store.is_new("greenhouse:acme:1") is True


def test_mark_seen_persists_across_instances(tmp_path):
    path = tmp_path / "seen.json"
    store = SeenStore(path=path)
    store.mark_seen("greenhouse:acme:1")
    store.save()

    reloaded = SeenStore(path=path)
    assert reloaded.is_new("greenhouse:acme:1") is False
    assert reloaded.is_new("greenhouse:acme:2") is True


def test_corrupt_store_file_treated_as_empty(tmp_path):
    path = tmp_path / "seen.json"
    path.write_text("not valid json", encoding="utf-8")
    store = SeenStore(path=path)
    assert store.is_new("anything") is True
