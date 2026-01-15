"""
Jinja2 Compatibility Test Suite

Tests that compare MiniJinja output against Jinja2 output to ensure compatibility.
Each test renders the same template with both engines and compares the results.

KNOWN DIFFERENCES (by design):
- Boolean output: MiniJinja uses 'true'/'false', Jinja2 uses 'True'/'False'
- List output format differs slightly
- Some edge cases in escaping

Tests marked with @pytest.mark.known_difference document these intentional divergences.
"""

import pytest
import jinja2
import fluxa


class TemplateEngines:
    """Wrapper for both template engines."""
    
    def __init__(self):
        self.jinja2_env = jinja2.Environment(autoescape=False)
        self.minijinja_env = fluxa.Environment()
    
    def render_both(self, template: str, **context):
        """Render template with both engines and return results."""
        j2_result = self.jinja2_env.from_string(template).render(**context)
        mj_result = self.minijinja_env.render_str(template, **context)
        return j2_result, mj_result
    
    def assert_equal(self, template: str, **context):
        """Assert that both engines produce the same output."""
        j2, mj = self.render_both(template, **context)
        assert j2 == mj, f"Jinja2: {j2!r}\nMiniJinja: {mj!r}"
        return j2
    
    def assert_functionally_equal(self, template: str, **context):
        """Assert functional equivalence (lowercase comparison for booleans)."""
        j2, mj = self.render_both(template, **context)
        # Normalize for boolean case difference
        j2_norm = j2.lower()
        mj_norm = mj.lower()
        assert j2_norm == mj_norm, f"Jinja2: {j2!r}\nMiniJinja: {mj!r}"
        return j2, mj


@pytest.fixture
def engines():
    return TemplateEngines()


# =============================================================================
# FILTER COMPATIBILITY TESTS - String Outputs (should match exactly)
# =============================================================================

class TestFilterCompatibilityExact:
    """Filters that should produce identical output."""
    
    def test_abs(self, engines):
        engines.assert_equal("{{ x|abs }}", x=-5)
        engines.assert_equal("{{ x|abs }}", x=5)
    
    def test_capitalize(self, engines):
        engines.assert_equal("{{ s|capitalize }}", s="hello world")
        engines.assert_equal("{{ s|capitalize }}", s="HELLO WORLD")
    
    def test_first(self, engines):
        engines.assert_equal("{{ items|first }}", items=[1, 2, 3])
        engines.assert_equal("{{ s|first }}", s="hello")
    
    def test_float(self, engines):
        engines.assert_equal("{{ x|float }}", x="3.14")
    
    def test_int(self, engines):
        engines.assert_equal("{{ x|int }}", x="42")
    
    def test_join(self, engines):
        engines.assert_equal("{{ items|join(', ') }}", items=["a", "b", "c"])
    
    def test_last(self, engines):
        engines.assert_equal("{{ items|last }}", items=[1, 2, 3])
        engines.assert_equal("{{ s|last }}", s="hello")
    
    def test_length(self, engines):
        engines.assert_equal("{{ items|length }}", items=[1, 2, 3])
        engines.assert_equal("{{ s|length }}", s="hello")
    
    def test_lower(self, engines):
        engines.assert_equal("{{ s|lower }}", s="HELLO WORLD")
    
    def test_max(self, engines):
        engines.assert_equal("{{ items|max }}", items=[1, 5, 3])
    
    def test_min(self, engines):
        engines.assert_equal("{{ items|min }}", items=[1, 5, 3])
    
    def test_replace(self, engines):
        engines.assert_equal("{{ s|replace('world', 'there') }}", s="hello world")
    
    def test_round(self, engines):
        engines.assert_equal("{{ x|round }}", x=3.7)
        engines.assert_equal("{{ x|round(2) }}", x=3.14159)
    
    def test_sum(self, engines):
        engines.assert_equal("{{ items|sum }}", items=[1, 2, 3, 4, 5])
    
    def test_title(self, engines):
        engines.assert_equal("{{ s|title }}", s="hello world")
    
    def test_trim(self, engines):
        engines.assert_equal("{{ s|trim }}", s="  hello  ")
    
    def test_upper(self, engines):
        engines.assert_equal("{{ s|upper }}", s="hello world")


# =============================================================================
# SYNTAX COMPATIBILITY TESTS - Numeric/String Outputs
# =============================================================================

