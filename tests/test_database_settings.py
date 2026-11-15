from blogs_api.config import Settings
from pydantic import ValidationError
import pytest


def test_settings_requires_database_url_when_env_missing(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValidationError, match="database_url"):
        Settings(_env_file=None)
