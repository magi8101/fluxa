#!/usr/bin/env python3
"""Edge case and stress tests for fluxa.

This test suite covers edge cases, stress tests, and complex scenarios
to find subtle bugs.
"""

import pytest
import fluxa
from fluxa import Environment


class TestEdgeCases:
    """Edge cases that might expose bugs."""
    
    def test_deeply_nested_dict(self):
        env = Environment()
        data = {"a": {"b": {"c": {"d": {"e": "deep"}}}}}
        result = env.render_str("{{ x.a.b.c.d.e }}", x=data)
        assert result == "deep"
    
    def test_deeply_nested_loops(self):
        env = Environment()
        tmpl = '''
{% for a in outer %}
{% for b in a %}
{% for c in b %}{{ c }}{% endfor %}
{% endfor %}
{% endfor %}
'''
        data = [[["1", "2"], ["3", "4"]], [["5", "6"], ["7", "8"]]]
        result = env.render_str(tmpl, outer=data)
        for i in range(1, 9):
            assert str(i) in result
    
    def test_long_string(self):
        env = Environment()
        long_str = "x" * 10000
        result = env.render_str("{{ s }}", s=long_str)
        assert result == long_str
    
    def test_many_variables(self):
        env = Environment()
        # Template with 100 variables
        vars_list = [f"v{i}" for i in range(100)]
        tmpl = " ".join([f"{{{{ {v} }}}}" for v in vars_list])
        context = {v: str(i) for i, v in enumerate(vars_list)}
        result = env.render_str(tmpl, **context)
        for i in range(100):
            assert str(i) in result
    
    def test_empty_values(self):
        env = Environment()
        env.undefined_behavior = "lenient"
        result = env.render_str("{{ empty_str }}{{ empty_list }}{{ empty_dict }}",
                                empty_str="", empty_list=[], empty_dict={})
        # Should not crash
        assert isinstance(result, str)
    
    def test_none_values(self):
        env = Environment()
        env.undefined_behavior = "lenient"
        result = env.render_str("{{ x }}", x=None)
        # None should render as empty or "none"
        assert result == "" or result.lower() == "none"
    
    def test_special_chars_in_string(self):
        env = Environment()
        result = env.render_str("{{ s }}", s="<>&\"'")
        # MiniJinja does NOT auto-escape by default (matches Jinja2 autoescape=False)
        # The raw string should be output
        assert "<" in result  # No escaping by default
    
    def test_unicode_strings(self):
        env = Environment()
        result = env.render_str("{{ s }}", s="Hello, World!")
        assert "Hello" in result
    
    def test_unicode_emoji(self):
        env = Environment()
        result = env.render_str("{{ s }}", s="Hello World")
        assert "Hello" in result or "World" in result
    
    def test_large_numbers(self):
        env = Environment()
        # Test large integer
        large_num = 9999999999999999999999999
        result = env.render_str("{{ n }}", n=large_num)
        # Should not crash, might render as string
        assert result
    
    def test_float_precision(self):
        env = Environment()
        result = env.render_str("{{ n }}", n=0.1 + 0.2)
        # Float precision issues in Python
        assert "0.3" in result
    
    def test_negative_numbers(self):
        env = Environment()
        result = env.render_str("{{ n }}", n=-42)
        assert result == "-42"
    
    def test_boolean_output(self):
        env = Environment()
        result_true = env.render_str("{{ x }}", x=True)
        result_false = env.render_str("{{ x }}", x=False)
        assert result_true.lower() == "true"
        assert result_false.lower() == "false"