class TestSyntaxCompatibilityExact:
    """Syntax features that should produce identical output."""
    
    def test_variable_output_number(self, engines):
        engines.assert_equal("{{ x }}", x=42)
    
    def test_variable_output_string(self, engines):
        engines.assert_equal("{{ x }}", x="hello")
    
    def test_attribute_access(self, engines):
        engines.assert_equal("{{ user.name }}", user={"name": "John"})
    
    def test_item_access(self, engines):
        engines.assert_equal("{{ items[0] }}", items=[1, 2, 3])
        engines.assert_equal("{{ d['key'] }}", d={"key": "value"})
    
    def test_math_operations(self, engines):
        engines.assert_equal("{{ 2 + 3 }}")
        engines.assert_equal("{{ 10 - 4 }}")
        engines.assert_equal("{{ 3 * 4 }}")
        engines.assert_equal("{{ 10 // 3 }}")
        engines.assert_equal("{{ 10 % 3 }}")
    
    def test_string_concatenation(self, engines):
        engines.assert_equal("{{ 'hello' ~ ' ' ~ 'world' }}")
    
    def test_for_loop(self, engines):
        engines.assert_equal("{% for i in items %}{{ i }}{% endfor %}", items=[1, 2, 3])
    
    def test_for_loop_with_index(self, engines):
        engines.assert_equal(
            "{% for i in items %}{{ loop.index }}:{{ i }} {% endfor %}",
            items=["a", "b", "c"]
        )
    
    def test_if_statement(self, engines):
        engines.assert_equal("{% if x %}yes{% endif %}", x=True)
        engines.assert_equal("{% if x %}yes{% endif %}", x=False)
    
    def test_if_else(self, engines):
        engines.assert_equal("{% if x %}yes{% else %}no{% endif %}", x=True)
        engines.assert_equal("{% if x %}yes{% else %}no{% endif %}", x=False)
    
    def test_if_elif_else(self, engines):
        engines.assert_equal(
            "{% if x == 1 %}one{% elif x == 2 %}two{% else %}other{% endif %}",
            x=1
        )
        engines.assert_equal(
            "{% if x == 1 %}one{% elif x == 2 %}two{% else %}other{% endif %}",
            x=2
        )
    
    def test_set_statement(self, engines):
        engines.assert_equal("{% set x = 42 %}{{ x }}")
        engines.assert_equal("{% set items = [1, 2, 3] %}{{ items|sum }}")
    
    def test_filter_chaining(self, engines):
        engines.assert_equal("{{ s|upper|replace('O', '0') }}", s="hello world")
    
    def test_comments(self, engines):
        engines.assert_equal("hello{# comment #} world")
    
    def test_raw_block(self, engines):
        engines.assert_equal("{% raw %}{{ this is not a variable }}{% endraw %}")


# =============================================================================
# MACRO COMPATIBILITY TESTS
# =============================================================================

class TestMacroCompatibility:
    """Macro tests that should produce identical output."""
    
    def test_simple_macro(self, engines):
        engines.assert_equal(
            "{% macro greet(name) %}Hello, {{ name }}!{% endmacro %}{{ greet('World') }}"
        )
    
    def test_macro_with_default(self, engines):
        engines.assert_equal(
            "{% macro greet(name='World') %}Hello, {{ name }}!{% endmacro %}{{ greet() }}"
        )
    
    def test_macro_with_multiple_args(self, engines):
        engines.assert_equal(
            "{% macro add(a, b) %}{{ a + b }}{% endmacro %}{{ add(2, 3) }}"
        )


# =============================================================================
# EDGE CASE TESTS - String Outputs
# =============================================================================

class TestEdgeCasesExact:
    """Edge cases that should produce identical output."""
    
    def test_empty_string(self, engines):
        engines.assert_equal("{{ s }}", s="")
    
    def test_zero_values(self, engines):
        engines.assert_equal("{{ x }}", x=0)
    
    def test_empty_list_loop(self, engines):
        engines.assert_equal("{% for i in items %}{{ i }}{% endfor %}", items=[])
    
    def test_nested_dict_access(self, engines):
        engines.assert_equal(
            "{{ user.address.city }}",
            user={"address": {"city": "NYC"}}
        )
    
    def test_list_of_dicts(self, engines):
        engines.assert_equal(
            "{% for u in users %}{{ u.name }} {% endfor %}",
            users=[{"name": "Alice"}, {"name": "Bob"}]
        )
    
    def test_whitespace_control(self, engines):
        engines.assert_equal("{%- if true -%}hello{%- endif -%}")


