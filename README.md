# `create-inspect-typeddict`

Compatibility helpers for creating and inspecting `TypedDict` types.

## Example

```python
from typing import List

from create_inspect_typeddict import (
    create_typeddict,
    get_hints,
    get_required_and_optional_keys,
)

Item = create_typeddict(
    "Item",
    {
        "name": str,
        "tags": List[str],
        "description": str,
    },
    optional_keys=["description"],
)

print(get_hints(Item))
required_keys, optional_keys = get_required_and_optional_keys(Item)
print(sorted(required_keys))
print(sorted(optional_keys))
```

Expected result:

- `name` and `tags` are required
- `description` is optional

## Main Functions

### `is_typeddict(typ)`
Returns `True` when `typ` appears to be a `TypedDict` type.

It prefers `typing_extensions.is_typeddict()` when available and otherwise falls back to structural checks.

### `create_typeddict(name, annotations, optional_keys=None)`
Creates a `TypedDict` class dynamically.

Arguments:

- `name`: class name
- `annotations`: field name to type mapping
- `optional_keys`: iterable of keys that should be optional

Behavior:

- validates that every optional key exists in `annotations`
- creates the `TypedDict`
- populates `__required_keys__` and `__optional_keys__`

### `get_hints(typ)`
Returns a dictionary of resolved type hints for `typ`.

It tries:

1. `typing_extensions.get_type_hints()`
2. `typing.get_type_hints()`
3. raw `__annotations__`

This is useful when consuming `TypedDict` definitions that may contain forward references or compatibility-layer typing objects.

### `get_required_and_optional_keys(typ)`
Returns a `(required_keys, optional_keys)` tuple of `frozenset` values for a `TypedDict`.

Resolution order:

1. `__required_keys__` / `__optional_keys__`
2. `__total__`

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).

