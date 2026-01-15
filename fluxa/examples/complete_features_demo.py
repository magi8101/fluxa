#!/usr/bin/env python3
"""
MiniJinja Complete Features Demonstration
==========================================

This example demonstrates all the improvements and features available in
MiniJinja Python bindings, including Jinja2 compatibility features.

Run this file to see all features in action:
    python examples/complete_features_demo.py
"""

import fluxa
from fluxa import Environment


def section(title: str) -> None:
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f" {title}")
    print('='*70)


def demo_basic_rendering():
    """Basic template rendering."""
    section("1. BASIC TEMPLATE RENDERING")
    
    env = Environment()
    
    # Simple string rendering
    result = env.render_str("Hello {{ name }}!", name="World")
    print(f"Simple: {result}")
    
    # With template registration
    env.add_template("greeting", """
Dear {{ recipient.name }},

Thank you for your order #{{ order_id }}.
Your items will ship on {{ ship_date }}.

Best regards,
{{ sender }}
""".strip())
    
    result = env.render_template("greeting",
        recipient={"name": "John Doe"},
        order_id=12345,
        ship_date="January 20, 2026",
        sender="The Team"
    )
    print(f"\nNamed template:\n{result}")


def demo_filters():
    """Demonstrate all filters including new Jinja2-compatible ones."""
    section("2. FILTERS - Jinja2 Compatible")
    
    env = Environment()
    
    # xmlattr - Convert dict to XML/HTML attributes
    result = env.render_str(
        '<div{{ attrs | xmlattr }}></div>',
        attrs={"class": "container", "id": "main", "data-value": "test"}
    )
    print(f"xmlattr: {result}")
    
    # urlize - Convert URLs to clickable links
    result = env.render_str(
        '{{ text | urlize }}',
        text="Check out https://example.com for more info!"
    )
    print(f"urlize: {result}")
    
    # filesizeformat - Human-readable file sizes
    result = env.render_str(
        '{{ size | filesizeformat }}',
        size=1048576
    )
    print(f"filesizeformat: {result}")
    
    # wordcount - Count words in text
    result = env.render_str(
        '{{ text | wordcount }} words',
        text="The quick brown fox jumps over the lazy dog"
    )
    print(f"wordcount: {result}")
    
    # truncate with all parameters
    result = env.render_str(
        '{{ text | truncate(length=20) }}',
        text="This is a very long sentence that needs to be truncated"
    )
    print(f"truncate: {result}")
    
    # Other useful filters
    filters_demo = """
upper: {{ "hello" | upper }}
lower: {{ "HELLO" | lower }}
title: {{ "hello world" | title }}
capitalize: {{ "hello world" | capitalize }}
trim: "{{ "  spaced  " | trim }}"
replace: {{ "hello" | replace("l", "x") }}
reverse: {{ [1, 2, 3] | reverse | list }}
sort: {{ [3, 1, 2] | sort | list }}
first: {{ [10, 20, 30] | first }}
last: {{ [10, 20, 30] | last }}
length: {{ "hello" | length }}
default: {{ missing | default("N/A") }}
join: {{ ["a", "b", "c"] | join(", ") }}
"""
    result = env.render_str(filters_demo)
    print(f"\nOther filters:{result}")


def demo_tests():
    """Demonstrate test functions."""
    section("3. TESTS - Conditional Checks")
    
    env = Environment()
    
    tests_demo = """
{% set items = [1, 2, 3] %}
{% set name = "Alice" %}
{% set count = 0 %}
{% set func = range %}

defined: {{ name is defined }}
undefined: {{ missing is undefined }}
none: {{ none is none }}
string: {{ name is string }}
number: {{ 42 is number }}
iterable: {{ items is iterable }}
sequence: {{ items is sequence }}
mapping: {{ {"a": 1} is mapping }}
callable: {{ func is callable }}
odd: {{ 3 is odd }}
even: {{ 4 is even }}
divisibleby: {{ 10 is divisibleby(5) }}
eq: {{ 5 is eq(5) }}
ne: {{ 5 is ne(3) }}
lt: {{ 3 is lt(5) }}
gt: {{ 5 is gt(3) }}
in: {{ 2 is in([1, 2, 3]) }}
"""
    result = env.render_str(tests_demo)
    print(result)


