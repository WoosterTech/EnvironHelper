import pytest
from environ.environ import Env  # type: ignore[import-untyped]

from environhelper.main import (
    generate_env_file_content,
    get_env_types,
    parse_settings_file,
)


@pytest.fixture()
def settings_file(tmp_path):
    settings_file = tmp_path / "settings.py"
    settings_file.write_text(
        """
        DEBUG = env('DEBUG', default=True)
        SECRET_KEY = env.str("SECRET_KEY")
        DATABASE_URL = env.str("DATABASE_URL", default="sqlite:///db.sqlite3")
        """
    )
    return settings_file


def test_get_env_types():
    valid_types = get_env_types(Env)
    assert "bool" in valid_types


def test_parse_settings_file(settings_file):
    result = parse_settings_file(settings_file)
    assert ("DEBUG", "True") in result.items()
    assert ("SECRET_KEY", "") in result.items()
    assert ("DATABASE_URL", '"sqlite:///db.sqlite3"') in result.items()


def test_generate_env_file_content():
    env_vars = {
        "DEBUG": "True",
        "SECRET_KEY": "",
        "DATABASE_URL": '"sqlite:///db.sqlite3"',
    }
    result = generate_env_file_content(env_vars)
    assert "DEBUG=True" in result
    assert "SECRET_KEY=" in result
    assert 'DATABASE_URL="sqlite:///db.sqlite3"' in result