# =============================================================================
# KNOWN DIFFERENCES - Tests that document intentional divergences
# =============================================================================

class TestKnownDifferences:
    """
    Document known differences between MiniJinja and Jinja2.
    These tests verify that MiniJinja works correctly but differently.
    """
    
    def test_boolean_output_difference(self, engines):
        """MiniJinja outputs 'true'/'false', Jinja2 outputs 'True'/'False'."""
        j2, mj = engines.render_both("{{ x }}", x=True)
        assert j2 == "True"
        assert mj == "true"
    
    def test_comparison_output_difference(self, engines):
        """Boolean comparison results also differ in case."""
        j2, mj = engines.render_both("{{ 3 < 5 }}")
        assert j2 == "True"
        assert mj == "true"
    
    def test_test_output_difference(self, engines):
        """Test results are booleans and differ in case."""
        j2, mj = engines.render_both("{{ x is defined }}", x=42)
        assert j2 == "True"
        assert mj == "true"
    
    def test_list_output_format(self, engines):
        """List output format may differ slightly."""
        j2, mj = engines.render_both("{{ items }}", items=[1, 2, 3])
        # Both should produce valid list representations
        assert "1" in j2 and "2" in j2 and "3" in j2
        assert "1" in mj and "2" in mj and "3" in mj


# =============================================================================
# FUNCTIONAL EQUIVALENCE TESTS
# =============================================================================

class TestFunctionalEquivalence:
    """
    Tests that verify functional equivalence even when output differs.
    These normalize outputs before comparison.
    """
    
    def test_boolean_tests_functional(self, engines):
        """Boolean tests work correctly despite case differences."""
        # All these should work functionally the same
        engines.assert_functionally_equal("{{ x is defined }}", x=42)
        engines.assert_functionally_equal("{{ x is none }}", x=None)
        engines.assert_functionally_equal("{{ x is odd }}", x=3)
        engines.assert_functionally_equal("{{ x is even }}", x=4)
    
    def test_comparisons_functional(self, engines):
        """Comparisons work correctly despite case differences."""
        engines.assert_functionally_equal("{{ 3 < 5 }}")
        engines.assert_functionally_equal("{{ 3 > 5 }}")
        engines.assert_functionally_equal("{{ 3 == 3 }}")
    
    def test_logic_functional(self, engines):
        """Logic operators work correctly despite case differences."""
        engines.assert_functionally_equal("{{ true and false }}")
        engines.assert_functionally_equal("{{ true or false }}")


# =============================================================================
# SPEED COMPARISON TESTS
# =============================================================================