def demo_control_structures():
    """Demonstrate control structures."""
    section("4. CONTROL STRUCTURES")
    
    env = Environment()
    
    # For loops with loop variable
    for_demo = """
{% for item in items %}
  {{ loop.index }}. {{ item.name }} - ${{ item.price }}
  {% if loop.first %}(FIRST){% endif %}
  {% if loop.last %}(LAST){% endif %}
{% endfor %}

Loop info: {{ items | length }} items total
"""
    result = env.render_str(for_demo, items=[
        {"name": "Apple", "price": 1.50},
        {"name": "Banana", "price": 0.75},
        {"name": "Cherry", "price": 3.00},
    ])
    print(f"For loop:\n{result}")
    
    # If/elif/else
    if_demo = """
{% if score >= 90 %}Grade: A
{% elif score >= 80 %}Grade: B
{% elif score >= 70 %}Grade: C
{% else %}Grade: F
{% endif %}
"""
    print("If/elif/else:")
    for score in [95, 85, 75, 50]:
        result = env.render_str(if_demo, score=score).strip()
        print(f"  Score {score}: {result}")


def demo_macros():
    """Demonstrate macro features including varargs and kwargs."""
    section("5. MACROS - Reusable Template Functions")
    
    env = Environment()
    
    macro_demo = """
{# Basic macro #}
{% macro button(text, type="primary") %}
<button class="btn btn-{{ type }}">{{ text }}</button>
{% endmacro %}

{{ button("Click Me") }}
{{ button("Submit", type="success") }}
{{ button("Cancel", type="danger") }}

{# Macro with varargs #}
{% macro list_items() %}
<ul>
{% for item in varargs %}
  <li>{{ item }}</li>
{% endfor %}
</ul>
{% endmacro %}

{{ list_items("Apple", "Banana", "Cherry") }}

{# Macro with kwargs #}
{% macro data_attrs() %}
{% for key, value in kwargs.items() %}
data-{{ key }}="{{ value }}"
{% endfor %}
{% endmacro %}

<div {{ data_attrs(id="main", action="submit", target="_blank") }}></div>
"""
    result = env.render_str(macro_demo)
    print(result)


def demo_macro_caller():
    """Demonstrate call blocks with macros."""
    section("6. MACRO CALLER - Block Content Injection")
    
    env = Environment()
    
    caller_demo = """
{% macro card(title) %}
<div class="card">
  <h2>{{ title }}</h2>
  <div class="card-body">
    {{ caller() }}
  </div>
</div>
{% endmacro %}

{% call card("Welcome") %}
  <p>This content is injected via caller()!</p>
  <p>You can put any HTML here.</p>
{% endcall %}

{% call card("Features") %}
  <ul>
    <li>Easy to use</li>
    <li>Powerful macros</li>
    <li>Jinja2 compatible</li>
  </ul>
{% endcall %}
"""
    result = env.render_str(caller_demo)
    print(result)


def demo_template_inheritance():
    """Demonstrate template inheritance."""
    section("7. TEMPLATE INHERITANCE")
    
    env = Environment()
    
    # Base template
    env.add_template("base.html", """
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Default Title{% endblock %}</title>
</head>
<body>
    <nav>{% block nav %}Home | About | Contact{% endblock %}</nav>
    <main>
        {% block content %}{% endblock %}
    </main>
    <footer>{% block footer %}Copyright 2026{% endblock %}</footer>
</body>
</html>
""".strip())
    
    # Child template
    env.add_template("page.html", """
{% extends "base.html" %}

{% block title %}{{ page_title }} - My Site{% endblock %}

{% block content %}
<h1>{{ page_title }}</h1>
<p>{{ content }}</p>
{% endblock %}
""".strip())
    
    result = env.render_template("page.html",
        page_title="Welcome",
        content="This page extends the base template!"
    )
    print(result)


def demo_sandbox_mode():
    """Demonstrate sandbox mode for secure template rendering."""
    section("8. SANDBOX MODE - Secure Template Rendering")
    
    from fluxa import SandboxedEnvironment, SecurityError
    
    env = SandboxedEnvironment()
    
    # Normal rendering works
    result = env.render_str("Hello {{ name }}!", name="World")
    print(f"Normal rendering: {result}")
    
    # Safe attribute access works
    result = env.render_str(
        "User: {{ user.name }}, Age: {{ user.age }}",
        user={"name": "Alice", "age": 30}
    )
    print(f"Safe attribute access: {result}")
    
    # Dangerous attribute access is blocked
    print("\nBlocked access attempts:")
    dangerous_templates = [
        ("__class__", "{{ ''.__class__ }}"),
        ("__mro__", "{{ ''.__class__.__mro__ }}"),
        ("_private", "{{ obj._secret }}"),
    ]
    
    for name, template in dangerous_templates:
        try:
            env.render_str(template, obj={"_secret": "password", "name": "test"})
            print(f"  {name}: NOT BLOCKED (unexpected)")
        except Exception as e:
            print(f"  {name}: BLOCKED - {type(e).__name__}")


