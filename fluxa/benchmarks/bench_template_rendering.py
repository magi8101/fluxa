"""
Comprehensive benchmark suite comparing MiniJinja vs Jinja2 template rendering performance.

Run with: pytest benchmarks/ -v --benchmark-autosave
Compare runs: pytest benchmarks/ --benchmark-compare

Requirements:
    pip install pytest-benchmark jinja2
"""

import pytest
from typing import Any

# Import both template engines
import fluxa
try:
    import jinja2
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False
    jinja2 = None


# Test data fixtures
@pytest.fixture
def simple_context() -> dict[str, Any]:
    """Simple context with basic types."""
    return {
        "name": "World",
        "count": 42,
        "active": True,
        "items": ["apple", "banana", "cherry"],
    }


@pytest.fixture
def complex_context() -> dict[str, Any]:
    """Complex nested context simulating real-world data."""
    return {
        "user": {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "age": 30,
            "address": {
                "street": "123 Main St",
                "city": "Springfield",
                "country": "USA",
            },
            "preferences": {
                "theme": "dark",
                "notifications": True,
                "language": "en",
            },
        },
        "products": [
            {"id": i, "name": f"Product {i}", "price": 10.99 + i, "in_stock": i % 3 != 0}
            for i in range(100)
        ],
        "categories": ["Electronics", "Clothing", "Books", "Home & Garden", "Sports"],
        "site_name": "BenchMark Store",
        "current_year": 2026,
    }


@pytest.fixture
def large_list_context() -> dict[str, Any]:
    """Context with a large list for loop performance testing."""
    return {
        "items": [
            {"id": i, "name": f"Item {i}", "value": i * 1.5, "active": i % 2 == 0}
            for i in range(1000)
        ],
    }


# Template strings
SIMPLE_TEMPLATE = "Hello, {{ name }}! Count: {{ count }}"

VARIABLE_ACCESS_TEMPLATE = """
User: {{ user.name }}
Email: {{ user.email }}
City: {{ user.address.city }}
Theme: {{ user.preferences.theme }}
"""

LOOP_TEMPLATE = """
{% for item in items %}
- {{ item.name }}: {{ item.value }}{% if item.active %} (active){% endif %}
{% endfor %}
"""

CONDITIONAL_TEMPLATE = """
{% if user.age >= 18 %}
Welcome, {{ user.name }}!
{% if user.preferences.notifications %}
You have notifications enabled.
{% endif %}
{% else %}
Sorry, you must be 18 or older.
{% endif %}
"""

FILTER_TEMPLATE = """
{{ user.name|upper }}
{{ user.email|lower }}
{{ products|length }} products available
{{ site_name|title }}
"""

TABLE_TEMPLATE = """
<table>
<thead>
    <tr><th>ID</th><th>Name</th><th>Price</th><th>Status</th></tr>
</thead>
<tbody>
{% for product in products %}
    <tr>
        <td>{{ product.id }}</td>
        <td>{{ product.name }}</td>
        <td>${{ product.price|round(2) }}</td>
        <td>{% if product.in_stock %}In Stock{% else %}Out of Stock{% endif %}</td>
    </tr>
{% endfor %}
</tbody>
</table>
"""

MACRO_TEMPLATE = """
{% macro button(text, type="primary") %}
<button class="btn btn-{{ type }}">{{ text }}</button>
{% endmacro %}

{{ button("Submit") }}
{{ button("Cancel", "secondary") }}
{{ button("Delete", "danger") }}
"""

INHERITANCE_BASE = """
<!DOCTYPE html>
<html>
<head><title>{% block title %}Default{% endblock %}</title></head>
<body>
{% block content %}{% endblock %}
</body>
</html>
"""

INHERITANCE_CHILD = """
{% extends "base.html" %}
{% block title %}{{ page_title }}{% endblock %}
{% block content %}
<h1>{{ heading }}</h1>
<p>{{ content }}</p>
{% endblock %}
"""


