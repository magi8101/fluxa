# Jinja2 Compatibility

This document tracks the differences between Jinja2 and MiniJinja and what
the state of compatibility and future direction is.

## Syntax Differences

Custom delimiters are an optional feature that is largely discouraged. 
For custom delimiters the `custom_syntax` feature needs to be enabled.

MiniJinja by default does not allow unicode identifiers.  These need to be
turned on with the `unicode` feature to achieve parity with Jinja2.

## Runtime Differences

The biggest differences between MiniJinja and Jinja2 stem from the different
runtime environments.  Jinja2 leaks out a lot of the underlying Python engine
whereas MiniJinja implements its own runtime data model.

The most significant differences are documented here:

### Python Methods

MiniJinja does not implement _any_ Python methods.  In particular this means
you cannot do `x.items()` to iterate over items.  For this particular case
both Jinja2 and MiniJinja now support `|items` for iteration instead.  Other
methods are rarely useful and filters should be used instead.

Support for these Python methods can however be loaded by registering the
`unknown_method_callback` from the `pycompat` module in the `minijinja-contrib`
crate.

### Tuples

MiniJinja does not implement tuples.  The creation of tuples with tuple syntax
instead creates lists.

### Keyword Arguments

MiniJinja maps keyword arguments to the creation of dictionaries which are passed
as last argument.  This is done as keyword arguments are not native to Rust and
mapping them to filter functions is tricky.  This also means that some filters in
MiniJinja do not accept the parameters with keyword arguments whereas in Jinja2
they do.

### Undefined

The Jinja2 undefined type tracks the origin of creation, in MiniJinja the undefined
type is a singleton without further information.

### Context

The context in Jinja2 is a data source and the runtime system pulls some pieces of
data from the context as necessary.  This optimization is not particularly useful
in MiniJinja and as such is not performed.  This also means that in MiniJinja the
default behavior is to pass the current state of the context everywhere.

### Escaping

Jinja2 only supports HTML escaping, in MiniJinja it's intended to support other
forms of auto escaping as well.

## Blocks

### `{% for %}`

`for` has feature parity with Jinja2.

### `{% if %}`

`if` has feature parity with Jinja2.

### `{% extends %}`

`extends` has feature parity with Jinja2.

### `{% block %}`

`block` has feature parity with Jinja2.

### `{% include %}`

`include` has feature parity with Jinja2, including `with context` and
`without context` modifiers.

### `{% import %}`

This tag is supported but the returned item is a map of the exported local
variables.  This means that the rendered content of the template is lost.

### `{% macro %}`

The macro tag works very similar to Jinja2 but with some differences.  Most
importantly the special `varargs` and `kwargs` arguments are not supported.
The external introspectable attributes `catch_kwargs`, `catch_varargs` and
are not supported.

### `{% call %}`

`call` has feature parity with Jinja2.

### `{% do %}`

`do` is not currently available in MiniJinja.

### `{% with %}`

`with` has feature parity with Jinja2.

### `{% set %}`

`set` has feature parity with Jinja2.

### `{% filter %}`

`filter` has feature parity with Jinja2.

### `{% autoescape %}`

`autoescape` has feature parity with Jinja2 with an undocumented extension.
Currently it's possible to provide the intended form of auto escaping to
the tag.  This is not documented because it's unclear if this behavior is
useful.

### `{% raw %}`

`raw` has feature parity with Jinja2.

### `{% continue %}`

`continue` is supported only if the `loop_controls` feature is enabled.

### `{% break %}`

`break` is supported only if the `loop_controls` feature is enabled.

## Expressions

Most expressions are supported from Jinja2.  The main difference for expressions
is that `foo["bar"]` and `foo.bar` have the same priority in MiniJinja whereas
in Jinja2 they are used to disambiguate against attributes of the underlying
Python objects.

Differences with expressions mostly stem from the underlying data model.  For
instance Jinja2 templates tend to use `{{ "string" % variable }}` to perform
string formatting which is not supported in MiniJinja.  Likewise not all filters
are available in MiniJinja or behave the same.

## Filters

MiniJinja now supports nearly all common Jinja2 filters. The following table shows
the compatibility status:

### String Filters

| Filter | Status | Notes |
|--------|--------|-------|
| `upper` | Full | Converts to uppercase |
| `lower` | Full | Converts to lowercase |
| `title` | Full | Title case |
| `capitalize` | Full | Capitalize first character |
| `trim` | Full | Strip whitespace from both ends |
| `replace` | Full | Replace substring |
| `safe` | Full | Mark string as safe (no escaping) |
| `escape` / `e` | Full | HTML escape |
| `forceescape` | Full | Force HTML escaping even if safe |
| `striptags` | Full | Remove HTML tags |
| `wordwrap` | Full | Wrap text at width |
| `truncate` | Partial | API differs from Jinja2 (length arg required) |
| `indent` | Full | Indent text |
| `center` | Not Available | Use custom filter |
| `urlize` | Full | Convert URLs to clickable links |
| `wordcount` | Full | Count words in string |

### HTML/XML Filters

| Filter | Status | Notes |
|--------|--------|-------|
| `xmlattr` | Full | Convert dict to XML attributes |
| `urlencode` | Full | URL encode |
| `tojson` | Full | Convert to JSON string |
| `pprint` | Full | Pretty print |

### Numeric Filters

| Filter | Status | Notes |
|--------|--------|-------|
| `abs` | Full | Absolute value |
| `round` | Full | Round number |
| `int` | Full | Convert to integer |
| `float` | Full | Convert to float |
| `filesizeformat` | Full | Human-readable file sizes |
| `format` | Full | Printf-style formatting |

### List/Sequence Filters