def demo_i18n():
    """Demonstrate internationalization support."""
    section("9. I18N/GETTEXT SUPPORT")
    
    from fluxa import install_null_translations
    
    env = Environment()
    install_null_translations(env)
    
    # Using translation functions
    i18n_demo = """
Simple: {{ _("Hello, World!") }}
With variable: {{ _("Hello, %(name)s!") % {"name": user_name} }}
Singular: {{ ngettext("1 item", "%(n)s items", count) }}
Context: {{ pgettext("menu", "File") }}
"""
    
    print("Null translations (pass-through):")
    result = env.render_str(i18n_demo, user_name="Alice", count=1)
    print(result)
    
    result = env.render_str(i18n_demo, user_name="Bob", count=5)
    print(result)


def demo_async_support():
    """Demonstrate async template rendering."""
    section("10. ASYNC TEMPLATE SUPPORT")
    
    import asyncio
    from fluxa import AsyncEnvironment
    
    async def render_async():
        async with AsyncEnvironment() as env:
            env.add_template("async_demo", "Hello {{ user_name }} from async!")
            
            # Async rendering
            result = await env.render_str_async(
                "Processing {{ count }} items asynchronously...",
                count=100
            )
            print(f"Async string: {result}")
            
            result = await env.render_template_async("async_demo", user_name="World")
            print(f"Async template: {result}")
            
            # Async expression evaluation
            result = await env.eval_expr_async("a + b * c", a=10, b=5, c=3)
            print(f"Async eval: 10 + 5 * 3 = {result}")
    
    asyncio.run(render_async())


def demo_debug_function():
    """Demonstrate debug introspection."""
    section("11. DEBUG INTROSPECTION")
    
    from fluxa import install_debug
    
    env = Environment()
    install_debug(env)
    
    # Pass variables explicitly to debug() for inspection
    result = env.render_str(
        "{{ debug(user=user, items=items, count=count, active=active) }}",
        user={"name": "Alice", "role": "admin"},
        items=[1, 2, 3],
        count=42,
        active=True
    )
    print(result)


def demo_custom_functions_and_filters():
    """Demonstrate custom functions and filters."""
    section("12. CUSTOM FUNCTIONS AND FILTERS")
    
    env = Environment()
    
    # Custom function
    def format_currency(amount, symbol="$"):
        return f"{symbol}{amount:,.2f}"
    
    env.add_function("currency", format_currency)
    
    # Custom filter
    def highlight(text, word):
        return text.replace(word, f"**{word}**")
    
    env.add_filter("highlight", highlight)
    
    # Custom test
    def is_premium(user):
        return user.get("tier", "free") == "premium"
    
    env.add_test("premium", is_premium)
    
    result = env.render_str("""
Price: {{ currency(1234.56) }}
Price (EUR): {{ currency(1234.56, "EUR ") }}
Highlighted: {{ "The quick brown fox" | highlight("quick") }}
User is premium: {{ user is premium }}
""", user={"name": "Alice", "tier": "premium"})
    print(result)


def demo_expression_evaluation():
    """Demonstrate expression evaluation."""
    section("13. EXPRESSION EVALUATION")
    
    env = Environment()
    
    expressions = [
        ("1 + 2 * 3", {}),
        ("items | length", {"items": [1, 2, 3, 4, 5]}),
        ("name | upper", {"name": "alice"}),
        ("price * quantity", {"price": 9.99, "quantity": 3}),
        ("user.name ~ ' <' ~ user.email ~ '>'", {"user": {"name": "Alice", "email": "alice@example.com"}}),
    ]
    
    for expr, ctx in expressions:
        result = env.eval_expr(expr, **ctx)
        print(f"  {expr} = {result}")


