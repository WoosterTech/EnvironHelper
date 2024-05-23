from __future__ import annotations

import inspect
import logging
import re
from pathlib import Path

from environ.environ import Env  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

RE_PATTERN = (
    r"env(?:\.([a-zA-Z_]+))?\(\s*['\"](\w+)['\"](?:,\s*default=(['\"]?.+['\"]?))?\)"
)


def get_env_types(cls) -> list[str]:
    methods = []
    for name, _method in inspect.getmembers(cls, inspect.isfunction):
        if not (
            name.startswith("_")
            or name in ["__class__", "__doc__", "__module__", "__init__"]
        ):
            method_obj = getattr(cls, name)
            if not isinstance(method_obj, classmethod):
                methods.append(name)

    return methods


def parse_settings_file(settings_file_path: Path | str) -> dict[str, str]:
    """Parse a Django settings file and return a dictionary with environment variables
    and their default values.
    """
    if isinstance(settings_file_path, str):
        settings_file_path = Path(settings_file_path)
    valid_env_types = get_env_types(Env)
    valid_group_count = 3

    env_vars = {}
    pattern = re.compile(RE_PATTERN)

    with settings_file_path.open("r") as file:
        for line in file:
            re_match = pattern.search(line)
            if re_match:
                match_groups = re_match.groups()
                if len(match_groups) != valid_group_count:
                    msg = (
                        f"Invalid number of groups in regex match: {len(match_groups)}"
                    )
                    raise ValueError(msg)
                value_type, key, default_value = re_match.groups()
                if value_type not in valid_env_types and value_type is not None:
                    msg = f"Invalid env type: {value_type}"
                    raise ValueError(msg)
                if default_value is None:
                    default_value = ""
                if value_type == "bool" or default_value.lower() in ["true", "false"]:
                    default_value = default_value.capitalize()  # True/False
                env_vars[key] = default_value

    return env_vars


def generate_env_file_content(env_vars: dict[str, str]) -> str:
    """Generate a .env file content from a dictionary of environment variables and their
    default values."""
    lines = []
    for key, default_value in env_vars.items():
        line = f"{key}={default_value}"
        lines.append(line)
    return "\n".join(lines)


def write_env_file(output_path: Path | str, content: str) -> None:
    if isinstance(output_path, str):
        output_path = Path(output_path)
    with output_path.open("w") as file:
        write_status = file.write(content)
        msg = f"File {output_path.name} write status: {write_status}"
        logger.info(msg)


def main(settings_file_path: Path | str, output_path: Path | str) -> None:
    if isinstance(settings_file_path, str):
        settings_file_path = Path(settings_file_path)
    if isinstance(output_path, str):
        output_path = Path(output_path)

    env_vars = parse_settings_file(settings_file_path)
    env_content = generate_env_file_content(env_vars)
    write_env_file(output_path, env_content)

    msg = f"Generated {output_path} with the following content:"
    logger.info(msg)
    msg = env_content
    logger.info(msg)
