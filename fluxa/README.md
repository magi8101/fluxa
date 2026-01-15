# Fluxa

> A high-performance Jinja2-compatible template engine for Python.

**Fluxa** is a fork of [MiniJinja](https://github.com/mitsuhiko/minijinja) by Armin Ronacher, enhanced with additional features for modern Python applications.

## What's Different from MiniJinja?

This fork adds several features that weren't available in the original:

- **Native Async Support** - True async rendering with `pyo3-async-runtimes` + tokio (not ThreadPoolExecutor)
- **OrJSON Integration** - Fast JSON serialization/deserialization
- **Pydantic Integration** - Type-safe context validation
- **Sandbox Mode** - Secure template rendering with attribute blocking
- **Debug Function** - Template debugging utilities
- **i18n/Gettext** - Full internationalization support

## Installation

```bash
pip install fluxa

# With optional dependencies
pip install fluxa[fast]      # orjson for faster JSON
pip install fluxa[pydantic]  # pydantic support
pip install fluxa[all]       # everything
```

## Quick Start

```python
from fluxa import Environment

env = Environment()
result = env.render_str("Hello {{ name }}!", name="World")
print(result)  # "Hello World!"
```

## Async Support

```python
from fluxa import AsyncEnvironment

async with AsyncEnvironment() as env:
    result = await env.render_str_async("Hello {{ name }}!", name="World")
```

## Sandbox Mode

```python
from fluxa import SandboxedEnvironment

env = SandboxedEnvironment()
# Blocks: __class__, __mro__, __globals__, _private attributes
result = env.render_str("{{ user.name }}", user={"name": "Alice"})
```

## License

Apache-2.0 (same as MiniJinja)

## Credits

- [Armin Ronacher](https://github.com/mitsuhiko) - Original MiniJinja author
- [magi8101](https://github.com/magi8101) - Fluxa fork maintainer
