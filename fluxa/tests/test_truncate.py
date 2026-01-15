"""Test truncate filter compatibility with Jinja2."""
from minijinja import Environment

env = Environment()

# Jinja2 examples from documentation:
# {{ "foo bar baz qux"|truncate(9) }} -> "foo..."
# {{ "foo bar baz qux"|truncate(9, True) }} -> "foo ba..."
# {{ "foo bar baz qux"|truncate(11) }} -> "foo bar baz qux"
# {{ "foo bar baz qux"|truncate(11, False, '...', 0) }} -> "foo bar..."

print("Test 1 (length=9):", repr(env.render_str('{{ s|truncate(length=9) }}', s='foo bar baz qux')))
print("Test 2 (killwords=true):", repr(env.render_str('{{ s|truncate(length=9, killwords=true) }}', s='foo bar baz qux')))
print("Test 3 (length=11, default leeway=5):", repr(env.render_str('{{ s|truncate(length=11) }}', s='foo bar baz qux')))
print("Test 4 (leeway=0):", repr(env.render_str('{{ s|truncate(length=11, killwords=false, leeway=0) }}', s='foo bar baz qux')))

# Expected Jinja2 outputs:
print("\nExpected Jinja2 outputs:")
print("Test 1: 'foo...'")
print("Test 2: 'foo ba...'")
print("Test 3: 'foo bar baz qux' (within leeway)")
print("Test 4: 'foo bar...'")