def demo_error_handling():
    """Demonstrate error handling and debugging."""
    section("14. ERROR HANDLING")
    
    env = Environment()
    env.debug = True  # Enable debug mode for detailed errors
    
    print("Template with syntax error:")
    try:
        env.render_str("{% if x %}missing endif")
    except fluxa.TemplateError as e:
        print(f"  TemplateError: {e}")
    
    print("\nTemplate with undefined variable (strict mode):")
    env.undefined_behavior = "strict"
    try:
        env.render_str("Hello {{ undefined_var }}!")
    except fluxa.TemplateError as e:
        print(f"  TemplateError: {type(e).__name__}")
    
    print("\nTemplate with undefined variable (lenient mode):")
    env.undefined_behavior = "lenient"
    result = env.render_str("Hello {{ undefined_var }}!")
    print(f"  Result: '{result}'")


def demo_orjson_integration():
    """Demonstrate orjson integration for fast JSON."""
    section("15. ORJSON INTEGRATION (Fast JSON)")
    
    if fluxa.has_orjson():
        print("orjson is available!")
        
        data = {"name": "Alice", "scores": [95, 87, 92], "active": True}
        
        # Fast JSON dumps
        json_str = fluxa.orjson_dumps(data)
        print(f"orjson_dumps: {json_str}")
        
        # Fast JSON loads
        parsed = fluxa.orjson_loads(json_str)
        print(f"orjson_loads: {parsed}")
        
        print("\nNote: orjson is 7-9x faster than stdlib json!")
    else:
        print("orjson not installed. Install with: pip install orjson")


def demo_pydantic_integration():
    """Demonstrate Pydantic integration."""
    section("16. PYDANTIC INTEGRATION")
    
    if fluxa.has_pydantic():
        print("Pydantic is available!")
        
        from pydantic import BaseModel
        from typing import List
        
        class User(BaseModel):
            name: str
            email: str
            age: int
        
        class Order(BaseModel):
            id: int
            user: User
            items: List[str]
            total: float
        
        # Create Pydantic models
        user = User(name="Alice", email="alice@example.com", age=30)
        order = Order(id=1234, user=user, items=["Apple", "Banana"], total=15.99)
        
        env = Environment()
        result = env.render_str("""
Order #{{ order.id }}
Customer: {{ order.user.name }} ({{ order.user.email }})
Items: {{ order.items | join(", ") }}
Total: ${{ "%.2f" | format(order.total) }}
""", order=order)
        print(result)
        
        # Context validation
        print("Context validation with Pydantic:")
        try:
            validated = fluxa.validate_context(User, {"name": "Bob", "email": "bob@example.com", "age": 25})
            print(f"  Validated: {validated}")
        except Exception as e:
            print(f"  Validation error: {e}")
    else:
        print("Pydantic not installed. Install with: pip install pydantic")


def demo_advanced_features():
    """Demonstrate advanced features."""
    section("17. ADVANCED FEATURES")
    
    env = Environment()
    
    # Whitespace control
    print("Whitespace control:")
    ws_demo = """
{%- for i in range(3) -%}
{{ i }}
{%- endfor -%}
"""
    result = env.render_str(ws_demo)
    print(f"  Result: '{result}'")
    
    # Raw blocks
    print("\nRaw blocks (escape Jinja syntax):")
    raw_demo = """
{% raw %}
This {{ will not }} be {% processed %}
{% endraw %}
"""
    result = env.render_str(raw_demo).strip()
    print(f"  {result}")
    
    # Set variables
    print("\nSet variables:")
    set_demo = """
{% set greeting = "Hello" %}
{% set name = "World" %}
{{ greeting }}, {{ name }}!
"""
    result = env.render_str(set_demo).strip()
    print(f"  {result}")
    
    # Namespace for loop scope
    print("\nNamespace (mutable state in loops):")
    ns_demo = """
{% set ns = namespace(total=0) %}
{% for item in items %}
{% set ns.total = ns.total + item.price %}
{% endfor %}
Total: ${{ ns.total }}
"""
    result = env.render_str(ns_demo, items=[
        {"price": 10}, {"price": 20}, {"price": 30}
    ]).strip()
    print(f"  {result}")


