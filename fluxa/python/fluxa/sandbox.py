"""Sandbox environment for running untrusted templates.

Provides a secure environment that restricts access to dangerous
Python attributes and methods.
"""

import types
from typing import Any, Dict, FrozenSet, Optional, Set, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from . import Environment


class SecurityError(Exception):
    """Raised when sandbox detects unsafe access."""
    pass


class SandboxedEnvironment:
    """Environment that restricts access to dangerous attributes.
    
    The sandbox blocks access to Python internals like __class__, __code__,
    __globals__, etc. that could be used for code injection attacks.
    
    Usage:
        env = SandboxedEnvironment()
        result = env.render_str("{{ user.name }}", user=user)
        
        # This would raise SecurityError:
        # env.render_str("{{ ''.__class__.__mro__[1] }}")
    
    Subclass and override is_safe_attribute() or is_safe_callable()
    to customize security rules.
    """
    
    # Attributes that are never safe to access
    UNSAFE_ATTRS: FrozenSet[str] = frozenset([
        # Class/type internals
        '__class__', '__subclasses__', '__mro__', '__bases__',
        # Code internals
        '__code__', '__globals__', '__builtins__', '__closure__',
        # Object internals
        '__init__', '__new__', '__del__', '__reduce__', '__reduce_ex__',
        '__getattribute__', '__setattr__', '__delattr__',
        '__dict__', '__doc__', '__module__', '__qualname__',
        # Callable internals
        '__self__', '__func__', '__wrapped__',
        # Generator/coroutine internals
        'gi_frame', 'gi_code', 'gi_yieldfrom',
        'cr_frame', 'cr_code', 'cr_origin',
        'ag_frame', 'ag_code',
        # Frame internals
        'f_globals', 'f_locals', 'f_code', 'f_builtins', 'f_back',
        # Import internals
        '__import__', '__loader__', '__spec__', '__path__', '__file__',
    ])
    
    # Types that are never safe to expose directly
    UNSAFE_TYPES: tuple = (
        type,
        types.FunctionType,
        types.MethodType,
        types.CodeType,
        types.FrameType,
        types.TracebackType,
        types.GeneratorType,
        types.CoroutineType,
        types.AsyncGeneratorType,
        types.ModuleType,
    )
    
    def __init__(self):
        """Create a sandboxed environment.
        
        The sandbox uses Rust-level attribute access blocking which intercepts
        all attribute access during template rendering, not just context values.
        """
        from . import Environment
        self._env = Environment()
        # Enable Rust-level sandbox that blocks all underscore-prefixed attributes
        self._env.enable_sandbox(True)
    
    @property
    def env(self):
        """Access underlying environment (use with caution)."""
        return self._env
    
    def is_safe_attribute(self, obj: Any, attr: str, value: Any) -> bool:
        """Check if attribute access is safe.
        
        Override this method to customize security rules.
        
        Args:
            obj: The object being accessed
            attr: The attribute name
            value: The attribute value
            
        Returns:
            True if access should be allowed
        """
        # Block all private/dunder attributes
        if attr.startswith('_'):
            return False
        
        # Block known dangerous attributes
        if attr in self.UNSAFE_ATTRS:
            return False
        
        # Block unsafe types
        if isinstance(value, self.UNSAFE_TYPES):
            return False
        
        return True
    
    def is_safe_callable(self, obj: Any) -> bool:
        """Check if callable is safe to use.
        
        Override this method to customize security rules.
        
        Args:
            obj: The callable object
            
        Returns:
            True if callable should be allowed
        """
        # Block type/class instantiation
        if isinstance(obj, type):
            return False
        
        # Allow normal functions and methods
        if isinstance(obj, (types.FunctionType, types.MethodType)):
            return True
        
        # Allow other callables (e.g., built-in functions)
        return callable(obj)
    
    def _sanitize_value(self, value: Any, depth: int = 0, seen: Optional[Set[int]] = None) -> Any:
        """Recursively sanitize a value for template use.
        
        Args:
            value: Value to sanitize
            depth: Current recursion depth
            seen: Set of seen object ids (for cycle detection)
            
        Returns:
            Sanitized value (wrapped in SafeProxy if needed)
        """
        if depth > 10:  # Prevent deep recursion
            return value
        
        if seen is None:
            seen = set()
        
        # Detect cycles
        obj_id = id(value)
        if obj_id in seen:
            return value
        seen.add(obj_id)
        
        # Block unsafe types entirely
        if isinstance(value, self.UNSAFE_TYPES):
            raise SecurityError(
                f"Access to {type(value).__name__} object is not allowed in sandbox"
            )
        
        # Recursively sanitize containers
        if isinstance(value, dict):
            return {
                k: self._sanitize_value(v, depth + 1, seen)
                for k, v in value.items()
                if not (isinstance(k, str) and k.startswith('_'))
            }
        
        if isinstance(value, list):
            return [self._sanitize_value(v, depth + 1, seen) for v in value]
        
        if isinstance(value, tuple):
            return tuple(self._sanitize_value(v, depth + 1, seen) for v in value)
        
        # Wrap objects to intercept attribute access
        if hasattr(value, '__dict__') and not isinstance(value, (str, bytes, int, float, bool, type(None))):
            return _SandboxProxy(value, self)
        
        return value
    
    def render_str(self, template: str, **context) -> str:
        """Render template with sandboxed context.
        
        Args:
            template: Template source string
            **context: Template variables
            
        Returns:
            Rendered template output
            
        Raises:
            SecurityError: If template attempts unsafe access
        """
        safe_context = {
            k: self._sanitize_value(v)
            for k, v in context.items()
            if not k.startswith('_')
        }
        return self._env.render_str(template, **safe_context)
    
    def add_template(self, name: str, source: str) -> None:
        """Add a template."""
        self._env.add_template(name, source)
    
    def render_template(self, name: str, **context) -> str:
        """Render a named template with sandboxed context."""
        safe_context = {
            k: self._sanitize_value(v)
            for k, v in context.items()
            if not k.startswith('_')
        }
        return self._env.render_template(name, **safe_context)
    
    def add_function(self, name: str, func) -> None:
        """Add a function (must be safe)."""
        if not self.is_safe_callable(func):
            raise SecurityError(f"Function '{name}' is not safe to add")
        self._env.add_function(name, func)
    
    def add_filter(self, name: str, func) -> None:
        """Add a filter (must be safe)."""
        if not self.is_safe_callable(func):
            raise SecurityError(f"Filter '{name}' is not safe to add")
        self._env.add_filter(name, func)


