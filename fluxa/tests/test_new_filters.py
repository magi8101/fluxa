"""Test script for new filters"""

from fluxa import Environment

env = Environment()

print("=== Testing New Jin Filters ===")

# filesizeformat tests
print("filesizeformat (1024 bytes):", env.render_str("{{ 1024|filesizeformat }}"))
print("filesizeformat (1536 bytes):", env.render_str("{{ 1536|filesizeformat }}"))
print("filesizeformat decimal (1500):", env.render_str("{{ 1500|filesizeformat(true) }}"))
print("filesizeformat (1048576):", env.render_str("{{ 1048576|filesizeformat }}"))

# urlize tests
print("urlize:", env.render_str('{{ "Check https://example.com here"|urlize }}'))
print("urlize email:", env.render_str('{{ "Contact test@example.com now"|urlize }}'))

# forceescape tests
print("forceescape:", env.render_str("{{ s|forceescape }}", s="<script>alert('xss')</script>"))

print("=== All filter tests complete ===")
