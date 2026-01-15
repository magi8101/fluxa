"""
Real-world HTML template benchmarks using production-style templates.

These benchmarks test rendering of complete HTML pages with:
- Template inheritance
- Complex loops and conditionals
- Filters and formatting
- JSON embedding
- Real-world data structures
"""

import pytest
import os
from pathlib import Path
from typing import Any

import fluxa

try:
    import jinja2
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False


TEMPLATE_DIR = Path(__file__).parent / "templates"


def load_template(name: str) -> str:
    """Load a template file from the templates directory."""
    template_path = TEMPLATE_DIR / name
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


# Load templates at module level for performance
BASE_TEMPLATE = load_template("base.html")
PRODUCTS_TEMPLATE = load_template("products.html")
DASHBOARD_TEMPLATE = load_template("dashboard.html")


def generate_nav_items() -> list[dict]:
    """Generate navigation menu items."""
    return [
        {"label": "Home", "url": "/", "active": False, "children": None},
        {"label": "Products", "url": "/products", "active": True, "children": [
            {"label": "Electronics", "url": "/products/electronics"},
            {"label": "Clothing", "url": "/products/clothing"},
            {"label": "Books", "url": "/products/books"},
        ]},
        {"label": "About", "url": "/about", "active": False, "children": None},
        {"label": "Contact", "url": "/contact", "active": False, "children": None},
    ]


def generate_products(count: int = 50) -> list[dict]:
    """Generate product data for testing."""
    categories = ["Electronics", "Clothing", "Books", "Home & Garden", "Sports"]
    return [
        {
            "id": i,
            "name": f"Premium Product {i}",
            "slug": f"premium-product-{i}",
            "category": categories[i % len(categories)],
            "price": 19.99 + (i * 2.5),
            "original_price": 29.99 + (i * 2.5) if i % 3 == 0 else 19.99 + (i * 2.5),
            "discount_percent": 33 if i % 3 == 0 else 0,
            "in_stock": i % 5 != 0,
            "rating": 3.5 + (i % 3) * 0.5,
            "review_count": 10 + (i * 3),
            "image_url": f"/images/products/{i}.jpg",
        }
        for i in range(1, count + 1)
    ]


def generate_orders(count: int = 10) -> list[dict]:
    """Generate order data for dashboard."""
    statuses = ["Pending", "Processing", "Shipped", "Delivered"]
    return [
        {
            "id": 1000 + i,
            "customer": {
                "name": f"Customer {i}",
                "avatar": f"/avatars/{i}.jpg",
            },
            "order_items": [{"id": j, "name": f"Item {j}"} for j in range(1, (i % 5) + 2)],
            "total": 49.99 + (i * 25.5),
            "status": statuses[i % len(statuses)],
            "created_at": f"2026-01-{(i % 28) + 1:02d}",
        }
        for i in range(1, count + 1)
    ]


def generate_activities(count: int = 8) -> list[dict]:
    """Generate activity feed data."""
    actions = [
        ("placed an order", "Order #"),
        ("left a review on", "Product"),
        ("updated", "Settings"),
        ("added", "to wishlist"),
    ]
    return [
        {
            "user": f"User{i}",
            "action": actions[i % len(actions)][0],
            "target": f"{actions[i % len(actions)][1]}{i}",
            "target_url": f"/item/{i}",
            "icon": ["📦", "⭐", "⚙️", "❤️"][i % 4],
            "type": ["order", "review", "settings", "wishlist"][i % 4],
            "time_ago": f"{i * 5} minutes ago",
        }
        for i in range(1, count + 1)
    ]


def generate_stats() -> list[dict]:
    """Generate dashboard statistics."""
    return [
        {"label": "Total Revenue", "value": 125430.50, "format": "currency", "icon": "💰", "type": "revenue", "change": 12.5},
        {"label": "Orders", "value": 1847, "format": "number", "icon": "📦", "type": "orders", "change": 8.2},
        {"label": "Customers", "value": 3241, "format": "number", "icon": "👥", "type": "customers", "change": -2.1},
        {"label": "Conversion Rate", "value": 3.42, "format": "percent", "icon": "📈", "type": "conversion", "change": 0.8},
    ]


@pytest.fixture
def base_context() -> dict[str, Any]:
    """Base context for all templates."""
    return {
        "site_name": "BenchMark Store",
        "site_description": "Your one-stop shop for everything",
        "nav_items": generate_nav_items(),
        "user": {"name": "John Doe", "avatar_url": "/avatars/john.jpg", "role": "admin"},
        "footer_text": "Quality products since 2020",
        "footer_links": [
            {"label": "Privacy Policy", "url": "/privacy"},
            {"label": "Terms of Service", "url": "/terms"},
            {"label": "FAQ", "url": "/faq"},
        ],
        "contact_email": "support@benchmark.store",
        "contact_phone": "+1 (555) 123-4567",
        "current_year": 2026,
    }


@pytest.fixture
def products_context(base_context) -> dict[str, Any]:
    """Context for products page."""
    return {
        **base_context,
        "page_title": "All Products",
        "products": generate_products(50),
        "total_products": 247,
        "categories": [
            {"id": 1, "name": "Electronics", "count": 45},
            {"id": 2, "name": "Clothing", "count": 78},
            {"id": 3, "name": "Books", "count": 62},
            {"id": 4, "name": "Home & Garden", "count": 34},
            {"id": 5, "name": "Sports", "count": 28},
        ],
        "selected_categories": [1, 3],
        "min_price": 10,
        "max_price": 500,
        "selected_rating": 4,
        "sort": "popular",
        "current_page": 1,
        "total_pages": 5,
        "user_wishlist": [1, 5, 12, 23],
    }


