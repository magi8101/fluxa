"""Real-world performance benchmark comparing MiniJinja and Jinja2.

This benchmark uses realistic HTML/CSS/JS templates with actual data to measure
template rendering performance in production-like scenarios.
"""

import time
import statistics
import json
from pathlib import Path
from typing import Dict, Any, List, Callable
from dataclasses import dataclass

# Template engines
import fluxa
try:
    import jinja2
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False
    print("Warning: Jinja2 not installed. Run: pip install jinja2")


@dataclass
class BenchmarkResult:
    """Results from a benchmark run."""
    name: str
    engine: str
    iterations: int
    total_time: float
    mean_time: float
    median_time: float
    min_time: float
    max_time: float
    std_dev: float
    renders_per_second: float
    
    def __str__(self) -> str:
        return (
            f"{self.engine:12} | "
            f"Mean: {self.mean_time*1000:8.3f}ms | "
            f"Median: {self.median_time*1000:8.3f}ms | "
            f"Min: {self.min_time*1000:8.3f}ms | "
            f"Max: {self.max_time*1000:8.3f}ms | "
            f"{self.renders_per_second:8.1f} renders/sec"
        )


def generate_ecommerce_data(product_count: int = 50) -> Dict[str, Any]:
    """Generate realistic e-commerce page data."""
    products = []
    for i in range(product_count):
        products.append({
            "id": i + 1,
            "name": f"Premium Product {i + 1}",
            "description": f"This is a high-quality product with excellent features. Perfect for everyday use. Made with premium materials and designed for durability. Product number {i + 1} in our collection.",
            "price": 29.99 + (i * 5.50),
            "sale_price": (19.99 + (i * 3.00)) if i % 3 == 0 else None,
            "image": f"https://example.com/images/product-{i + 1}.jpg",
            "rating": (i % 5) + 1,
            "reviews_count": 50 + (i * 10),
            "in_stock": i % 4 != 0,
        })
    
    return {
        "page_title": "Shop Our Collection",
        "site_name": "TechStore Pro",
        "site_description": "Your one-stop shop for premium technology products.",
        "theme": {
            "primary_color": "#6366f1",
            "secondary_color": "#8b5cf6",
            "background_color": "#f8fafc",
            "text_color": "#1e293b",
        },
        "nav_links": [
            {"title": "Home", "url": "/"},
            {"title": "Products", "url": "/products"},
            {"title": "Categories", "url": "/categories"},
            {"title": "Deals", "url": "/deals"},
            {"title": "About", "url": "/about"},
        ],
        "user": {"name": "John Doe", "email": "john@example.com"},
        "cart_count": 3,
        "hero_image": "https://example.com/images/hero-banner.jpg",
        "hero_title": "Summer Sale - Up to 50% Off",
        "hero_subtitle": "Discover amazing deals on our best-selling products",
        "products": products,
        "featured_categories": [
            {"name": "Electronics", "slug": "electronics", "image": "https://example.com/cat1.jpg", "product_count": 150},
            {"name": "Clothing", "slug": "clothing", "image": "https://example.com/cat2.jpg", "product_count": 320},
            {"name": "Home & Garden", "slug": "home-garden", "image": "https://example.com/cat3.jpg", "product_count": 180},
        ],
        "footer_links": [
            {"title": "Privacy Policy", "url": "/privacy"},
            {"title": "Terms of Service", "url": "/terms"},
            {"title": "Shipping Info", "url": "/shipping"},
            {"title": "Returns", "url": "/returns"},
        ],
        "contact": {
            "email": "support@techstore.com",
            "phone": "+1 (555) 123-4567",
            "address": "123 Tech Street, San Francisco, CA 94102",
        },
        "social_links": [
            {"platform": "Twitter", "url": "https://twitter.com/techstore"},
            {"platform": "Facebook", "url": "https://facebook.com/techstore"},
            {"platform": "Instagram", "url": "https://instagram.com/techstore"},
        ],
        "current_year": 2026,
    }