class MiniJinjaEngine:
    """MiniJinja template engine wrapper for benchmarking."""
    
    def __init__(self):
        self.env = fluxa.Environment()
        self.name = "MiniJinja"
    
    def render(self, template_str: str, context: dict) -> str:
        return self.env.render_str(template_str, **context)
    
    def render_with_inheritance(self, context: dict) -> str:
        env = fluxa.Environment()
        env.add_template("base.html", INHERITANCE_BASE)
        env.add_template("child.html", INHERITANCE_CHILD)
        return env.render_template("child.html", **context)


class Jinja2Engine:
    """Jinja2 template engine wrapper for benchmarking."""
    
    def __init__(self):
        if not HAS_JINJA2:
            raise ImportError("Jinja2 not installed")
        self.env = jinja2.Environment()
        self.name = "Jinja2"
    
    def render(self, template_str: str, context: dict) -> str:
        template = self.env.from_string(template_str)
        return template.render(**context)
    
    def render_with_inheritance(self, context: dict) -> str:
        loader = jinja2.DictLoader({
            "base.html": INHERITANCE_BASE,
            "child.html": INHERITANCE_CHILD,
        })
        env = jinja2.Environment(loader=loader)
        tmpl = env.get_template("child.html")
        return tmpl.render(**context)


# MiniJinja Benchmarks
class TestMiniJinjaBenchmarks:
    """MiniJinja rendering benchmarks."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.engine = MiniJinjaEngine()
    
    def test_simple_render(self, benchmark, simple_context):
        """Benchmark simple variable substitution."""
        result = benchmark(self.engine.render, SIMPLE_TEMPLATE, simple_context)
        assert "Hello, World!" in result
    
    def test_variable_access(self, benchmark, complex_context):
        """Benchmark nested variable access."""
        result = benchmark(self.engine.render, VARIABLE_ACCESS_TEMPLATE, complex_context)
        assert "Alice Johnson" in result
    
    def test_loop_small(self, benchmark, simple_context):
        """Benchmark small loop iteration."""
        template = "{% for item in items %}{{ item }}{% endfor %}"
        result = benchmark(self.engine.render, template, simple_context)
        assert "apple" in result
    
    def test_loop_large(self, benchmark, large_list_context):
        """Benchmark large loop (1000 items)."""
        result = benchmark(self.engine.render, LOOP_TEMPLATE, large_list_context)
        assert "Item 0" in result
    
    def test_conditionals(self, benchmark, complex_context):
        """Benchmark conditional statements."""
        result = benchmark(self.engine.render, CONDITIONAL_TEMPLATE, complex_context)
        assert "Welcome" in result
    
    def test_filters(self, benchmark, complex_context):
        """Benchmark filter applications."""
        result = benchmark(self.engine.render, FILTER_TEMPLATE, complex_context)
        assert "ALICE JOHNSON" in result
    
    def test_table_rendering(self, benchmark, complex_context):
        """Benchmark complex table rendering (100 rows)."""
        result = benchmark(self.engine.render, TABLE_TEMPLATE, complex_context)
        assert "<table>" in result
    
    def test_macros(self, benchmark):
        """Benchmark macro calls."""
        result = benchmark(self.engine.render, MACRO_TEMPLATE, {})
        assert "btn-primary" in result
    
    def test_inheritance(self, benchmark):
        """Benchmark template inheritance."""
        context = {"page_title": "Test Page", "heading": "Hello", "content": "World"}
        result = benchmark(self.engine.render_with_inheritance, context)
        assert "Test Page" in result


# Jinja2 Benchmarks
@pytest.mark.skipif(not HAS_JINJA2, reason="Jinja2 not installed")
class TestJinja2Benchmarks:
    """Jinja2 rendering benchmarks for comparison."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.engine = Jinja2Engine()
    
    def test_simple_render(self, benchmark, simple_context):
        """Benchmark simple variable substitution."""
        result = benchmark(self.engine.render, SIMPLE_TEMPLATE, simple_context)
        assert "Hello, World!" in result
    
    def test_variable_access(self, benchmark, complex_context):
        """Benchmark nested variable access."""
        result = benchmark(self.engine.render, VARIABLE_ACCESS_TEMPLATE, complex_context)
        assert "Alice Johnson" in result
    
    def test_loop_small(self, benchmark, simple_context):
        """Benchmark small loop iteration."""
        template = "{% for item in items %}{{ item }}{% endfor %}"
        result = benchmark(self.engine.render, template, simple_context)
        assert "apple" in result
    
    def test_loop_large(self, benchmark, large_list_context):
        """Benchmark large loop (1000 items)."""
        result = benchmark(self.engine.render, LOOP_TEMPLATE, large_list_context)
        assert "Item 0" in result
    
    def test_conditionals(self, benchmark, complex_context):
        """Benchmark conditional statements."""
        result = benchmark(self.engine.render, CONDITIONAL_TEMPLATE, complex_context)
        assert "Welcome" in result
    
    def test_filters(self, benchmark, complex_context):
        """Benchmark filter applications."""
        result = benchmark(self.engine.render, FILTER_TEMPLATE, complex_context)
        assert "ALICE JOHNSON" in result
    
    def test_table_rendering(self, benchmark, complex_context):
        """Benchmark complex table rendering (100 rows)."""
        result = benchmark(self.engine.render, TABLE_TEMPLATE, complex_context)
        assert "<table>" in result
    
    def test_macros(self, benchmark):
        """Benchmark macro calls."""
        result = benchmark(self.engine.render, MACRO_TEMPLATE, {})
        assert "btn-primary" in result
    
    def test_inheritance(self, benchmark):
        """Benchmark template inheritance."""
        context = {"page_title": "Test Page", "heading": "Hello", "content": "World"}
        result = benchmark(self.engine.render_with_inheritance, context)
        assert "Test Page" in result


