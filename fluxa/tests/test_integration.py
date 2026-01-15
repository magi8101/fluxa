"""Test file for Jin Pydantic and orjson integration"""

from fluxa import Environment
from fluxa._lowlevel import has_orjson, has_pydantic, orjson_dumps, orjson_loads
from pydantic import BaseModel

print("=== Jin Integration Test ===")
print(f"orjson available: {has_orjson()}")
print(f"pydantic available: {has_pydantic()}")

# Test orjson serialization
data = {"name": "Alice", "age": 30, "items": [1, 2, 3]}
json_bytes = orjson_dumps(data)
print(f"orjson_dumps result: {json_bytes}")

if json_bytes:
    loaded = orjson_loads(json_bytes)
    print(f"orjson_loads result: {loaded}")

# Test Pydantic model in template
class User(BaseModel):
    name: str
    age: int

env = Environment()
env.add_template("greeting", "Hello {{ user.name }}, you are {{ user.age }} years old!")

user = User(name="Alice", age=30)
result = env.render_template("greeting", user=user)
print(f"Pydantic model render: {result}")

# Test nested Pydantic model
class Address(BaseModel):
    city: str
    country: str

class Person(BaseModel):
    name: str
    address: Address

env.add_template("person", "{{ person.name }} lives in {{ person.address.city }}, {{ person.address.country }}")
person = Person(name="Bob", address=Address(city="Tokyo", country="Japan"))
result2 = env.render_template("person", person=person)
print(f"Nested Pydantic model render: {result2}")

print("=== All tests passed ===")