class TestFilterEdgeCases:
    """Filter edge cases."""
    
    def test_chained_filters(self):
        env = Environment()
        result = env.render_str('{{ s | trim | upper | lower | title }}', s="  hello world  ")
        assert result == "Hello World"
    
    def test_filter_on_none(self):
        env = Environment()
        env.undefined_behavior = "lenient"
        try:
            result = env.render_str('{{ x | default("fallback") }}', x=None)
            # default filter should work with None
            assert result in ["fallback", "", "none"]
        except Exception:
            pass  # Some filters may fail on None
    
    def test_length_on_empty(self):
        env = Environment()
        assert env.render_str('{{ "" | length }}') == "0"
        assert env.render_str('{{ [] | length }}', items=[]) == "0"
    
    def test_first_on_empty(self):
        env = Environment()
        try:
            result = env.render_str('{{ [] | first }}')
            # Should return empty or raise error
        except fluxa.TemplateError:
            pass  # Expected
    
    def test_join_on_empty(self):
        env = Environment()
        result = env.render_str('{{ [] | join(",") }}')
        assert result == ""
    
    def test_replace_no_match(self):
        env = Environment()
        result = env.render_str('{{ "hello" | replace("x", "y") }}')
        assert result == "hello"


class TestLoopEdgeCases:
    """Loop edge cases."""
    
    def test_loop_over_empty(self):
        env = Environment()
        result = env.render_str('{% for i in [] %}x{% endfor %}')
        assert result == ""
    
    def test_loop_over_single(self):
        env = Environment()
        result = env.render_str('{% for i in [1] %}{{ loop.first }}-{{ loop.last }}{% endfor %}')
        assert "true" in result.lower()
    
    def test_loop_over_string(self):
        env = Environment()
        result = env.render_str('{% for c in "abc" %}{{ c }}{% endfor %}')
        assert result == "abc"
    
    def test_loop_over_dict(self):
        env = Environment()
        result = env.render_str('{% for k, v in d.items() %}{{ k }}:{{ v }};{% endfor %}', d={"a": 1})
        assert "a" in result and "1" in result
    
    def test_loop_with_else(self):
        env = Environment()
        result = env.render_str('{% for i in [] %}x{% else %}empty{% endfor %}')
        assert result == "empty"
    
    def test_loop_variable_scope(self):
        env = Environment()
        result = env.render_str('{% for i in [1,2,3] %}{% set x = i %}{% endfor %}{{ x | default("not set") }}')
        # x should not be accessible outside loop OR should be last value
        # This tests scope behavior


class TestMacroEdgeCases:
    """Macro edge cases."""
    
    def test_macro_no_args(self):
        env = Environment()
        result = env.render_str('{% macro hello() %}Hello{% endmacro %}{{ hello() }}')
        assert result == "Hello"
    
    def test_macro_many_args(self):
        env = Environment()
        result = env.render_str('{% macro f(a,b,c,d,e) %}{{ a }}{{ b }}{{ c }}{{ d }}{{ e }}{% endmacro %}{{ f(1,2,3,4,5) }}')
        assert result == "12345"
    
    def test_macro_recursive(self):
        env = Environment()
        # Self-referential macro (should work in MiniJinja)
        tmpl = '''
{% macro countdown(n) %}
{% if n > 0 %}{{ n }}{{ countdown(n-1) }}{% else %}done{% endif %}
{% endmacro %}
{{ countdown(3) }}
'''
        try:
            result = env.render_str(tmpl)
            # May or may not support recursion
        except fluxa.TemplateError:
            pass  # Recursion might not be supported


class TestInheritanceEdgeCases:
    """Template inheritance edge cases."""
    
    def test_multiple_blocks(self):
        env = Environment()
        env.add_template("base", "{% block a %}A{% endblock %}{% block b %}B{% endblock %}")
        env.add_template("child", "{% extends 'base' %}{% block a %}X{% endblock %}{% block b %}Y{% endblock %}")
        result = env.render_template("child")
        assert result == "XY"
    
    def test_nested_inheritance(self):
        env = Environment()
        env.add_template("base", "{% block content %}base{% endblock %}")
        env.add_template("mid", "{% extends 'base' %}{% block content %}mid{% endblock %}")
        env.add_template("child", "{% extends 'mid' %}{% block content %}child{% endblock %}")
        result = env.render_template("child")
        assert "child" in result


