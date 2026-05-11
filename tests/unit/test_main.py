from search_engine import main


def test_main_delegates_to_cli_run(monkeypatch):
    called = {}

    def fake_run():
        called["used"] = True
        return 7

    monkeypatch.setattr(main, "run", fake_run)

    assert main.main() == 7
    assert called["used"] is True
