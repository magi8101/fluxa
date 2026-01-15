"""Tests for Phase 10 Jinja2 feature parity."""

import pytest
import fluxa
from fluxa import (
    SandboxedEnvironment,
    SecurityError,
    AsyncEnvironment,
    install_gettext_translations,
    install_null_translations,
    install_debug,
    create_debug_function,
)


# =============================================================================
# SANDBOX TESTS
# =============================================================================

class TestSandboxEnvironment:
    """Test sandboxed environment security features."""
    
    def test_basic_rendering_works(self):
        """Normal rendering should work in sandbox."""
        env = SandboxedEnvironment()
        result = env.render_str("Hello {{ name }}!", name="World")
        assert result == "Hello World!"
    
    def test_dict_access_works(self):
        """Dict attribute access should work."""
        env = SandboxedEnvironment()
        result = env.render_str("{{ user.name }}", user={"name": "Alice"})
        assert result == "Alice"
    
    def test_blocks_dunder_class(self):
        """Should block __class__ access at Rust VM level."""
        env = SandboxedEnvironment()
        with pytest.raises(fluxa.TemplateError, match="blocked by sandbox"):
            env.render_str("{{ ''.__class__ }}")
    
    def test_blocks_private_attrs(self):
        """Should block access to _private attributes."""
        env = SandboxedEnvironment()
        with pytest.raises(fluxa.TemplateError, match="blocked by sandbox"):
            env.render_str("{{ obj._secret }}", obj={"_secret": "password", "name": "test"})
    
    def test_safe_object_access(self):
        """Safe object access should work."""
        env = SandboxedEnvironment()
        
        class User:
            def __init__(self):
                self.name = "Bob"
                self.age = 30
        
        result = env.render_str("{{ user.name }} is {{ user.age }}", user=User())
        assert result == "Bob is 30"
    
    def test_blocks_dunder_mro(self):
        """Should block __mro__ access on string literal."""
        env = SandboxedEnvironment()
        with pytest.raises(fluxa.TemplateError, match="blocked by sandbox"):
            env.render_str("{{ ''.__class__.__mro__ }}")


# =============================================================================
# ASYNC TESTS (require pytest-asyncio)
# =============================================================================

class TestAsyncEnvironment:
    """Test async environment wrapper."""
    
    def test_sync_methods_work(self):
        """Synchronous methods should work."""
        env = AsyncEnvironment()
        env.add_template("test", "{{ x }}")
        env.add_function("double", lambda x: x * 2)
        env.add_filter("triple", lambda x: x * 3)
    
    def test_env_property(self):
        """env property should return underlying Environment."""
        env = AsyncEnvironment()
        assert hasattr(env.env, 'render_str')


# =============================================================================
# I18N TESTS
# =============================================================================

class TestI18n:
    """Test i18n/gettext support."""
    
    def test_install_null_translations(self):
        """Null translations should pass through strings."""
        env = fluxa.Environment()
        install_null_translations(env)
        
        result = env.render_str('{{ _("Hello World") }}')
        assert result == "Hello World"
    
    def test_ngettext_singular(self):
        """ngettext should return singular for n=1."""
        env = fluxa.Environment()
        install_null_translations(env)
        
        result = env.render_str('{{ ngettext("1 item", "items", 1) }}')
        assert result == "1 item"
    
    def test_ngettext_plural(self):
        """ngettext should return plural for n>1."""
        env = fluxa.Environment()
        install_null_translations(env)
        
        result = env.render_str('{{ ngettext("1 item", "items", 5) }}')
        assert result == "items"
    
    def test_pgettext(self):
        """pgettext should work with null translations."""
        env = fluxa.Environment()
        install_null_translations(env)
        
        result = env.render_str('{{ pgettext("menu", "File") }}')
        assert result == "File"
    
    def test_gettext_function(self):
        """gettext should work."""
        env = fluxa.Environment()
        install_null_translations(env)
        
        result = env.render_str('{{ gettext("Hello") }}')
        assert result == "Hello"


# =============================================================================
# DEBUG TESTS
# =============================================================================

class TestDebugFunction:
    """Test debug function."""
    
    def test_create_debug_function(self):
        """Debug function should be created."""
        debug_fn = create_debug_function()
        assert callable(debug_fn)
    
    def test_debug_function_direct_call(self):
        """Debug function should work when called directly."""
        debug_fn = create_debug_function()
        result = debug_fn(name="test", count=42)
        assert "DEBUG INFO" in result
        assert "count" in result
        assert "name" in result
    
    def test_install_debug(self):
        """install_debug should add debug function to environment."""
        env = fluxa.Environment()
        install_debug(env)
        # Function should be added (no error)
        # Note: debug() in template doesn't receive context vars automatically
        result = env.render_str("{{ debug() }}")
        assert "DEBUG INFO" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