def generate_blog_data(comment_count: int = 20) -> Dict[str, Any]:
    """Generate realistic blog article data."""
    content_blocks = [
        {"type": "paragraph", "text": "In today's rapidly evolving technology landscape, staying ahead of the curve is more important than ever. This comprehensive guide will walk you through everything you need to know about modern web development practices."},
        {"type": "heading", "text": "Understanding the Fundamentals"},
        {"type": "paragraph", "text": "Before diving into advanced topics, it's crucial to have a solid foundation. Let's explore the core concepts that will serve as building blocks for more complex implementations."},
        {"type": "blockquote", "text": "The best code is no code at all. Every new line of code you willingly bring into the world is code that has to be debugged, code that has to be read and understood."},
        {"type": "paragraph", "text": "This principle guides our approach to software development. We focus on simplicity, maintainability, and performance above all else."},
        {"type": "heading", "text": "Practical Implementation"},
        {"type": "code", "code": "def process_data(items):\n    return [transform(item) for item in items if validate(item)]"},
        {"type": "paragraph", "text": "The above code demonstrates a clean, functional approach to data processing. Notice how we combine filtering and transformation in a single, readable expression."},
        {"type": "list", "list_items": ["Improved performance", "Better maintainability", "Reduced complexity", "Enhanced testability"]},
        {"type": "image", "url": "https://example.com/diagram.png", "caption": "System architecture overview"},
        {"type": "paragraph", "text": "As we conclude this exploration, remember that the best solutions are often the simplest ones. Keep learning, keep experimenting, and most importantly, keep building."},
    ]
    
    comments = []
    for i in range(comment_count):
        comment = {
            "id": i + 1,
            "author": f"User{i + 1}",
            "text": f"This is comment number {i + 1}. Great article, really helped me understand the concepts better. Looking forward to more content like this!",
            "created_at": f"2026-01-{(i % 28) + 1:02d} at 10:{i:02d} AM",
            "replies": [],
        }
        if i % 5 == 0 and i > 0:
            comment["replies"] = [
                {"author": "Author", "text": f"Thank you for your feedback on comment {i + 1}!", "created_at": f"2026-01-{(i % 28) + 1:02d} at 11:{i:02d} AM"},
            ]
        comments.append(comment)
    
    return {
        "page_title": "Complete Guide to Modern Web Development",
        "blog": {
            "name": "TechInsights",
            "tagline": "Exploring the cutting edge of technology",
        },
        "article": {
            "id": 1,
            "title": "The Complete Guide to Modern Web Development in 2026",
            "slug": "complete-guide-modern-web-development-2026",
            "featured_image": "https://example.com/featured.jpg",
            "published_at": "January 15, 2026",
            "read_time": 12,
            "views": 15420,
            "content_blocks": content_blocks,
            "tags": ["Web Development", "JavaScript", "Python", "Best Practices", "Tutorial"],
            "author": {
                "name": "Sarah Johnson",
                "avatar": "https://example.com/avatars/sarah.jpg",
                "bio": "Senior Software Engineer with 10+ years of experience in web development. Passionate about clean code and teaching others.",
                "social_links": [
                    {"platform": "Twitter", "url": "https://twitter.com/sarahj"},
                    {"platform": "GitHub", "url": "https://github.com/sarahj"},
                ],
            },
        },
        "comments": comments,
        "related_posts": [
            {"slug": "intro-to-rust", "title": "Introduction to Rust Programming", "thumbnail": "https://example.com/rust.jpg", "excerpt": "Learn the basics of Rust programming language and why it's becoming so popular."},
            {"slug": "python-best-practices", "title": "Python Best Practices for 2026", "thumbnail": "https://example.com/python.jpg", "excerpt": "Master the latest Python patterns and practices for production-ready code."},
            {"slug": "frontend-frameworks", "title": "Comparing Frontend Frameworks", "thumbnail": "https://example.com/frontend.jpg", "excerpt": "An in-depth comparison of React, Vue, and Svelte for modern web applications."},
        ],
    }


