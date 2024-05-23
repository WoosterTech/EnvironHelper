from __future__ import annotations

import ast
import inspect
import logging
from enum import StrEnum, auto
from pathlib import Path
from typing import Any

from environ.environ import Env
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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


class EnvCallVisitor(ast.NodeVisitor):
    env_vars: dict[str, str] = ...

    def __init__(self, valid_env_types: list[str]):
        self.env_vars = {}
        self.valid_env_types = valid_env_types

    def visit_Call(self, node: ast.Call):  # noqa: N802
        node_func_type = type(node.func)

        match node_func_type:
            case ast.Name:
                node_id = node.func.id
            case ast.Attribute:
                node_id = node.func.value.id
            case _:
                return

        if node_id == "env":
            # Get the type of the env call if specified
            env_type = None
            if isinstance(node.func, ast.Attribute):
                env_type = (
                    node.func.attr if (node.func.attr in self.valid_env_types) else None
                )

            key = None
            default_value = None
            if node.args:
                key = (
                    node.args[0].value
                    if isinstance(node.args[0], ast.Constant)
                    else None
                )
                if len(node.args) > 1:
                    default_value = DefaultValue(
                        value=self._get_default_value(node.args[1]), env_type=env_type
                    )
            if node.keywords:
                keyword_dict = {kw.arg: kw.value.value for kw in node.keywords}
                default_value = keyword_dict.get("default") or None
                if default_value is not None:
                    default_value = DefaultValue(value=default_value, env_type=env_type)
                if key is None:
                    key = (
                        keyword_dict.get("key")
                        if isinstance(keyword_dict.get("key"), ast.Constant)
                        else None
                    )

            if key:
                validated_default_value = (
                    default_value.value_as_str() if default_value else ""
                )
                self.env_vars[key] = validated_default_value

        self.generic_visit(node)

    def _get_default_value(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Constant):
            return str(node.value)
        if isinstance(node, ast.Name):
            return node.id
        return None


class EnvTypes(StrEnum):
    BOOL = auto()


class DefaultValue(BaseModel):
    """Store default value and convert to type based on the value or the env_type."""

    value: str | bool | Any
    env_type: str | EnvTypes | None = None

    def model_post_init(self, __context: Any) -> None:
        if self.env_type is None:
            is_boolean, boolean_value = self.is_booleany()
            self.value = boolean_value if is_boolean else self.value
            self.env_type = EnvTypes.BOOL if is_boolean else None
        return super().model_post_init(__context)

    def value_as_str(self) -> str:
        """Return the value as a string."""
        if self.env_type == EnvTypes.BOOL:
            return str(self.value).capitalize()
        return str(self.value)

    def is_booleany(self) -> tuple[bool, bool]:
        """Return a tuple with two boolean values: the first is True if the value is
        likely a boolean, the second is the resulting boolean value.
        """
        if isinstance(self.value, bool):
            return True, self.value
        if truthy(self.value):
            return True, True
        if falsy(self.value):
            return True, False
        return False, False


def truthy(value: str) -> bool:
    """Return True if the value is truthy, False otherwise."""
    return value.lower() in ("true", "1", "yes", "on")


def falsy(value: str) -> bool:
    """Return True if the value is falsy, False otherwise."""
    return value.lower() in ("false", "0", "no", "off")


def parse_settings_file(settings_file_path: Path | str) -> dict[str, str]:
    """Parse a Django settings file and return a dictionary with environment variables
    and their default values.
    """
    if isinstance(settings_file_path, str):
        settings_file_path = Path(settings_file_path)
    valid_env_types = get_env_types(Env)

    with settings_file_path.open("r") as file:
        tree = ast.parse(file.read(), filename=str(settings_file_path))

    visitor = EnvCallVisitor(valid_env_types)
    visitor.visit(tree)

    return visitor.env_vars


def generate_env_file_content(env_vars: dict[str, str]) -> str:
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


def create_sample_env(settings_file_path: Path | str, output_path: Path | str) -> None:
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
