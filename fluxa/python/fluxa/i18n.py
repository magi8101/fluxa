"""Internationalization support for Fluxa templates.

Provides gettext integration for template translations.
"""

from typing import Any, Callable, Protocol, runtime_checkable


@runtime_checkable
class Translations(Protocol):
    """Protocol for translation objects (compatible with gettext)."""
    
    def gettext(self, message: str) -> str:
        """Translate a message."""
        ...
    
    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """Translate with plural forms."""
        ...


def install_gettext_translations(env, translations: Translations) -> None:
    """Install gettext translation functions into the environment.
    
    This adds the following functions to templates:
    - gettext(message) - translate a message
    - ngettext(singular, plural, n) - translate with plural forms
    - _(message) - alias for gettext
    - pgettext(context, message) - context-aware translation (if available)
    - npgettext(context, singular, plural, n) - context-aware plural (if available)
    
    Args:
        env: Fluxa Environment instance
        translations: A translations object with gettext/ngettext methods.
                     Typically from gettext.translation() or babel.
    
    Example:
        import gettext
        trans = gettext.translation('messages', 'locale', ['es'])
        install_gettext_translations(env, trans)
        
        # In template: {{ _("Hello") }} or {{ gettext("Hello") }}
        # For plurals: {{ ngettext("1 item", "%(n)s items", count) }}
    """
    env.add_function('gettext', translations.gettext)
    env.add_function('ngettext', translations.ngettext)
    env.add_function('_', translations.gettext)
    
    # Optional context-aware translations (pgettext/npgettext)
    if hasattr(translations, 'pgettext'):
        env.add_function('pgettext', translations.pgettext)
    if hasattr(translations, 'npgettext'):
        env.add_function('npgettext', translations.npgettext)


def install_null_translations(env) -> None:
    """Install no-op translation functions.
    
    Useful when translations are not needed but templates use i18n functions.
    All translation functions will return the input string unchanged.
    
    Args:
        env: Fluxa Environment instance
    
    Example:
        install_null_translations(env)
        # {{ _("Hello") }} will output "Hello"
    """
    env.add_function('gettext', lambda s: s)
    env.add_function('ngettext', lambda s, p, n: s if n == 1 else p)
    env.add_function('_', lambda s: s)
    env.add_function('pgettext', lambda ctx, s: s)
    env.add_function('npgettext', lambda ctx, s, p, n: s if n == 1 else p)


def extract_translations(env, template_source: str) -> list:
    """Extract translatable strings from a template.
    
    Scans template source for gettext/_/ngettext calls and returns
    the string arguments. Useful for generating .pot files.
    
    Args:
        env: Fluxa Environment instance
        template_source: Template source string
        
    Returns:
        List of (lineno, funcname, message) tuples
    
    Note:
        This is a basic implementation. For production use,
        consider using Babel's extract functionality.
    """
    import re
    
    results = []
    
    # Pattern for _("..."), gettext("..."), ngettext("...", "...", n)
    patterns = [
        (r'\{\{\s*_\s*\(\s*["\']([^"\']+)["\']\s*\)', '_'),
        (r'\{\{\s*gettext\s*\(\s*["\']([^"\']+)["\']\s*\)', 'gettext'),
        (r'\{\{\s*ngettext\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*,', 'ngettext'),
    ]
    
    lines = template_source.split('\n')
    for lineno, line in enumerate(lines, 1):
        for pattern, funcname in patterns:
            for match in re.finditer(pattern, line):
                if funcname == 'ngettext':
                    results.append((lineno, funcname, (match.group(1), match.group(2))))
                else:
                    results.append((lineno, funcname, match.group(1)))
    
    return results
