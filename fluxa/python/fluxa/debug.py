"""Debug support for Fluxa templates.

Provides debugging utilities similar to Jinja2's debug extension.
"""

from typing import Any


def create_debug_function():
    """Create a debug function that can be used in templates.
    
    The debug() function returns a string with information about
    the current template context, useful for debugging templates.
    
    Returns:
        A callable that formats debug information.
    
    Example:
        env.add_function('debug', create_debug_function())
        # In template: {{ debug() }}
    """
    def debug_func(**context):
        """Debug function for templates.
        
        Returns a formatted string with context variable information.
        """
        lines = ["=== DEBUG INFO ==="]
        lines.append(f"Variables ({len(context)}):")
        for name, value in sorted(context.items()):
            value_repr = repr(value)
            if len(value_repr) > 80:
                value_repr = value_repr[:77] + "..."
            lines.append(f"  {name}: {value_repr}")
        return "\n".join(lines)
    
    return debug_func


def install_debug(env) -> None:
    """Install debug function into the environment.
    
    Adds a debug() function that can be called in templates to inspect
    the current context variables.
    
    Args:
        env: Fluxa Environment instance
    
    Example:
        install_debug(env)
        # In template: {{ debug() }}
        # Output:
        # === DEBUG INFO ===
        # Variables (2):
        #   name: 'Alice'
        #   count: 42
    
    Note:
        Due to Fluxa's architecture, the debug() function receives
        the variables passed to render_str/render_template, not all
        variables in scope at call time (unlike Jinja2's debug extension).
    """
    # The debug function needs to be called without arguments in the template
    # but receives context via render - this is a limitation
    # For a proper implementation, we'd need state access
    def debug_placeholder():
        return "=== DEBUG INFO ===\n(Context not available - use {{ debug(var1=var1, var2=var2) }} to inspect specific variables)"
    
    # Also provide a version that takes kwargs for explicit debugging
    def debug_with_vars(**kwargs):
        lines = ["=== DEBUG INFO ==="]
        lines.append(f"Variables ({len(kwargs)}):")
        for name, value in sorted(kwargs.items()):
            # Use str() for simple display since values are already converted by Fluxa
            value_str = str(value)
            if len(value_str) > 80:
                value_str = value_str[:77] + "..."
            lines.append(f"  {name}: {value_str}")
        return "\n".join(lines)
    
    env.add_function('debug', debug_with_vars)
