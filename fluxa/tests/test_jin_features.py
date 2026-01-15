"""Test cases for Jin custom features: new filters and integrations"""

import pytest
from fluxa import Environment
from fluxa._lowlevel import has_orjson, has_pydantic, orjson_dumps, orjson_loads


class TestXmlAttrFilter:
    """Tests for the xmlattr filter"""

    def test_basic_attributes(self):
        env = Environment()
        result = env.render_str("{{ d|xmlattr }}", d={"class": "btn", "id": "submit"})
        assert 'class="btn"' in result
        assert 'id="submit"' in result

    def test_autospace_default(self):
        env = Environment()
        result = env.render_str("{{ d|xmlattr }}", d={"id": "test"})
        assert result.startswith(" ")

    def test_autospace_disabled(self):
        env = Environment()
        result = env.render_str("{{ d|xmlattr(false) }}", d={"id": "test"})
        assert not result.startswith(" ")

    def test_empty_dict(self):
        env = Environment()
        result = env.render_str("{{ d|xmlattr }}", d={})
        assert result == ""

    def test_none_values_skipped(self):
        env = Environment()
        result = env.render_str("{{ d|xmlattr }}", d={"class": "btn", "disabled": None})
        assert 'class="btn"' in result
        assert "disabled" not in result

    def test_boolean_true_minimal(self):
        env = Environment()
        result = env.render_str("{{ d|xmlattr }}", d={"checked": True, "id": "cb"})
        assert "checked" in result
        assert 'id="cb"' in result

    def test_html_escaping(self):
        env = Environment()
        result = env.render_str("{{ d|xmlattr }}", d={"title": "<script>alert('xss')</script>"})
        assert "&lt;script&gt;" in result
        assert "<script>" not in result


class TestWordCountFilter:
    """Tests for the wordcount filter"""

    def test_basic_count(self):
        env = Environment()
        result = env.render_str("{{ s|wordcount }}", s="Hello World")
        assert result == "2"

    def test_multiple_spaces(self):
        env = Environment()
        result = env.render_str("{{ s|wordcount }}", s="Hello    World    Test")
        assert result == "3"

    def test_empty_string(self):
        env = Environment()
        result = env.render_str("{{ s|wordcount }}", s="")
        assert result == "0"

    def test_only_whitespace(self):
        env = Environment()
        result = env.render_str("{{ s|wordcount }}", s="   ")
        assert result == "0"

    def test_newlines_tabs(self):
        env = Environment()
        result = env.render_str("{{ s|wordcount }}", s="Hello\nWorld\tTest")
        assert result == "3"


class TestOrjsonIntegration:
    """Tests for orjson integration"""

    def test_orjson_available(self):
        assert has_orjson() is True

    def test_orjson_dumps_dict(self):
        data = {"name": "Alice", "age": 30}
        result = orjson_dumps(data)
        assert result is not None
        assert b'"name"' in result
        assert b'"Alice"' in result

    def test_orjson_dumps_list(self):
        data = [1, 2, 3, 4, 5]
        result = orjson_dumps(data)
        assert result == b"[1,2,3,4,5]"

    def test_orjson_loads(self):
        data = b'{"name": "Bob", "age": 25}'
        result = orjson_loads(data)
        assert result == {"name": "Bob", "age": 25}

    def test_orjson_roundtrip(self):
        original = {"nested": {"key": "value"}, "list": [1, 2, 3]}
        serialized = orjson_dumps(original)
        deserialized = orjson_loads(serialized)
        assert deserialized == original


class TestPydanticIntegration:
    """Tests for Pydantic model integration"""

    def test_pydantic_available(self):
        assert has_pydantic() is True

    def test_pydantic_model_render(self):
        from pydantic import BaseModel

        class User(BaseModel):
            name: str
            age: int

        env = Environment()
        env.add_template("test", "{{ user.name }} is {{ user.age }}")
        result = env.render_template("test", user=User(name="Alice", age=30))
        assert result == "Alice is 30"

    def test_pydantic_nested_model(self):
        from pydantic import BaseModel

        class Address(BaseModel):
            city: str
            country: str

        class Person(BaseModel):
            name: str
            address: Address

        env = Environment()
        env.add_template("test", "{{ p.name }} lives in {{ p.address.city }}")
        person = Person(name="Bob", address=Address(city="Tokyo", country="Japan"))
        result = env.render_template("test", p=person)
        assert result == "Bob lives in Tokyo"

    def test_pydantic_model_in_loop(self):
        from pydantic import BaseModel

        class Item(BaseModel):
            name: str
            price: float

        env = Environment()
        env.add_template("test", "{% for item in items %}{{ item.name }}: ${{ item.price }}{% if not loop.last %}, {% endif %}{% endfor %}")
        items = [Item(name="Apple", price=1.50), Item(name="Banana", price=0.75)]
        result = env.render_template("test", items=items)
        assert result == "Apple: $1.5, Banana: $0.75"