# JSON Serialization Benchmarks
class TestJSONBenchmarks:
    """Benchmarks for JSON serialization performance."""
    
    @pytest.fixture
    def json_context(self):
        return {
            "data": [
                {"id": i, "name": f"Object {i}", "values": list(range(10))}
                for i in range(100)
            ],
        }
    
    def test_minijinja_tojson(self, benchmark, json_context):
        """Benchmark MiniJinja tojson filter."""
        env = fluxa.Environment()
        template = "{{ data|tojson }}"
        result = benchmark(env.render_str, template, **json_context)
        assert "[" in result
    
    @pytest.mark.skipif(not HAS_JINJA2, reason="Jinja2 not installed")
    def test_jinja2_tojson(self, benchmark, json_context):
        """Benchmark Jinja2 tojson filter."""
        env = jinja2.Environment()
        template = env.from_string("{{ data|tojson }}")
        result = benchmark(template.render, **json_context)
        assert "[" in result


# Compilation Benchmarks
class TestCompilationBenchmarks:
    """Benchmarks for template compilation/parsing performance."""
    
    def test_minijinja_compile(self, benchmark):
        """Benchmark MiniJinja template compilation."""
        env = fluxa.Environment()
        counter = [0]
        def compile_template():
            counter[0] += 1
            name = f"test_{counter[0]}"
            env.add_template(name, TABLE_TEMPLATE)
            return env.render_template(name)
        result = benchmark(compile_template)
        assert result is not None
    
    @pytest.mark.skipif(not HAS_JINJA2, reason="Jinja2 not installed")
    def test_jinja2_compile(self, benchmark):
        """Benchmark Jinja2 template compilation."""
        env = jinja2.Environment()
        def compile_template():
            return env.from_string(TABLE_TEMPLATE)
        result = benchmark(compile_template)
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-autosave"])
