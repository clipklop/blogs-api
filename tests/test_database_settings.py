from blogs_api.database import Settings


def test_settings_uses_sqlite_default_when_env_missing():
    settings = Settings(_env_file=None)
    assert settings.database_url.startswith("sqlite")
