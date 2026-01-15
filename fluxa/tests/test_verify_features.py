"""Verify all documented features exist and work."""
import fluxa
from fluxa import (
    Environment,
    AsyncEnvironment,
    SandboxedEnvironment,
    install_null_translations,
    install_gettext_translations,
    install_debug,
    create_debug_function,
    has_orjson,
    has_pydantic,
    orjson_dumps,
    orjson_loads,
    validate_context,
)

print("Checking all documented exports...")

# 1. Basic Environment
env = Environment()
print("  Environment: OK")

# 2. SandboxedEnvironment
senv = SandboxedEnvironment()
print("  SandboxedEnvironment: OK")

# 3. AsyncEnvironment
aenv = AsyncEnvironment()
print("  AsyncEnvironment: OK")

# 4. i18n functions
env2 = Environment()
install_null_translations(env2)
result = env2.render_str("{{ _('Hello') }}")
assert result == "Hello", f"Expected Hello, got {result}"
result = env2.render_str("{{ gettext('World') }}")
assert result == "World", f"Expected World, got {result}"
result = env2.render_str("{{ ngettext('1 item', 'items', 1) }}")
assert result == "1 item", f"Expected 1 item, got {result}"
result = env2.render_str("{{ ngettext('1 item', 'items', 5) }}")
assert result == "items", f"Expected items, got {result}"
result = env2.render_str("{{ pgettext('menu', 'File') }}")
assert result == "File", f"Expected File, got {result}"
print("  i18n functions (_, gettext, ngettext, pgettext): OK")

# 5. Debug functions
debug_fn = create_debug_function()
info = debug_fn(x=1, y=2)
assert "DEBUG INFO" in info, f"Expected DEBUG INFO in result"
print("  create_debug_function: OK")

env3 = Environment()
install_debug(env3)
result = env3.render_str("{{ debug() }}")
assert "DEBUG INFO" in result
print("  install_debug: OK")

# 6. orjson/pydantic detection
print(f"  has_orjson(): {has_orjson()}")
print(f"  has_pydantic(): {has_pydantic()}")

# 7. orjson functions (if available)
if has_orjson():
    data = {"name": "Alice"}
    json_bytes = orjson_dumps(data)
    parsed = orjson_loads(json_bytes)
    assert parsed == data
    print("  orjson_dumps/orjson_loads: OK")
else:
    print("  orjson not installed (skipping orjson_dumps/orjson_loads)")

# 8. pydantic validation (if available)
if has_pydantic():
    from pydantic import BaseModel
    class User(BaseModel):
        name: str
        age: int
    user = validate_context(User, {"name": "Bob", "age": 30})
    assert user.name == "Bob"
    print("  validate_context: OK")
else:
    print("  pydantic not installed (skipping validate_context)")

print()
print("ALL DOCUMENTED FEATURES EXIST AND WORK!")
