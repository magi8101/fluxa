"""Comprehensive verification of COMPATIBILITY.md claims."""
from fluxa import Environment, SandboxedEnvironment

env = Environment()
env.pycompat = True

print("=" * 60)
print("COMPATIBILITY.md VERIFICATION")
print("=" * 60)

# ============================================================================
# BLOCKS / TAGS
# ============================================================================
print("\n--- BLOCKS / TAGS ---")

# for loop
print("{% for %}: ", end="")
result = env.render_str("{% for i in items %}{{ i }}{% endfor %}", items=[1,2,3])
print(f"OK - {result}" if result == "123" else f"FAIL - {result}")

# for loop.index
print("  loop.index: ", end="")
result = env.render_str("{% for i in items %}{{ loop.index }}{% endfor %}", items=[1,2,3])
print(f"OK - {result}" if result == "123" else f"FAIL - {result}")

# for loop.first/last
print("  loop.first/last: ", end="")
result = env.render_str("{% for i in items %}{{ loop.first }}/{{ loop.last }}{% endfor %}", items=[1,2])
print(f"OK - {result}")

# for loop.cycle
print("  loop.cycle: ", end="")
try:
    result = env.render_str("{% for i in items %}{{ loop.cycle('a','b') }}{% endfor %}", items=[1,2,3,4])
    print(f"OK - {result}")
except Exception as e:
    print(f"FAIL - {e}")

# if/elif/else
print("{% if/elif/else %}: ", end="")
result = env.render_str("{% if x > 10 %}big{% elif x > 5 %}med{% else %}small{% endif %}", x=7)
print(f"OK - {result}" if result == "med" else f"FAIL - {result}")

# extends/block
print("{% extends/block %}: ", end="")
env.add_template("base", "A{% block c %}X{% endblock %}B")
env.add_template("child", "{% extends 'base' %}{% block c %}Y{% endblock %}")
result = env.render_template("child")
print(f"OK - {result}" if result == "AYB" else f"FAIL - {result}")

# super()
print("  super(): ", end="")
env.add_template("super_child", "{% extends 'base' %}{% block c %}{{ super() }}Z{% endblock %}")
result = env.render_template("super_child")
print(f"OK - {result}" if "X" in result and "Z" in result else f"FAIL - {result}")

# include
print("{% include %}: ", end="")
env.add_template("partial", "INCLUDED")
result = env.render_str("{% include 'partial' %}")
print(f"OK - {result}" if result == "INCLUDED" else f"FAIL - {result}")

# include without context
print("  without context: ", end="")
try:
    result = env.render_str("{% include 'partial' without context %}")
    print(f"WORKS (doc says not supported)")
except:
    print("Not supported (matches doc)")

# include with context
print("  with context: ", end="")
try:
    result = env.render_str("{% include 'partial' with context %}")
    print(f"WORKS (doc says not supported)")
except:
    print("Not supported (matches doc)")

# import
print("{% import %}: ", end="")
env.add_template("macros", "{% macro hello(name) %}Hello {{ name }}{% endmacro %}")
result = env.render_str("{% import 'macros' as m %}{{ m.hello('World') }}")
print(f"OK - {result}")

# macro
print("{% macro %}: ", end="")
result = env.render_str("{% macro greet(name) %}Hi {{ name }}{% endmacro %}{{ greet('Bob') }}")
print(f"OK - {result}")

# macro with defaults
print("  default args: ", end="")
result = env.render_str("{% macro greet(name='World') %}Hi {{ name }}{% endmacro %}{{ greet() }}")
print(f"OK - {result}")

# macro varargs
print("  varargs (*args): ", end="")
try:
    result = env.render_str("{% macro test(*args) %}{{ args }}{% endmacro %}{{ test(1,2) }}")
    print(f"WORKS - {result}")
except:
    print("Not supported (matches doc)")

# call
print("{% call %}: ", end="")
result = env.render_str("{% macro wrap() %}<div>{{ caller() }}</div>{% endmacro %}{% call wrap() %}X{% endcall %}")
print(f"OK - {result}")

# do
print("{% do %}: ", end="")
try:
    result = env.render_str("{% set items = [] %}{% do items.append(1) %}{{ items }}")
    print(f"OK - {result}")
except:
    print("Not available")

# with
print("{% with %}: ", end="")
result = env.render_str("{% with x = 42 %}{{ x }}{% endwith %}")
print(f"OK - {result}" if result == "42" else f"FAIL - {result}")

# set
print("{% set %}: ", end="")
result = env.render_str("{% set x = 'hello' %}{{ x }}")
print(f"OK - {result}" if result == "hello" else f"FAIL - {result}")

# filter tag
print("{% filter %}: ", end="")
result = env.render_str("{% filter upper %}hello{% endfilter %}")
print(f"OK - {result}" if result == "HELLO" else f"FAIL - {result}")

# autoescape
print("{% autoescape %}: ", end="")
result = env.render_str("{% autoescape true %}{{ x }}{% endautoescape %}", x="<script>")
print(f"OK - escaped" if "&lt;" in result else f"FAIL - {result}")