@pytest.fixture
def products_large_context(base_context) -> dict[str, Any]:
    """Large context for products page with 200 products."""
    return {
        **base_context,
        "page_title": "All Products",
        "products": generate_products(200),
        "total_products": 1000,
        "categories": [
            {"id": i, "name": f"Category {i}", "count": 50 + i * 10}
            for i in range(1, 11)
        ],
        "selected_categories": [1, 3, 5],
        "min_price": 10,
        "max_price": 1000,
        "selected_rating": 3,
        "sort": "newest",
        "current_page": 3,
        "total_pages": 20,
        "user_wishlist": list(range(1, 50, 3)),
    }


@pytest.fixture
def dashboard_context(base_context) -> dict[str, Any]:
    """Context for dashboard page."""
    return {
        **base_context,
        "page_title": "Dashboard Overview",
        "dashboard_sections": [
            {
                "title": "Main",
                "menu_items": [
                    {"label": "Dashboard", "url": "/dashboard", "icon": "D", "active": True, "badge": None},
                    {"label": "Orders", "url": "/orders", "icon": "O", "active": False, "badge": 5},
                    {"label": "Products", "url": "/products", "icon": "P", "active": False, "badge": None},
                ],
            },
            {
                "title": "Reports",
                "menu_items": [
                    {"label": "Analytics", "url": "/analytics", "icon": "A", "active": False, "badge": None},
                    {"label": "Sales", "url": "/sales", "icon": "S", "active": False, "badge": None},
                ],
            },
        ],
        "search_query": "",
        "unread_notifications": 3,
        "stats": generate_stats(),
        "recent_orders": generate_orders(10),
        "activities": generate_activities(8),
        "chart_period": "month",
        "chart_data": [
            {"date": f"2026-01-{i:02d}", "value": 1000 + i * 150 + (i % 3) * 200}
            for i in range(1, 31)
        ],
        "top_products": [
            {"name": f"Top Product {i}", "image": f"/products/{i}.jpg", "sales": 500 - i * 40, "revenue": 5000 - i * 350}
            for i in range(1, 6)
        ],
    }


class TestMiniJinjaRealHTML:
    """MiniJinja benchmarks with real HTML templates."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.env = fluxa.Environment()
        self.env.add_template("base.html", BASE_TEMPLATE)
        self.env.add_template("products.html", PRODUCTS_TEMPLATE)
        self.env.add_template("dashboard.html", DASHBOARD_TEMPLATE)
    
    def test_base_template(self, benchmark, base_context):
        """Benchmark base template rendering."""
        result = benchmark(self.env.render_template, "base.html", **base_context)
        assert "<!DOCTYPE html>" in result
        assert base_context["site_name"] in result
    
    def test_products_page(self, benchmark, products_context):
        """Benchmark products listing page (50 products)."""
        result = benchmark(self.env.render_template, "products.html", **products_context)
        assert "product-card" in result
        assert "Premium Product 1" in result
    
    def test_products_page_large(self, benchmark, products_large_context):
        """Benchmark products listing page (200 products)."""
        result = benchmark(self.env.render_template, "products.html", **products_large_context)
        assert "product-card" in result
        assert "Premium Product 100" in result
    
    def test_dashboard_page(self, benchmark, dashboard_context):
        """Benchmark admin dashboard page."""
        result = benchmark(self.env.render_template, "dashboard.html", **dashboard_context)
        assert "dashboard" in result
        assert "Total Revenue" in result


@pytest.mark.skipif(not HAS_JINJA2, reason="Jinja2 not installed")
class TestJinja2RealHTML:
    """Jinja2 benchmarks with real HTML templates."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        loader = jinja2.DictLoader({
            "base.html": BASE_TEMPLATE,
            "products.html": PRODUCTS_TEMPLATE,
            "dashboard.html": DASHBOARD_TEMPLATE,
        })
        self.env = jinja2.Environment(loader=loader)
    
    def test_base_template(self, benchmark, base_context):
        """Benchmark base template rendering."""
        template = self.env.get_template("base.html")
        result = benchmark(template.render, **base_context)
        assert "<!DOCTYPE html>" in result
        assert base_context["site_name"] in result
    
    def test_products_page(self, benchmark, products_context):
        """Benchmark products listing page (50 products)."""
        template = self.env.get_template("products.html")
        result = benchmark(template.render, **products_context)
        assert "product-card" in result
        assert "Premium Product 1" in result
    
    def test_products_page_large(self, benchmark, products_large_context):
        """Benchmark products listing page (200 products)."""
        template = self.env.get_template("products.html")
        result = benchmark(template.render, **products_large_context)
        assert "product-card" in result
        assert "Premium Product 100" in result
    
    def test_dashboard_page(self, benchmark, dashboard_context):
        """Benchmark admin dashboard page."""
        template = self.env.get_template("dashboard.html")
        result = benchmark(template.render, **dashboard_context)
        assert "dashboard" in result
        assert "Total Revenue" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-columns=mean,stddev,ops"])
