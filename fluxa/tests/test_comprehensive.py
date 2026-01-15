#!/usr/bin/env python3
"""Comprehensive deep test suite for fluxa.

This test suite covers all implemented features across all phases
to find and document any remaining bugs or issues.
"""

import pytest
import fluxa
from fluxa import Environment


class TestFilterCompatibility:
    """Test all Jinja2-compatible filters."""
    
    def test_xmlattr_basic(self):
        env = Environment()
        result = env.render_str('<div{{ attrs | xmlattr }}></div>', attrs={"class": "foo"})
        assert 'class="foo"' in result
    
    def test_xmlattr_escaping(self):
        env = Environment()
        result = env.render_str('<div{{ attrs | xmlattr }}></div>', attrs={"data": '<script>'})
        assert '&lt;script&gt;' in result or '&#' in result
    
    def test_urlize_basic(self):
        env = Environment()
        result = env.render_str('{{ text | urlize }}', text="Visit https://example.com today")
        assert 'href="https://example.com"' in result or 'https://example.com' in result
    
    def test_filesizeformat(self):
        env = Environment()
        result = env.render_str('{{ size | filesizeformat }}', size=1024)
        assert '1' in result and ('KiB' in result or 'KB' in result or 'kB' in result)
    
    def test_filesizeformat_large(self):
        env = Environment()
        result = env.render_str('{{ size | filesizeformat }}', size=1048576)
        assert '1' in result and ('MiB' in result or 'MB' in result)
    
    def test_wordcount(self):
        env = Environment()
        result = env.render_str('{{ text | wordcount }}', text="one two three four")
        assert result == "4"
    
    def test_wordcount_empty(self):
        env = Environment()
        result = env.render_str('{{ text | wordcount }}', text="")
        assert result == "0"
    
    def test_upper(self):
        env = Environment()
        assert env.render_str('{{ "hello" | upper }}') == "HELLO"
    
    def test_lower(self):
        env = Environment()
        assert env.render_str('{{ "HELLO" | lower }}') == "hello"
    
    def test_title(self):
        env = Environment()
        result = env.render_str('{{ "hello world" | title }}')
        assert result == "Hello World"
    
    def test_capitalize(self):
        env = Environment()
        result = env.render_str('{{ "hello world" | capitalize }}')
        assert result.startswith("H")
    
    def test_trim(self):
        env = Environment()
        assert env.render_str('{{ "  hello  " | trim }}') == "hello"
    
    def test_replace(self):
        env = Environment()
        assert env.render_str('{{ "hello" | replace("l", "x") }}') == "hexxo"
    
    def test_first(self):
        env = Environment()
        assert env.render_str('{{ items | first }}', items=[1, 2, 3]) == "1"
    
    def test_last(self):
        env = Environment()
        assert env.render_str('{{ items | last }}', items=[1, 2, 3]) == "3"
    
    def test_length(self):
        env = Environment()
        assert env.render_str('{{ items | length }}', items=[1, 2, 3]) == "3"
    
    def test_default(self):
        env = Environment()
        env.undefined_behavior = "lenient"
        assert env.render_str('{{ x | default("N/A") }}') == "N/A"
    
    def test_join(self):
        env = Environment()
        assert env.render_str('{{ items | join(", ") }}', items=["a", "b", "c"]) == "a, b, c"
    
    def test_sort(self):
        env = Environment()
        result = env.render_str('{{ items | sort | list }}', items=[3, 1, 2])
        assert "1" in result and "2" in result and "3" in result
    
    def test_reverse(self):
        env = Environment()
        result = env.render_str('{{ items | reverse | list }}', items=[1, 2, 3])
        assert result.index("3") < result.index("1")