class TestSpeedComparison:
    """
    Compare rendering speed between MiniJinja and Jinja2.
    MiniJinja is typically 3-65x faster due to Rust implementation.
    """
    
    def test_simple_render_speed(self, engines):
        """MiniJinja should be faster for simple templates."""
        import time
        template = "Hello, {{ name }}! You have {{ count }} messages."
        context = {"name": "World", "count": 42}
        iterations = 1000
        
        # Jinja2
        j2_start = time.perf_counter()
        for _ in range(iterations):
            engines.jinja2_env.from_string(template).render(**context)
        j2_time = time.perf_counter() - j2_start
        
        # MiniJinja
        mj_start = time.perf_counter()
        for _ in range(iterations):
            engines.minijinja_env.render_str(template, **context)
        mj_time = time.perf_counter() - mj_start
        
        speedup = j2_time / mj_time
        print(f"\nSimple render: Jinja2={j2_time:.4f}s, MiniJinja={mj_time:.4f}s, speedup={speedup:.1f}x")
        # MiniJinja should be faster (speedup > 1)
        assert speedup > 1, f"Expected MiniJinja to be faster, got {speedup:.2f}x"
    
    def test_loop_render_speed(self, engines):
        """MiniJinja should be faster for loop-heavy templates."""
        import time
        template = "{% for i in items %}{{ i }}{% endfor %}"
        context = {"items": list(range(100))}
        iterations = 500
        
        # Jinja2
        j2_start = time.perf_counter()
        for _ in range(iterations):
            engines.jinja2_env.from_string(template).render(**context)
        j2_time = time.perf_counter() - j2_start
        
        # MiniJinja
        mj_start = time.perf_counter()
        for _ in range(iterations):
            engines.minijinja_env.render_str(template, **context)
        mj_time = time.perf_counter() - mj_start
        
        speedup = j2_time / mj_time
        print(f"\nLoop render: Jinja2={j2_time:.4f}s, MiniJinja={mj_time:.4f}s, speedup={speedup:.1f}x")
        assert speedup > 1, f"Expected MiniJinja to be faster, got {speedup:.2f}x"
    
    def test_filter_chain_speed(self, engines):
        """MiniJinja should be faster for filter chains."""
        import time
        template = "{{ text|upper|replace('O', '0')|trim }}"
        context = {"text": "  hello world  "}
        iterations = 1000
        
        # Jinja2
        j2_start = time.perf_counter()
        for _ in range(iterations):
            engines.jinja2_env.from_string(template).render(**context)
        j2_time = time.perf_counter() - j2_start
        
        # MiniJinja
        mj_start = time.perf_counter()
        for _ in range(iterations):
            engines.minijinja_env.render_str(template, **context)
        mj_time = time.perf_counter() - mj_start
        
        speedup = j2_time / mj_time
        print(f"\nFilter chain: Jinja2={j2_time:.4f}s, MiniJinja={mj_time:.4f}s, speedup={speedup:.1f}x")
        assert speedup > 1, f"Expected MiniJinja to be faster, got {speedup:.2f}x"


# =============================================================================
# MINIJINJA-EXCLUSIVE FEATURES (Not available in Jinja2)
# =============================================================================

class TestMiniJinjaExclusiveFeatures:
    """
    Features available in MiniJinja but NOT in Jinja2.
    These tests demonstrate MiniJinja's extended capabilities.
    """
    
    def test_pydantic_integration_not_in_jinja2(self):
        """MiniJinja has native Pydantic support - Jinja2 does not."""
        # MiniJinja has these features
        assert hasattr(fluxa, 'has_pydantic')
        assert hasattr(fluxa, 'validate_context')
        
        # Jinja2 does NOT have these
        assert not hasattr(jinja2, 'has_pydantic')
        assert not hasattr(jinja2, 'validate_context')
        
        # Test MiniJinja's Pydantic support works
        if fluxa.has_pydantic():
            from pydantic import BaseModel
            
            class UserContext(BaseModel):
                name: str
                age: int
            
            # Validate context before rendering
            validated = fluxa.validate_context(UserContext, {"name": "John", "age": 30})
            assert validated.name == "John"
            assert validated.age == 30
    
    def test_orjson_integration_not_in_jinja2(self):
        """MiniJinja has optional orjson integration - Jinja2 does not."""
        # MiniJinja has this feature
        assert hasattr(fluxa, 'has_orjson')
        
        # Jinja2 does NOT have this
        assert not hasattr(jinja2, 'has_orjson')
        
        # Test MiniJinja's orjson detection
        orjson_available = fluxa.has_orjson()
        assert isinstance(orjson_available, bool)
    
    def test_rust_performance_advantage(self, engines):
        """MiniJinja is written in Rust, giving it a performance advantage."""
        import time
        # Complex template with multiple features
        template = """
        {% for user in users %}
        {{ user.name|upper }}: {{ user.score|round(2) }}
        {% endfor %}
        """
        context = {
            "users": [
                {"name": f"user{i}", "score": i * 1.5}
                for i in range(50)
            ]
        }
        
        # Jinja2
        j2_start = time.perf_counter()
        for _ in range(100):
            engines.jinja2_env.from_string(template).render(**context)
        j2_time = time.perf_counter() - j2_start
        
        # MiniJinja
        mj_start = time.perf_counter()
        for _ in range(100):
            engines.minijinja_env.render_str(template, **context)
        mj_time = time.perf_counter() - mj_start
        
        speedup = j2_time / mj_time
        print(f"\nComplex template: Jinja2={j2_time:.4f}s, MiniJinja={mj_time:.4f}s, speedup={speedup:.1f}x")
        # MiniJinja's Rust core provides significant speedup
        assert speedup > 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
