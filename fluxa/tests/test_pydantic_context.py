"""Test Pydantic context validation."""
from pydantic import BaseModel, ValidationError
from fluxa import validate_context, has_pydantic, Environment


class UserContext(BaseModel):
    name: str
    age: int
    email: str = "default@example.com"


class ArticleContext(BaseModel):
    title: str
    author: UserContext
    tags: list[str] = []


print(f"Pydantic available: {has_pydantic()}")

# Test 1: Valid simple validation
data = {"name": "John", "age": 30}
validated = validate_context(UserContext, data)
print(f"Test 1 (valid simple): {validated}")

# Test 2: Validation with defaults
data2 = {"name": "Jane", "age": 25}
validated2 = validate_context(UserContext, data2)
print(f"Test 2 (with defaults): email={validated2.email}")

# Test 3: Nested model validation
data3 = {
    "title": "My Article",
    "author": {"name": "Bob", "age": 40},
    "tags": ["python", "templating"]
}
validated3 = validate_context(ArticleContext, data3)
print(f"Test 3 (nested): {validated3.title} by {validated3.author.name}")

# Test 4: Invalid data - should raise ValidationError
try:
    invalid_data = {"name": "Alice"}  # missing required 'age'
    validate_context(UserContext, invalid_data)
    print("Test 4 (invalid): FAILED - should have raised error")
except Exception as e:
    print(f"Test 4 (invalid): Correctly raised {type(e).__name__}")

# Test 5: Use validated context in template
env = Environment()
template = "Hello, {{ name }}! You are {{ age }} years old."
validated5 = validate_context(UserContext, {"name": "Charlie", "age": 35})
result = env.render_str(template, **validated5.model_dump())
print(f"Test 5 (render): {result}")

print("\nAll tests passed!")
