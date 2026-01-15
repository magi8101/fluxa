"""Async support for Fluxa templates.

Provides native async rendering API using pyo3-async-runtimes + tokio.
No ThreadPoolExecutor - truly async from Rust.
"""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from . import Environment

# Import native async functions from lowlevel module
from ._lowlevel import (
    render_str_async as _render_str_async,
    render_template_async as _render_template_async,
    eval_expr_async as _eval_expr_async,
)


class AsyncEnvironment:
    """Async wrapper around Fluxa Environment.
    
    Provides native async rendering API using pyo3-async-runtimes with tokio.
    This is the recommended way to use Fluxa with async web frameworks
    like FastAPI, Starlette, or aiohttp.
    
    Note: This does NOT support async/await within templates themselves.
    Template rendering uses tokio::spawn_blocking for CPU-bound operations.
    
    Usage:
        env = AsyncEnvironment()
        result = await env.render_str_async("Hello {{ name }}", name="World")
        
        # With FastAPI:
        @app.get("/")
        async def home():
            return await env.render_str_async("index.html", data=data)
    """
    
    def __init__(self, **env_kwargs):
        """Create async environment.
        
        Args:
            **env_kwargs: Passed to underlying Fluxa.Environment
        """
        from . import Environment
        self._env = Environment(**env_kwargs)
    
    @property
    def env(self):
        """Access underlying synchronous environment."""
        return self._env
    
    async def render_str_async(self, template: str, **context) -> str:
        """Render template string asynchronously.
        
        Uses native Rust async with tokio spawn_blocking.
        
        Args:
            template: Template source string
            **context: Template variables
            
        Returns:
            Rendered template output
        """
        return await _render_str_async(self._env, template, **context)
    
    async def render_template_async(self, name: str, **context) -> str:
        """Render named template asynchronously.
        
        Uses native Rust async with tokio spawn_blocking.
        
        Args:
            name: Template name (must be added via add_template first)
            **context: Template variables
            
        Returns:
            Rendered template output
        """
        return await _render_template_async(self._env, name, **context)
    
    async def eval_expr_async(self, expr: str, **context) -> Any:
        """Evaluate expression asynchronously.
        
        Uses native Rust async with tokio spawn_blocking.
        
        Args:
            expr: Expression to evaluate
            **context: Variables for evaluation
            
        Returns:
            Expression result
        """
        return await _eval_expr_async(self._env, expr, **context)
    
    def add_template(self, name: str, source: str) -> None:
        """Add a template (synchronous, no I/O)."""
        self._env.add_template(name, source)
    
    def add_function(self, name: str, func) -> None:
        """Add a function to the environment."""
        self._env.add_function(name, func)
    
    def add_filter(self, name: str, func) -> None:
        """Add a filter to the environment."""
        self._env.add_filter(name, func)
    
    def add_test(self, name: str, func) -> None:
        """Add a test to the environment."""
        self._env.add_test(name, func)
    
    def add_global(self, name: str, value: Any) -> None:
        """Add a global variable to the environment."""
        self._env.add_global(name, value)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        return False