def demo_benchmark_vs_jinja2():
    """Benchmark comparison between MiniJinja and Jinja2."""
    section("18. PERFORMANCE BENCHMARK: MiniJinja vs Jinja2")
    
    import time
    import statistics
    
    try:
        import jinja2
        has_jinja2 = True
    except ImportError:
        has_jinja2 = False
        print("Jinja2 not installed. Install with: pip install jinja2")
        return
    
    # Test templates
    templates = {
        "simple": {
            "template": "Hello {{ name }}!",
            "context": {"name": "World"},
            "iterations": 10000,
        },
        "loop_small": {
            "template": "{% for i in items %}{{ i }}{% endfor %}",
            "context": {"items": list(range(10))},
            "iterations": 5000,
        },
        "loop_large": {
            "template": "{% for i in items %}{{ i }}{% endfor %}",
            "context": {"items": list(range(100))},
            "iterations": 2000,
        },
        "nested_access": {
            "template": "{{ user.profile.name }} ({{ user.profile.email }})",
            "context": {"user": {"profile": {"name": "Alice", "email": "alice@example.com"}}},
            "iterations": 10000,
        },
        "conditionals": {
            "template": "{% if score >= 90 %}A{% elif score >= 80 %}B{% else %}C{% endif %}",
            "context": {"score": 85},
            "iterations": 10000,
        },
        "filters": {
            "template": "{{ name | upper | replace('A', 'X') }}",
            "context": {"name": "banana"},
            "iterations": 5000,
        },
        "complex_page": {
            "template": """
<!DOCTYPE html>
<html>
<head><title>{{ title }}</title></head>
<body>
<h1>{{ title }}</h1>
{% for item in items %}
<div class="item">
    <h2>{{ item.name }}</h2>
    <p>{{ item.description }}</p>
    <span>${{ item.price }}</span>
</div>
{% endfor %}
</body>
</html>
""",
            "context": {
                "title": "Products",
                "items": [
                    {"name": f"Product {i}", "description": f"Description for product {i}", "price": 9.99 + i}
                    for i in range(20)
                ]
            },
            "iterations": 1000,
        },
    }
    
    results = []
    
    for name, config in templates.items():
        template = config["template"]
        context = config["context"]
        iterations = config["iterations"]
        
        # MiniJinja
        mj_env = Environment()
        mj_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            mj_env.render_str(template, **context)
            mj_times.append(time.perf_counter() - start)
        mj_mean = statistics.mean(mj_times) * 1000
        
        # Jinja2
        j2_env = jinja2.Environment()
        j2_template = j2_env.from_string(template)
        j2_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            j2_template.render(**context)
            j2_times.append(time.perf_counter() - start)
        j2_mean = statistics.mean(j2_times) * 1000
        
        ratio = j2_mean / mj_mean if mj_mean > 0 else 0
        winner = "MiniJinja" if ratio > 1 else "Jinja2"
        
        results.append({
            "name": name,
            "mj_ms": mj_mean,
            "j2_ms": j2_mean,
            "ratio": ratio,
            "winner": winner,
        })
    
    # Print results table
    print(f"\n{'Test':<20} {'MiniJinja':>12} {'Jinja2':>12} {'Ratio':>10} {'Winner':>12}")
    print("-" * 70)
    
    for r in results:
        ratio_str = f"{r['ratio']:.2f}x" if r['ratio'] > 1 else f"{1/r['ratio']:.2f}x"
        print(f"{r['name']:<20} {r['mj_ms']:>10.4f}ms {r['j2_ms']:>10.4f}ms {ratio_str:>10} {r['winner']:>12}")
    
    # Summary
    mj_avg = statistics.mean([r["mj_ms"] for r in results])
    j2_avg = statistics.mean([r["j2_ms"] for r in results])
    overall_ratio = j2_avg / mj_avg
    
    print("-" * 70)
    print(f"{'AVERAGE':<20} {mj_avg:>10.4f}ms {j2_avg:>10.4f}ms")
    print(f"\nOverall: MiniJinja is {overall_ratio:.2f}x {'faster' if overall_ratio > 1 else 'slower'} than Jinja2")


def main():
    """Run all demonstrations."""
    print("""
    +======================================================================+
    |         MiniJinja Complete Features Demonstration                     |
    |                                                                       |
    |  This demo showcases all the improvements and features of            |
    |  MiniJinja Python bindings with Jinja2 compatibility.                |
    +======================================================================+
    """)
    
    demos = [
        demo_basic_rendering,
        demo_filters,
        demo_tests,
        demo_control_structures,
        demo_macros,
        demo_macro_caller,
        demo_template_inheritance,
        demo_sandbox_mode,
        demo_i18n,
        demo_async_support,
        demo_debug_function,
        demo_custom_functions_and_filters,
        demo_expression_evaluation,
        demo_error_handling,
        demo_orjson_integration,
        demo_pydantic_integration,
        demo_advanced_features,
        demo_benchmark_vs_jinja2,
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n[ERROR in {demo.__name__}]: {e}")
    
    print("\n" + "="*70)
    print(" DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nFor more information, see the documentation.")


if __name__ == "__main__":
    main()