class _SandboxProxy:
    """Proxy object that intercepts attribute access for sandboxing."""
    
    __slots__ = ('_obj', '_sandbox')
    
    def __init__(self, obj: Any, sandbox: SandboxedEnvironment):
        object.__setattr__(self, '_obj', obj)
        object.__setattr__(self, '_sandbox', sandbox)
    
    def __getattr__(self, name: str) -> Any:
        obj = object.__getattribute__(self, '_obj')
        sandbox = object.__getattribute__(self, '_sandbox')
        
        # Block unsafe attribute names
        if name.startswith('_') or name in SandboxedEnvironment.UNSAFE_ATTRS:
            raise SecurityError(f"Access to attribute '{name}' is not allowed")
        
        try:
            value = getattr(obj, name)
        except AttributeError:
            raise AttributeError(f"'{type(obj).__name__}' has no attribute '{name}'")
        
        # Check if access is safe
        if not sandbox.is_safe_attribute(obj, name, value):
            raise SecurityError(f"Access to attribute '{name}' is not allowed")
        
        # Recursively wrap the result
        return sandbox._sanitize_value(value)
    
    def __repr__(self) -> str:
        obj = object.__getattribute__(self, '_obj')
        return f"<SandboxProxy for {type(obj).__name__}>"
    
    def __str__(self) -> str:
        obj = object.__getattribute__(self, '_obj')
        return str(obj)