class TestExistingFilters:
    """Tests for existing filters still work"""

    def test_pprint_filter(self):
        env = Environment()
        result = env.render_str("{{ d|pprint }}", d={"key": "value"})
        assert "key" in result
        assert "value" in result

    def test_format_filter(self):
        env = Environment()
        result = env.render_str('{{ "%s: %d"|format("Count", 42) }}')
        assert result == "Count: 42"


class TestFilesizeformatFilter:
    """Tests for the filesizeformat filter"""

    def test_bytes(self):
        env = Environment()
        result = env.render_str("{{ 100|filesizeformat }}")
        assert "Bytes" in result

    def test_kilobytes_binary(self):
        env = Environment()
        result = env.render_str("{{ 1536|filesizeformat }}")
        # Should show around 1.5 in some unit
        assert "1.5" in result or "1536" in result

    def test_megabytes(self):
        env = Environment()
        result = env.render_str("{{ 1048576|filesizeformat }}")
        assert "1.0" in result
        assert "M" in result

    def test_gigabytes(self):
        env = Environment()
        result = env.render_str("{{ 1073741824|filesizeformat }}")
        assert "G" in result


class TestUrlizeFilter:
    """Tests for the urlize filter"""

    def test_https_url(self):
        env = Environment()
        result = env.render_str('{{ "Visit https://example.com today"|urlize }}')
        assert '<a href="https://example.com">' in result
        assert "</a>" in result

    def test_http_url(self):
        env = Environment()
        result = env.render_str('{{ "Visit http://example.com today"|urlize }}')
        assert '<a href="http://example.com">' in result

    def test_email_address(self):
        env = Environment()
        result = env.render_str('{{ "Email test@example.com now"|urlize }}')
        assert 'mailto:test@example.com' in result

    def test_no_link_plain_text(self):
        env = Environment()
        result = env.render_str('{{ "Just plain text"|urlize }}')
        assert "<a" not in result


class TestForceescapeFilter:
    """Tests for the forceescape filter"""

    def test_script_tag(self):
        env = Environment()
        result = env.render_str("{{ s|forceescape }}", s="<script>alert(1)</script>")
        assert "&lt;script&gt;" in result
        assert "<script>" not in result

    def test_quotes(self):
        env = Environment()
        result = env.render_str("{{ s|forceescape }}", s='Say "hello"')
        assert "&quot;" in result

    def test_ampersand(self):
        env = Environment()
        result = env.render_str("{{ s|forceescape }}", s="A & B")
        assert "&amp;" in result


class TestStringPercentFormat:
    """Tests for Python-style string % formatting"""

    def test_basic_string(self):
        env = Environment()
        result = env.render_str('{{ "Hello %s" % "World" }}')
        assert result == "Hello World"

    def test_multiple_args(self):
        env = Environment()
        result = env.render_str('{{ "Hello %s, you are %d years old" % ["Alice", 30] }}')
        assert result == "Hello Alice, you are 30 years old"

    def test_integer_format(self):
        env = Environment()
        result = env.render_str('{{ "Number: %d" % 42 }}')
        assert result == "Number: 42"

    def test_float_format(self):
        env = Environment()
        result = env.render_str('{{ "Float: %f" % 3.14 }}')
        assert "3.14" in result

    def test_hex_format(self):
        env = Environment()
        result = env.render_str('{{ "Hex: %x" % 255 }}')
        assert result == "Hex: ff"

    def test_numeric_modulo_still_works(self):
        env = Environment()
        result = env.render_str('{{ 10 % 3 }}')
        assert result == "1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