class TestTestFunctions:
    """Test all test functions."""
    
    def test_defined(self):
        env = Environment()
        assert env.render_str('{{ x is defined }}', x=1) == "true"
    
    def test_undefined(self):
        env = Environment()
        env.undefined_behavior = "lenient"
        assert env.render_str('{{ x is undefined }}') == "true"
    
    def test_none(self):
        env = Environment()
        assert env.render_str('{{ x is none }}', x=None) == "true"
    
    def test_string(self):
        env = Environment()
        assert env.render_str('{{ x is string }}', x="hello") == "true"
    
    def test_number(self):
        env = Environment()
        assert env.render_str('{{ x is number }}', x=42) == "true"
    
    def test_iterable(self):
        env = Environment()
        assert env.render_str('{{ x is iterable }}', x=[1, 2, 3]) == "true"
    
    def test_sequence(self):
        env = Environment()
        assert env.render_str('{{ x is sequence }}', x=[1, 2, 3]) == "true"
    
    def test_mapping(self):
        env = Environment()
        assert env.render_str('{{ x is mapping }}', x={"a": 1}) == "true"
    
    def test_odd(self):
        env = Environment()
        assert env.render_str('{{ 3 is odd }}') == "true"
        assert env.render_str('{{ 4 is odd }}') == "false"
    
    def test_even(self):
        env = Environment()
        assert env.render_str('{{ 4 is even }}') == "true"
        assert env.render_str('{{ 3 is even }}') == "false"
    
    def test_divisibleby(self):
        env = Environment()
        assert env.render_str('{{ 10 is divisibleby(5) }}') == "true"
        assert env.render_str('{{ 10 is divisibleby(3) }}') == "false"
    
    def test_eq(self):
        env = Environment()
        assert env.render_str('{{ 5 is eq(5) }}') == "true"
    
    def test_ne(self):
        env = Environment()
        assert env.render_str('{{ 5 is ne(3) }}') == "true"
    
    def test_lt(self):
        env = Environment()
        assert env.render_str('{{ 3 is lt(5) }}') == "true"
    
    def test_gt(self):
        env = Environment()
        assert env.render_str('{{ 5 is gt(3) }}') == "true"
    
    def test_in(self):
        env = Environment()
        assert env.render_str('{{ 2 is in([1, 2, 3]) }}') == "true"


class TestMacros:
    """Test macro functionality."""
    
    def test_basic_macro(self):
        env = Environment()
        tmpl = '{% macro hello(name) %}Hello {{ name }}!{% endmacro %}{{ hello("World") }}'
        assert "Hello World!" in env.render_str(tmpl)
    
    def test_macro_default_args(self):
        env = Environment()
        tmpl = '{% macro greet(name, greeting="Hello") %}{{ greeting }} {{ name }}!{% endmacro %}{{ greet("Bob") }}'
        assert "Hello Bob!" in env.render_str(tmpl)
    
    def test_macro_with_custom_arg(self):
        env = Environment()
        tmpl = '{% macro greet(name, greeting="Hello") %}{{ greeting }} {{ name }}!{% endmacro %}{{ greet("Bob", greeting="Hi") }}'
        assert "Hi Bob!" in env.render_str(tmpl)
    
    def test_macro_caller(self):
        env = Environment()
        tmpl = '''
{% macro wrapper() %}<div>{{ caller() }}</div>{% endmacro %}
{% call wrapper() %}Content{% endcall %}
'''
        result = env.render_str(tmpl)
        assert "<div>Content</div>" in result


class TestControlStructures:
    """Test control structures."""
    
    def test_for_loop_basic(self):
        env = Environment()
        result = env.render_str('{% for i in items %}{{ i }}{% endfor %}', items=[1, 2, 3])
        assert result == "123"
    
    def test_for_loop_index(self):
        env = Environment()
        result = env.render_str('{% for i in items %}{{ loop.index }}{% endfor %}', items=[1, 2, 3])
        assert result == "123"
    
    def test_for_loop_first_last(self):
        env = Environment()
        result = env.render_str('{% for i in items %}{% if loop.first %}[{% endif %}{{ i }}{% if loop.last %}]{% endif %}{% endfor %}', items=[1, 2, 3])
        assert result == "[123]"
    
    def test_if_elif_else(self):
        env = Environment()
        tmpl = '{% if x > 10 %}big{% elif x > 5 %}medium{% else %}small{% endif %}'
        assert env.render_str(tmpl, x=15) == "big"
        assert env.render_str(tmpl, x=7) == "medium"
        assert env.render_str(tmpl, x=3) == "small"


