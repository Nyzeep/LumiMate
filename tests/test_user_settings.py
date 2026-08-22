import json

from config.app_config import PROJECT_ROOT, USER_SETTINGS_PATH, UserSettings


def test_load_falls_back_to_defaults_when_file_missing(monkeypatch, tmp_path):
    missing = tmp_path / "missing.json"
    monkeypatch.setattr("config.app_config.USER_SETTINGS_PATH", missing)
    settings = UserSettings.load()
    assert settings.language == "zh-CN"
    assert settings.check_update_on_startup is False
    assert settings.startup_page == "home"
    assert settings.reduce_motion is False
    assert settings.ambient_mode == "quiet"


def test_save_then_load_round_trip(monkeypatch, tmp_path):
    target = tmp_path / "user_settings.json"
    monkeypatch.setattr("config.app_config.USER_SETTINGS_PATH", target)
    expected = UserSettings(
        language="en-US",
        check_update_on_startup=True,
        startup_page="workbench",
        reduce_motion=True,
        ambient_mode="breath",
    )
    assert expected.save() is True
    assert UserSettings.load() == expected


def test_example_template_matches_code_defaults():
    payload = json.loads(
        (PROJECT_ROOT / "config" / "user_settings.example.json").read_text(encoding="utf-8")
    )
    defaults = UserSettings()
    assert payload["language"] == defaults.language
    assert payload["check_update_on_startup"] == defaults.check_update_on_startup
    assert payload["startup_page"] == defaults.startup_page
    assert payload["reduce_motion"] == defaults.reduce_motion
    assert payload["ambient_mode"] == defaults.ambient_mode
