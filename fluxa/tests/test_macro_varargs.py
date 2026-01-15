"""Test macro varargs and kwargs for Jinja2 compatibility"""

from minijinja import Environment

env = Environment()

print("=== Testing Macro Varargs/Kwargs ===")

# Test basic macro with varargs
template1 = """
{% macro test_varargs(a, b) %}
Args: {{ a }}, {{ b }}
Varargs: {{ varargs }}
{% endmacro %}

{{ test_varargs("x", "y", "extra1", "extra2") }}
"""
print("Test 1 - Varargs:")
print(env.render_str(template1))

# Test macro with kwargs
template2 = """
{% macro test_kwargs(name) %}
Name: {{ name }}
Kwargs: {{ kwargs }}
{% endmacro %}

{{ test_kwargs("Alice", extra="value", foo="bar") }}
"""
print("Test 2 - Kwargs:")
print(env.render_str(template2))

# Test macro with both varargs and kwargs
template3 = """
{% macro test_both(a) %}
Arg: {{ a }}
Varargs: {{ varargs }}
Kwargs: {{ kwargs }}
{% endmacro %}

{{ test_both("first", "extra1", "extra2", key1="val1", key2="val2") }}
"""
print("Test 3 - Both Varargs and Kwargs:")
print(env.render_str(template3))

# Test macro without extra args
template4 = """
{% macro test_normal(a, b) %}
Args: {{ a }}, {{ b }}
Varargs: {{ varargs }}
Kwargs: {{ kwargs }}
{% endmacro %}

{{ test_normal("x", "y") }}
"""
print("Test 4 - No Extra Args:")
print(env.render_str(template4))

print("=== All macro tests complete ===")