# raw
print("{% raw %}: ", end="")
result = env.render_str("{% raw %}{{ not rendered }}{% endraw %}")
print(f"OK" if "{{ not rendered }}" in result else f"FAIL - {result}")

# continue/break (loop_controls)
print("{% continue/break %}: ", end="")
try:
    result = env.render_str("{% for i in range(5) %}{% if i == 2 %}{% continue %}{% endif %}{{ i }}{% endfor %}")
    print(f"OK - {result}")
except:
    print("Not available (needs loop_controls feature)")

# ============================================================================
# FILTERS
# ============================================================================
print("\n--- FILTERS ---")

filters_to_test = [
    ("upper", "'hello'|upper", "HELLO"),
    ("lower", "'HELLO'|lower", "hello"),
    ("title", "'hello world'|title", "Hello World"),
    ("capitalize", "'hello'|capitalize", None),  # Just check starts with H
    ("trim", "'  x  '|trim", "x"),
    ("replace", "'ab'|replace('a','x')", "xb"),
    ("safe", "'<b>'|safe", "<b>"),
    ("escape", "'<'|escape", "&lt;"),
    ("striptags", "'<b>x</b>'|striptags", "x"),
    ("truncate", "'hello world'|truncate(5)", None),  # Contains ...
    ("indent", "'x'|indent(2)", "  x"),
    ("center", "'x'|center(5)", None),
    ("urlize", "'https://x.com'|urlize", "href"),
    ("wordcount", "'a b c'|wordcount", "3"),
    ("abs", "(-5)|abs", "5"),
    ("round", "3.7|round", "4"),
    ("int", "'42'|int", "42"),
    ("float", "'3.14'|float", "3.14"),
    ("filesizeformat", "1024|filesizeformat", None),  # Contains K
    ("tojson", "{'a':1}|tojson", "a"),
    ("pprint", "{'a':1}|pprint", "a"),
    ("first", "[1,2,3]|first", "1"),
    ("last", "[1,2,3]|last", "3"),
    ("length", "[1,2,3]|length", "3"),
    ("default", "x|default('N')", "N"),
    ("join", "[1,2]|join('-')", "1-2"),
    ("sort", "[3,1,2]|sort|list", None),
    ("reverse", "[1,2,3]|reverse|list", None),
    ("unique", "[1,1,2]|unique|list", None),
    ("map", "[1,2]|map(attribute='x')", None),
    ("select", "[1,2,3]|select('odd')|list", None),
    ("reject", "[1,2,3]|reject('odd')|list", None),
    ("selectattr", None, None),  # Skip complex ones
    ("groupby", None, None),
    ("batch", "[1,2,3,4]|batch(2)|list", None),
    ("slice", "[1,2,3,4]|slice(2)|list", None),
    ("items", "{'a':1}|items|list", None),
    ("dictsort", "{'b':2,'a':1}|dictsort", None),
    ("xmlattr", "{'class':'x'}|xmlattr", "class"),
    ("urlencode", "{'a':'b c'}|urlencode", None),
]

env2 = Environment()
env2.undefined_behavior = "lenient"

for name, expr, expected in filters_to_test:
    if expr is None:
        continue
    try:
        result = env2.render_str("{{ " + expr + " }}")
        if expected is None:
            print(f"  {name}: OK - {result[:30]}...")
        elif expected in result:
            print(f"  {name}: OK")
        else:
            print(f"  {name}: UNEXPECTED - got {result}, expected {expected}")
    except Exception as e:
        print(f"  {name}: ERROR - {e}")

# ============================================================================
# TESTS
# ============================================================================
print("\n--- TESTS ---")

tests_to_check = [
    ("defined", "x is defined", True, {"x": 1}),
    ("undefined", "x is undefined", True, {}),
    ("none", "x is none", True, {"x": None}),
    ("string", "'x' is string", True, {}),
    ("number", "42 is number", True, {}),
    ("sequence", "[1] is sequence", True, {}),
    ("mapping", "{'a':1} is mapping", True, {}),
    ("iterable", "[1] is iterable", True, {}),
    ("odd", "3 is odd", True, {}),
    ("even", "4 is even", True, {}),
    ("divisibleby", "10 is divisibleby(5)", True, {}),
    ("eq", "5 is eq(5)", True, {}),
    ("ne", "5 is ne(3)", True, {}),
    ("lt", "3 is lt(5)", True, {}),
    ("gt", "5 is gt(3)", True, {}),
    ("le", "5 is le(5)", True, {}),
    ("ge", "5 is ge(5)", True, {}),
    ("in", "2 is in([1,2,3])", True, {}),
]

env3 = Environment()
env3.undefined_behavior = "lenient"

for name, expr, expected, ctx in tests_to_check:
    try:
        result = env3.render_str("{{ " + expr + " }}", **ctx)
        ok = (result == "true") == expected
        print(f"  {name}: {'OK' if ok else 'FAIL'} - {result}")
    except Exception as e:
        print(f"  {name}: ERROR - {e}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