| Filter | Status | Notes |
|--------|--------|-------|
| `first` | Full | First item |
| `last` | Full | Last item |
| `length` | Full | Length of sequence |
| `reverse` | Full | Reverse sequence |
| `sort` | Full | Sort sequence |
| `unique` | Full | Remove duplicates |
| `list` | Full | Convert to list |
| `batch` | Full | Batch items |
| `slice` | Full | Slice into n groups |
| `join` | Full | Join items with separator |
| `map` | Full | Apply filter/attr to items |
| `select` | Full | Filter items by test |
| `reject` | Full | Reject items by test |
| `selectattr` | Full | Select by attribute |
| `rejectattr` | Full | Reject by attribute |
| `groupby` | Full | Group by attribute |
| `sum` | Full | Sum values |
| `min` | Full | Minimum value |
| `max` | Full | Maximum value |

### Dict Filters

| Filter | Status | Notes |
|--------|--------|-------|
| `items` | Full | Get dict items |
| `keys` | Full | Get dict keys |
| `values` | Full | Get dict values |
| `dictsort` | Full | Sort dict |
| `d` / `default` | Full | Default value |
| `attr` | Full | Get attribute |

### Test Filters

| Filter | Status | Notes |
|--------|--------|-------|
| `bool` | Full | Convert to boolean |

### Differences from Jinja2

Some filters have minor differences in argument handling:

1. **Keyword Arguments**: Some filters in MiniJinja do not support all keyword
   arguments that Jinja2 does. Use positional arguments when possible.

2. **`attribute` Argument**: Filters like `map`, `select`, `groupby` support the
   `attribute` argument for accessing object attributes.

3. **`truncate`**: Fully supports all 4 Jinja2 parameters:
   - `length` (default: 255)
   - `killwords` (default: false)
   - `end` (default: "...")
   - `leeway` (default: 0)

## Tests

MiniJinja supports all common Jinja2 tests:

| Test | Status | Notes |
|------|--------|-------|
| `defined` | Full | Variable is defined |
| `undefined` | Full | Variable is undefined |
| `none` | Full | Value is None |
| `boolean` | Full | Value is boolean |
| `integer` | Full | Value is integer |
| `float` | Full | Value is float |
| `number` | Full | Value is numeric |
| `string` | Full | Value is string |
| `sequence` | Full | Value is sequence |
| `iterable` | Full | Value is iterable |
| `mapping` | Full | Value is mapping/dict |
| `callable` | Full | Value is callable |
| `odd` | Full | Number is odd |
| `even` | Full | Number is even |
| `divisibleby` | Full | Divisible by n |
| `eq` / `==` | Full | Equality |
| `ne` / `!=` | Full | Not equal |
| `lt` / `<` | Full | Less than |
| `le` / `<=` | Full | Less than or equal |
| `gt` / `>` | Full | Greater than |
| `ge` / `>=` | Full | Greater than or equal |
| `in` | Full | Value in container |
| `sameas` | Full | Same object identity |
| `true` | Full | Value is true |
| `false` | Full | Value is false |
| `filter` | Full | Filter exists |
| `test` | Full | Test exists |

## Python Extensions

MiniJinja-py (the Python bindings) provides additional features:

### orjson Integration

Fast JSON serialization using orjson (7-9x faster than stdlib json):

```python
import minijinja
if minijinja.has_orjson():
    json_bytes = minijinja.orjson_dumps(data)
    parsed = minijinja.orjson_loads(json_bytes)
```

### Pydantic Integration

Pydantic models work seamlessly in templates:

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str

user = User(name="Alice", email="alice@example.com")
env.render_str("{{ user.name }}", user=user)

# Context validation
minijinja.validate_context(User, {"name": "Bob", "email": "bob@example.com"})
```

### Sandbox Mode

Secure template rendering that blocks access to dangerous attributes:

```python
from minijinja import SandboxedEnvironment

env = SandboxedEnvironment()
# Blocks: __class__, __mro__, __globals__, _private attributes
env.render_str("{{ user.name }}", user={"name": "Alice"})  # Works
# env.render_str("{{ ''.__class__ }}")  # Raises TemplateError
```

### Async Support

Native async rendering using pyo3-async-runtimes + tokio (no ThreadPoolExecutor):

```python
from minijinja import AsyncEnvironment

# Basic usage
env = AsyncEnvironment()
result = await env.render_str_async("Hello {{ name }}", name="World")

# With async context manager (recommended)
async with AsyncEnvironment() as env:
    env.add_template("index", "<h1>{{ title }}</h1>")
    result = await env.render_template_async("index", title="Welcome")
    
    # Expression evaluation
    value = await env.eval_expr_async("a + b", a=10, b=20)

# With FastAPI/Starlette
@app.get("/")
async def home():
    return await env.render_str_async("Hello {{ user }}", user="World")
```

The async implementation uses `tokio::spawn_blocking` for CPU-bound template
rendering, ensuring the async event loop is never blocked.

### i18n/Gettext Support

Internationalization support:

```python
from minijinja import install_null_translations, install_gettext_translations

install_null_translations(env)  # Pass-through translations

# With real translations:
# import gettext
# translations = gettext.translation('messages', 'locales', ['es'])
# install_gettext_translations(env, translations)

# Available functions: _(), gettext(), ngettext(), pgettext()
result = env.render_str('{{ _("Hello World") }}')
```

### Debug Function

Template debugging support:

```python
from minijinja import install_debug, create_debug_function

# Install debug() function to environment
install_debug(env)
result = env.render_str("{{ debug(x=x, y=y) }}", x=1, y=2)

# Or create standalone debug function
debug_fn = create_debug_function()
info = debug_fn(name="test", count=42)
```