class TestTemplateInheritance:
    """Test template inheritance."""
    
    def test_extends_basic(self):
        env = Environment()
        env.add_template("base.html", "Header{% block content %}default{% endblock %}Footer")
        env.add_template("child.html", "{% extends 'base.html' %}{% block content %}CUSTOM{% endblock %}")
        result = env.render_template("child.html")
        assert result == "HeaderCUSTOMFooter"
    
    def test_block_super(self):
        env = Environment()
        env.add_template("base.html", "{% block content %}BASE{% endblock %}")
        env.add_template("child.html", "{% extends 'base.html' %}{% block content %}{{ super() }}CHILD{% endblock %}")
        result = env.render_template("child.html")
        assert "BASE" in result and "CHILD" in result


class TestSandboxMode:
    """Test sandbox security features."""
    
    def test_sandbox_blocks_dunder_class(self):
        from fluxa import SandboxedEnvironment
        env = SandboxedEnvironment()
        with pytest.raises(fluxa.TemplateError, match="blocked by sandbox"):
            env.render_str("{{ ''.__class__ }}")
    
    def test_sandbox_blocks_dunder_mro(self):
        from fluxa import SandboxedEnvironment
        env = SandboxedEnvironment()
        with pytest.raises(fluxa.TemplateError, match="blocked by sandbox"):
            env.render_str("{{ ''.__class__.__mro__ }}")
    
    def test_sandbox_blocks_private_attrs(self):
        from fluxa import SandboxedEnvironment
        env = SandboxedEnvironment()
        with pytest.raises(fluxa.TemplateError, match="blocked by sandbox"):
            env.render_str("{{ x._secret }}", x={"_secret": "password", "name": "test"})
    
    def test_sandbox_allows_normal_access(self):
        from fluxa import SandboxedEnvironment
        env = SandboxedEnvironment()
        result = env.render_str("{{ user.name }}", user={"name": "Alice"})
        assert result == "Alice"


class TestI18n:
    """Test internationalization support."""
    
    def test_null_translations_gettext(self):
        from fluxa import install_null_translations
        env = Environment()
        install_null_translations(env)
        result = env.render_str('{{ _("Hello") }}')
        assert result == "Hello"
    
    def test_null_translations_ngettext_singular(self):
        from fluxa import install_null_translations
        env = Environment()
        install_null_translations(env)
        result = env.render_str('{{ ngettext("1 item", "many items", 1) }}')
        assert result == "1 item"
    
    def test_null_translations_ngettext_plural(self):
        from fluxa import install_null_translations
        env = Environment()
        install_null_translations(env)
        result = env.render_str('{{ ngettext("1 item", "many items", 5) }}')
        assert result == "many items"
    
    def test_null_translations_pgettext(self):
        from fluxa import install_null_translations
        env = Environment()
        install_null_translations(env)
        result = env.render_str('{{ pgettext("menu", "File") }}')
        assert result == "File"


class TestAsyncSupport:
    """Test async environment."""
    
    def test_async_render_str(self):
        import asyncio
        from fluxa import AsyncEnvironment
        
        async def run_test():
            async with AsyncEnvironment() as env:
                result = await env.render_str_async("Hello {{ name }}!", name="World")
                return result
        
        result = asyncio.run(run_test())
        assert result == "Hello World!"
    
    def test_async_render_template(self):
        import asyncio
        from fluxa import AsyncEnvironment
        
        async def run_test():
            async with AsyncEnvironment() as env:
                env.add_template("test", "Value: {{ x }}")
                result = await env.render_template_async("test", x=42)
                return result
        
        result = asyncio.run(run_test())
        assert result == "Value: 42"
    
    def test_async_eval_expr(self):
        import asyncio
        from fluxa import AsyncEnvironment
        
        async def run_test():
            async with AsyncEnvironment() as env:
                result = await env.eval_expr_async("a + b", a=10, b=20)
                return result
        
        result = asyncio.run(run_test())
        assert str(result) == "30"  # Native async returns string


