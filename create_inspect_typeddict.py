# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

"""Compatibility helpers for creating and inspecting ``TypedDict`` types."""

import typing
from typing import Any, Callable, FrozenSet, Iterable, Mapping, Optional, Tuple, Type

import typing_extensions
from typing_extensions import TypedDict

_KeySets = Tuple[FrozenSet[str], FrozenSet[str]]
_TypeHintsGetter = Callable[[Any], Mapping[str, Any]]

_typing_extensions_is_typeddict = getattr(typing_extensions, "is_typeddict", None)
_typing_extensions_get_type_hints = getattr(typing_extensions, "get_type_hints", None)
_typing_get_type_hints = getattr(typing, "get_type_hints", None)

__all__ = [
    "create_typeddict",
    "get_hints",
    "get_required_and_optional_keys",
    "is_typeddict",
]


def is_typeddict(typ):
    """Return ``True`` when *typ* looks like a ``TypedDict`` class."""
    if _typing_extensions_is_typeddict is not None:
        try:
            return bool(_typing_extensions_is_typeddict(typ))
        except Exception:
            return False

    if not isinstance(typ, type) or not issubclass(typ, dict):
        return False

    annotations = getattr(typ, "__annotations__", None)
    return isinstance(annotations, dict) and hasattr(typ, "__total__")


def create_typeddict(name, annotations, optional_keys=None):
    """Create a ``TypedDict`` class with optional-key metadata preserved."""
    annotations = dict(annotations)
    optional_key_names = frozenset(optional_keys or ())
    unknown_optional_keys = optional_key_names.difference(annotations)
    if unknown_optional_keys:
        raise ValueError(
            "Optional TypedDict keys missing from annotations: %s"
            % ", ".join(sorted(unknown_optional_keys))
        )

    typed_dict = TypedDict(
        str(name),
        annotations,
        total=(not optional_key_names),
    )
    typed_dict.__required_keys__ = frozenset(annotations).difference(optional_key_names)
    typed_dict.__optional_keys__ = optional_key_names
    return typed_dict


def get_hints(typ):
    """Return resolved type hints for *typ*, falling back to raw annotations."""
    for get_type_hints in _iter_type_hint_getters():
        try:
            hints = get_type_hints(typ)
        except Exception:
            continue
        if hints is not None:
            return hints

    return getattr(typ, "__annotations__", None) or {}


def get_required_and_optional_keys(typ):
    """Return ``(required_keys, optional_keys)`` for a ``TypedDict`` type."""
    required_keys = getattr(typ, "__required_keys__", None)
    optional_keys = getattr(typ, "__optional_keys__", None)
    if required_keys is not None or optional_keys is not None:
        return frozenset(required_keys or ()), frozenset(optional_keys or ())

    key_names = set(get_hints(typ)) or set(getattr(typ, "__annotations__", None) or {})
    if getattr(typ, "__total__", True):
        return frozenset(key_names), frozenset()

    return frozenset(), frozenset(key_names)


def _iter_type_hint_getters():
    """Yield available ``get_type_hints`` helpers in preference order."""
    seen = set()
    for get_type_hints in (
        _typing_get_type_hints,
        _typing_extensions_get_type_hints,
    ):
        if get_type_hints is None or get_type_hints in seen:
            continue
        seen.add(get_type_hints)
        yield get_type_hints