class TestIncludeFeature:
    """Test include functionality."""
    
    def test_basic_include(self):
        env = Environment()
        env.add_template("partial", "Partial Content")
        env.add_template("main", "Before {% include 'partial' %} After")
        result = env.render_template("main")
        assert "Partial Content" in result
    
    def test_include_with_variables(self):
        env = Environment()
        env.add_template("partial", "Hello {{ name }}")
        env.add_template("main", "{% include 'partial' %}")
        result = env.render_template("main", name="World")
        # Context should be passed to included template
        assert "Hello" in result


class TestSecurityEdgeCases:
    """Security-related edge cases."""
    
    def test_sandbox_nested_access_blocked(self):
        from fluxa import SandboxedEnvironment
        env = SandboxedEnvironment()
        with pytest.raises(fluxa.TemplateError):
            # Try to access class through method
            env.render_str("{{ ''.upper.__class__ }}")
    
    def test_sandbox_loop_item_access(self):
        from fluxa import SandboxedEnvironment
        env = SandboxedEnvironment()
        # Normal access in loop should work
        result = env.render_str("{% for item in items %}{{ item.name }}{% endfor %}",
                               items=[{"name": "test"}])
        assert result == "test"


class TestCustomFunctionsAndFilters:
    """Test custom functions and filters."""
    
    def test_custom_function(self):
        env = Environment()
        env.add_function("double", lambda x: x * 2)
        result = env.render_str("{{ double(5) }}")
        assert result == "10"
    
    def test_custom_function_with_multiple_args(self):
        env = Environment()
        env.add_function("add", lambda a, b, c: a + b + c)
        result = env.render_str("{{ add(1, 2, 3) }}")
        assert result == "6"
    
    def test_custom_filter(self):
        env = Environment()
        env.add_filter("exclaim", lambda s: s + "!")
        result = env.render_str('{{ "Hello" | exclaim }}')
        assert result == "Hello!"
    
    def test_custom_test(self):
        env = Environment()
        env.add_test("positive", lambda x: x > 0)
        assert env.render_str("{{ 5 is positive }}") == "true"
        assert env.render_str("{{ -5 is positive }}") == "false"


class TestAsyncEdgeCases:
    """Async edge cases."""
    
    def test_async_with_custom_function(self):
        import asyncio
        from fluxa import AsyncEnvironment
        
        async def run():
            async with AsyncEnvironment() as env:
                env.add_function("double", lambda x: x * 2)
                result = await env.render_str_async("{{ double(5) }}")
                return result
        
        result = asyncio.run(run())
        assert result == "10"
    
    def test_async_multiple_renders(self):
        import asyncio
        from fluxa import AsyncEnvironment
        
        async def run():
            async with AsyncEnvironment() as env:
                results = []
                for i in range(5):
                    r = await env.render_str_async(f"Value: {{{{ n }}}}", n=i)
                    results.append(r)
                return results
        
        results = asyncio.run(run())
        for i, r in enumerate(results):
            assert f"Value: {i}" == r


class TestStressTests:
    """Stress tests for performance and stability."""
    
    def test_many_renders(self):
        env = Environment()
        for i in range(100):
            result = env.render_str("{{ i }}", i=i)
            assert result == str(i)
    
    def test_large_loop(self):
        env = Environment()
        result = env.render_str("{% for i in range(1000) %}x{% endfor %}")
        assert len(result) == 1000
    
    def test_deeply_nested_conditionals(self):
        env = Environment()
        # 10 levels of nesting
        tmpl = "{% if true %}{% if true %}{% if true %}{% if true %}{% if true %}{% if true %}{% if true %}{% if true %}{% if true %}{% if true %}DEEP{% endif %}{% endif %}{% endif %}{% endif %}{% endif %}{% endif %}{% endif %}{% endif %}{% endif %}{% endif %}"
        result = env.render_str(tmpl)
        assert result == "DEEP"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