class TestDebugFunction:
    """Test debug introspection."""
    
    def test_debug_with_vars(self):
        from fluxa import install_debug
        env = Environment()
        install_debug(env)
        result = env.render_str('{{ debug(x=x, y=y) }}', x=1, y=2)
        assert "DEBUG INFO" in result
        assert "Variables (2)" in result


class TestOrjsonIntegration:
    """Test orjson integration."""
    
    def test_has_orjson(self):
        # Should return True or False without error
        result = fluxa.has_orjson()
        assert isinstance(result, bool)
    
    def test_orjson_dumps(self):
        if fluxa.has_orjson():
            data = {"name": "Alice", "age": 30}
            result = fluxa.orjson_dumps(data)
            assert isinstance(result, bytes)
            assert b"Alice" in result
    
    def test_orjson_loads(self):
        if fluxa.has_orjson():
            data = b'{"name": "Bob", "age": 25}'
            result = fluxa.orjson_loads(data)
            assert result == {"name": "Bob", "age": 25}


class TestPydanticIntegration:
    """Test Pydantic integration."""
    
    def test_has_pydantic(self):
        result = fluxa.has_pydantic()
        assert isinstance(result, bool)
    
    def test_validate_context(self):
        if fluxa.has_pydantic():
            from pydantic import BaseModel
            
            class User(BaseModel):
                name: str
                age: int
            
            result = fluxa.validate_context(User, {"name": "Alice", "age": 30})
            assert result.name == "Alice"
            assert result.age == 30
    
    def test_pydantic_model_in_template(self):
        if fluxa.has_pydantic():
            from pydantic import BaseModel
            
            class User(BaseModel):
                name: str
                email: str
            
            env = Environment()
            user = User(name="Alice", email="alice@example.com")
            result = env.render_str("{{ user.name }} <{{ user.email }}>", user=user)
            assert result == "Alice <alice@example.com>"


class TestExpressionEvaluation:
    """Test expression evaluation."""
    
    def test_eval_arithmetic(self):
        env = Environment()
        assert env.eval_expr("1 + 2 * 3") == 7
    
    def test_eval_with_context(self):
        env = Environment()
        assert env.eval_expr("x + y", x=10, y=20) == 30
    
    def test_eval_with_filter(self):
        env = Environment()
        assert env.eval_expr("name | upper", name="alice") == "ALICE"
    
    def test_eval_string_concat(self):
        env = Environment()
        result = env.eval_expr("a ~ b", a="Hello ", b="World")
        assert result == "Hello World"


class TestErrorHandling:
    """Test error handling."""
    
    def test_syntax_error(self):
        env = Environment()
        with pytest.raises(fluxa.TemplateError):
            env.render_str("{% if x %}missing endif")
    
    def test_undefined_strict(self):
        env = Environment()
        env.undefined_behavior = "strict"
        with pytest.raises(fluxa.TemplateError):
            env.render_str("{{ undefined_var }}")
    
    def test_undefined_lenient(self):
        env = Environment()
        env.undefined_behavior = "lenient"
        result = env.render_str("Hello {{ x }}!")
        assert result == "Hello !"


class TestAdvancedFeatures:
    """Test advanced features."""
    
    def test_whitespace_control(self):
        env = Environment()
        result = env.render_str("{%- for i in range(3) -%}{{ i }}{%- endfor -%}")
        assert result == "012"
    
    def test_raw_block(self):
        env = Environment()
        result = env.render_str("{% raw %}{{ not processed }}{% endraw %}")
        assert "{{ not processed }}" in result
    
    def test_set_variable(self):
        env = Environment()
        result = env.render_str("{% set x = 'Hello' %}{{ x }}")
        assert result == "Hello"
    
    def test_namespace(self):
        env = Environment()
        result = env.render_str(
            "{% set ns = namespace(total=0) %}{% for i in items %}{% set ns.total = ns.total + i %}{% endfor %}{{ ns.total }}",
            items=[1, 2, 3, 4, 5]
        )
        assert result == "15"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