def run_benchmark(
    name: str,
    render_fn: Callable[[], str],
    iterations: int = 1000,
    warmup: int = 50
) -> BenchmarkResult:
    """Run a benchmark with the given render function."""
    # Warmup
    for _ in range(warmup):
        render_fn()
    
    # Actual benchmark
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = render_fn()
        end = time.perf_counter()
        times.append(end - start)
        # Verify output is non-empty
        assert len(result) > 100, "Render produced empty or minimal output"
    
    total_time = sum(times)
    mean_time = statistics.mean(times)
    
    return BenchmarkResult(
        name=name,
        engine=name.split(" ")[0],
        iterations=iterations,
        total_time=total_time,
        mean_time=mean_time,
        median_time=statistics.median(times),
        min_time=min(times),
        max_time=max(times),
        std_dev=statistics.stdev(times) if len(times) > 1 else 0,
        renders_per_second=iterations / total_time,
    )


def main():
    """Run all benchmarks."""
    print("=" * 80)
    print("MiniJinja vs Jinja2 Real-World Performance Benchmark")
    print("=" * 80)
    print()
    
    # Load templates
    template_dir = Path(__file__).parent / "templates"
    ecommerce_template = (template_dir / "ecommerce.html").read_text()
    blog_template = (template_dir / "blog_article.html").read_text()
    
    # Generate test data with different sizes
    test_configs = [
        ("Small", 10, 5),   # 10 products, 5 comments
        ("Medium", 50, 20), # 50 products, 20 comments
        ("Large", 200, 100), # 200 products, 100 comments
    ]
    
    results: List[BenchmarkResult] = []
    
    for size_name, product_count, comment_count in test_configs:
        print(f"\n{'=' * 80}")
        print(f"Dataset: {size_name} ({product_count} products, {comment_count} comments)")
        print("=" * 80)
        
        ecommerce_data = generate_ecommerce_data(product_count)
        blog_data = generate_blog_data(comment_count)
        
        iterations = 500 if size_name == "Large" else 1000
        
        # MiniJinja benchmarks
        print(f"\n[E-commerce Template - {size_name}]")
        mj_env = fluxa.Environment()
        mj_env.add_template("ecommerce", ecommerce_template)
        
        result = run_benchmark(
            f"MiniJinja {size_name}",
            lambda: mj_env.render_template("ecommerce", **ecommerce_data),
            iterations=iterations
        )
        print(f"  {result}")
        results.append(result)
        
        if HAS_JINJA2:
            j2_env = jinja2.Environment()
            j2_template = j2_env.from_string(ecommerce_template)
            
            result = run_benchmark(
                f"Jinja2 {size_name}",
                lambda: j2_template.render(**ecommerce_data),
                iterations=iterations
            )
            print(f"  {result}")
            results.append(result)
        
        # Blog template benchmarks
        print(f"\n[Blog Article Template - {size_name}]")
        mj_env.add_template("blog", blog_template)
        
        result = run_benchmark(
            f"MiniJinja {size_name}",
            lambda: mj_env.render_template("blog", **blog_data),
            iterations=iterations
        )
        print(f"  {result}")
        results.append(result)
        
        if HAS_JINJA2:
            j2_blog = j2_env.from_string(blog_template)
            
            result = run_benchmark(
                f"Jinja2 {size_name}",
                lambda: j2_blog.render(**blog_data),
                iterations=iterations
            )
            print(f"  {result}")
            results.append(result)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if HAS_JINJA2:
        mj_results = [r for r in results if r.engine == "MiniJinja"]
        j2_results = [r for r in results if r.engine == "Jinja2"]
        
        mj_avg = statistics.mean([r.mean_time for r in mj_results])
        j2_avg = statistics.mean([r.mean_time for r in j2_results])
        
        speedup = j2_avg / mj_avg
        
        print(f"\nAverage render time:")
        print(f"  MiniJinja: {mj_avg * 1000:.3f} ms")
        print(f"  Jinja2:    {j2_avg * 1000:.3f} ms")
        print(f"\nMiniJinja is {speedup:.2f}x {'faster' if speedup > 1 else 'slower'} than Jinja2")
        
        mj_rps = statistics.mean([r.renders_per_second for r in mj_results])
        j2_rps = statistics.mean([r.renders_per_second for r in j2_results])
        print(f"\nThroughput:")
        print(f"  MiniJinja: {mj_rps:.1f} renders/sec")
        print(f"  Jinja2:    {j2_rps:.1f} renders/sec")
    
    print("\n" + "=" * 80)
    print("Benchmark complete!")


if __name__ == "__main__":
    main()
