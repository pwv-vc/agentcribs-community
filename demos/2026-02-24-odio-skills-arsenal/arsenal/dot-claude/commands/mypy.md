We are cleaning up mypy errors on this active PR. To see the strict mypy errors you MUST use the `just lint-and-fix` command in the api directory; it runs both baseline checks on all files AND strict checks on all src files in parallel.

## Type Annotation Patterns

### Use Proper Types, Not `Any` with Inline Ignores

**DO NOT** use `Any` with inline type ignore comments as a quick fix. Instead:

1. **For JSON data**: Use `JSONValue` or `JSONSchema` from `@api/src/json_types.py`
   ```python
   from json_types import JSONValue

   def process_field(raw_value: JSONValue) -> str | None:  # ✅ Good
   def process_field(raw_value: Any) -> str | None:  # ❌ Bad - type: ignore[explicit-any]
   ```

2. **For Optional parameters**: Use `T | None` instead of implicit Optional
   ```python
   def create_person(name: str | None = None):  # ✅ Good
   def create_person(name: str = None):  # ❌ Bad - causes assignment error
   ```

3. **For dict parameters**: Use `dict[str, Any] | None` for form data that can be optional
   ```python
   def create_form(form_data: dict[str, Any] | None = None):  # ✅ Good
   def create_form(form_data: dict = None):  # ❌ Bad - causes assignment error
   ```

4. **For factory fixtures**: Define Protocol classes instead of using `Callable` or `Any`
   ```python
   # ✅ Good - Define Protocol
   class PersonFactory(Protocol):
       def __call__(self, name: str | None = None, **overrides: Any) -> Persons: ...  # type: ignore[explicit-any]

   @pytest.fixture
   def person_factory(session) -> PersonFactory:  # Use Protocol type
       def _create(name: str | None = None, **overrides: Any) -> Persons:  # type: ignore[explicit-any]
           ...
       return _create

   # ❌ Bad - Using Callable or Any
   def person_factory(session) -> Callable:  # Essentially Any
   def person_factory(session) -> Any:  # type: ignore[explicit-any]
   ```

### When `# type: ignore[explicit-any]` IS Acceptable

**ONLY** use `# type: ignore[explicit-any]` in these specific cases:

1. **Protocol `__call__` methods** with `**kwargs: Any` for test flexibility
2. **Factory function implementations** that need `**overrides: Any` for test ergonomics
3. **SQLAlchemy event callbacks** with multiple `Any` parameters (conn, cursor, etc.)
4. **Dict types for test timings/metrics** where Any is unavoidable

**Important**: Place the type ignore comment on the **first line** of multi-line function signatures:
```python
def my_function(  # type: ignore[explicit-any]
    param1: str,
    **kwargs: Any,
) -> ReturnType:
```

## Workflow

1. Run `just lint-and-fix` in api directory to see all strict mypy errors
2. Make a plan per file, organizing work into single-file changes
3. Address non-`Any` errors first (missing annotations, Optional types, etc.)
4. For `Any` usage, check if you can use:
   - `JSONValue`/`JSONSchema` from `json_types.py`
   - Protocol classes (see `@api/tests/integration/conftest.py` or `@api/tests/helpers/model_factory_fixtures.py` for examples)
   - Proper Optional types (`T | None`)
5. Keep track of new imports needed
6. After each file: run `just lint-and-fix` to verify
7. Iterate until no mypy errors remain
8. Produce a summary report of changes

## Reference Examples

- Protocol definitions: `@api/tests/integration/conftest.py` (lines 78-100)
- Factory fixtures with Protocols: `@api/tests/helpers/model_factory_fixtures.py`
- JSON type usage: `@api/src/message_processing/onboarding_facts.py`