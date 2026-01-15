"""
Benchmarks for orjson integration vs standard JSON serialization.

Compares:
1. orjson vs json module for Python object serialization
2. MiniJinja with orjson vs MiniJinja default tojson
3. Real-world template rendering with JSON data embedding
"""

import pytest
import json
from typing import Any

import fluxa

try:
    import orjson
    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False


def generate_test_data(size: int = 100) -> dict[str, Any]:
    """Generate test data of varying complexity."""
    return {
        "users": [
            {
                "id": i,
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "age": 20 + (i % 50),
                "active": i % 3 != 0,
                "scores": [i * 10, i * 20, i * 30],
                "metadata": {
                    "created": f"2026-01-{(i % 28) + 1:02d}",
                    "updated": f"2026-01-{(i % 28) + 1:02d}",
                    "version": i % 10,
                },
            }
            for i in range(size)
        ],
        "settings": {
            "theme": "dark",
            "language": "en",
            "notifications": {
                "email": True,
                "push": False,
                "sms": True,
            },
        },
        "metrics": {
            "total_users": size,
            "active_users": size * 2 // 3,
            "page_views": size * 1000,
        },
    }


class TestJSONSerializationBenchmarks:
    """Pure Python JSON serialization benchmarks."""
    
    @pytest.fixture
    def small_data(self):
        return generate_test_data(10)
    
    @pytest.fixture
    def medium_data(self):
        return generate_test_data(100)
    
    @pytest.fixture
    def large_data(self):
        return generate_test_data(1000)
    
    def test_json_small(self, benchmark, small_data):
        """Standard json module - small data."""
        result = benchmark(json.dumps, small_data)
        assert len(result) > 0
    
    def test_json_medium(self, benchmark, medium_data):
        """Standard json module - medium data."""
        result = benchmark(json.dumps, medium_data)
        assert len(result) > 0
    
    def test_json_large(self, benchmark, large_data):
        """Standard json module - large data."""
        result = benchmark(json.dumps, large_data)
        assert len(result) > 0
    
    @pytest.mark.skipif(not HAS_ORJSON, reason="orjson not installed")
    def test_orjson_small(self, benchmark, small_data):
        """orjson - small data."""
        result = benchmark(orjson.dumps, small_data)
        assert len(result) > 0
    
    @pytest.mark.skipif(not HAS_ORJSON, reason="orjson not installed")
    def test_orjson_medium(self, benchmark, medium_data):
        """orjson - medium data."""
        result = benchmark(orjson.dumps, medium_data)
        assert len(result) > 0
    
    @pytest.mark.skipif(not HAS_ORJSON, reason="orjson not installed")
    def test_orjson_large(self, benchmark, large_data):
        """orjson - large data."""
        result = benchmark(orjson.dumps, large_data)
        assert len(result) > 0


class TestMiniJinjaJSONBenchmarks:
    """MiniJinja template rendering with JSON embedding benchmarks."""
    
    @pytest.fixture
    def env(self):
        return fluxa.Environment()
    
    @pytest.fixture
    def small_data(self):
        return generate_test_data(10)
    
    @pytest.fixture
    def medium_data(self):
        return generate_test_data(100)
    
    @pytest.fixture
    def large_data(self):
        return generate_test_data(1000)
    
    def test_tojson_small(self, benchmark, env, small_data):
        """MiniJinja tojson filter - small data."""
        template = "var data = {{ data|tojson }};"
        result = benchmark(env.render_str, template, data=small_data)
        assert "var data = " in result
    
    def test_tojson_medium(self, benchmark, env, medium_data):
        """MiniJinja tojson filter - medium data."""
        template = "var data = {{ data|tojson }};"
        result = benchmark(env.render_str, template, data=medium_data)
        assert "var data = " in result
    
    def test_tojson_large(self, benchmark, env, large_data):
        """MiniJinja tojson filter - large data."""
        template = "var data = {{ data|tojson }};"
        result = benchmark(env.render_str, template, data=large_data)
        assert "var data = " in result
    
    def test_tojson_safe_medium(self, benchmark, env, medium_data):
        """MiniJinja tojson|safe filter chain - medium data."""
        template = "var data = {{ data|tojson|safe }};"
        result = benchmark(env.render_str, template, data=medium_data)
        assert "var data = " in result


class TestRealWorldJSONTemplates:
    """Real-world template scenarios with JSON data."""
    
    @pytest.fixture
    def api_response_template(self):
        return '''
{
    "status": "success",
    "data": {{ users|tojson }},
    "meta": {
        "total": {{ total }},
        "page": {{ page }},
        "per_page": {{ per_page }}
    }
}
'''
    
    @pytest.fixture
    def html_data_template(self):
        return '''
<!DOCTYPE html>
<html>
<head><title>Data Dashboard</title></head>
<body>
<script>
const appState = {{ state|tojson }};
const config = {{ config|tojson }};
</script>
<div id="app"></div>
</body>
</html>
'''
    
    @pytest.fixture
    def api_context(self):
        return {
            "users": generate_test_data(50)["users"],
            "total": 50,
            "page": 1,
            "per_page": 50,
        }
    
    @pytest.fixture
    def html_context(self):
        return {
            "state": generate_test_data(20),
            "config": {
                "api_url": "https://api.example.com",
                "theme": "dark",
                "features": ["charts", "tables", "filters"],
            },
        }
    
    def test_api_response(self, benchmark, api_response_template, api_context):
        """API JSON response rendering."""
        env = fluxa.Environment()
        result = benchmark(env.render_str, api_response_template, **api_context)
        assert '"status": "success"' in result
    
    def test_html_data_embedding(self, benchmark, html_data_template, html_context):
        """HTML page with embedded JSON data."""
        env = fluxa.Environment()
        result = benchmark(env.render_str, html_data_template, **html_context)
        assert "appState" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-autosave"])
