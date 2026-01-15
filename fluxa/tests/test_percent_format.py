"""Test string % formatting for Jinja2 compatibility"""

from minijinja import Environment

env = Environment()

print("=== Testing String % Formatting ===")

# Basic %s
print("Basic %s:", env.render_str('{{ "Hello %s" % "World" }}'))

# With tuple
print("Multiple args:", env.render_str('{{ "Hello %s, you are %d years old" % ["Alice", 30] }}'))

# Integer formatting
print("%d format:", env.render_str('{{ "Number: %d" % 42 }}'))

# Float formatting
print("%f format:", env.render_str('{{ "Float: %f" % 3.14159 }}'))

# Hex formatting
print("%x format:", env.render_str('{{ "Hex: %x" % 255 }}'))
print("%X format:", env.render_str('{{ "Hex: %X" % 255 }}'))

# Escaped percent
print("Escaped %%:", env.render_str('{{ "100%% complete" }}'))

# Numeric modulo still works
print("Numeric modulo:", env.render_str('{{ 10 % 3 }}'))

print("=== All string % formatting tests complete ===")
