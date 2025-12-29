# MappingProxyType

## Overview

`types.MappingProxyType` creates a read-only view of a dictionary. Unlike just "promising not to modify it," this provides true runtime immutability - any attempt to modify raises `TypeError`.

## The Problem

```python
config = {"debug": False, "timeout": 30}

# Pass to function
process(config)

# Oops, function modified it
config["debug"] = True  # Side effect!
```

Solutions that don't work well:
- "Just don't modify it" - Not enforced
- `dict.copy()` - Makes a copy (memory overhead)
- `tuple(dict.items())` - Loses dict interface

## The Solution

```python
from types import MappingProxyType

config = {"debug": False}
readonly = MappingProxyType(config)

readonly["debug"]  # Works
readonly["debug"] = True  # TypeError!
```

## How It Works

```python
original = {"a": 1, "b": 2}
proxy = MappingProxyType(original)

# Read operations work
proxy["a"]           # 1
proxy.get("b")       # 2
"a" in proxy         # True
list(proxy.keys())   # ['a', 'b']

# Write operations fail
proxy["c"] = 3       # TypeError
del proxy["a"]       # TypeError
proxy.clear()        # TypeError
```

## Key Characteristics

### 1. Read-Only View

```python
proxy = MappingProxyType(data)
proxy["key"]  # ✓ Works
proxy["key"] = value  # ✗ TypeError
```

### 2. Dynamic (Not a Copy)

```python
data = {"count": 0}
proxy = MappingProxyType(data)

data["count"] = 10
print(proxy["count"])  # 10 - reflects change!
```

### 3. Zero Copy Overhead

```python
# No memory duplication
proxy = MappingProxyType(huge_dict)  # Instant, no copy
```

### 4. Full Read Interface

```python
proxy.keys()
proxy.values()
proxy.items()
proxy.get(key, default)
len(proxy)
key in proxy
```

## Common Use Cases

### 1. Configuration Protection

```python
class Config:
    def __init__(self):
        self._config = {"debug": False}
        self.settings = MappingProxyType(self._config)
    
    def set(self, key, value):
        self._config[key] = value  # Controlled update

config = Config()
config.settings["debug"]  # ✓ Read
config.settings["debug"] = True  # ✗ Write blocked
config.set("debug", True)  # ✓ Use API
```

### 2. API Responses

```python
class APIResponse:
    def __init__(self, data):
        self.data = MappingProxyType(data)

response = APIResponse({"user": "alice"})
# Clients can't modify response data
```

### 3. Default Values

```python
_DEFAULTS = {"timeout": 30, "retries": 3}
DEFAULTS = MappingProxyType(_DEFAULTS)

# Users can read defaults but can't change them
```

### 4. Sharing Data Safely

```python
shared_state = MappingProxyType(internal_state)
# Share with untrusted code without risk
```

## Python's Internal Use

Python uses `MappingProxyType` internally:

```python
class Example:
    class_var = 42

print(type(Example.__dict__))
# <class 'mappingproxy'>
```

**Why:** Prevents direct modification of class namespace.

```python
Example.__dict__["new_attr"] = "value"  # TypeError!
Example.new_attr = "value"  # ✓ Use normal attribute assignment
```

## Shallow vs Deep Immutability

### Shallow (What You Get)

```python
data = {
    "name": "Alice",
    "tags": ["python", "async"]
}
proxy = MappingProxyType(data)

proxy["name"] = "Bob"  # ✗ TypeError
proxy["tags"].append("web")  # ✓ Works! (nested object)
```

### Deep Immutability Solution

```python
def make_deep_readonly(d):
    """Recursively make readonly"""
    result = {}
    for key, value in d.items():
        if isinstance(value, dict):
            value = make_deep_readonly(value)
        elif isinstance(value, list):
            value = tuple(value)  # Lists → tuples
        result[key] = value
    return MappingProxyType(result)
```

## vs Other Approaches

### 1. Plain Dict

```python
config = {"debug": False}
# No protection, easy to modify by mistake
```

### 2. Tuple of Items

```python
config = (("debug", False), ("timeout", 30))
# Immutable but no dict interface
config["debug"]  # Doesn't work!
```

### 3. Frozen Dict (Third-Party)

```python
from frozendict import frozendict
config = frozendict({"debug": False})
# Immutable and hashable, but requires dependency
```

### 4. dict.copy()

```python
readonly = config.copy()
# Makes a copy (memory overhead)
# Still mutable!
```

### 5. MappingProxyType

```python
readonly = MappingProxyType(config)
# ✓ True immutability
# ✓ No copy overhead
# ✓ Dynamic view
# ✓ Built-in
```

## Best Practices

### 1. Document the Protection

```python
class Service:
    """
    Attributes:
        config: Read-only configuration (MappingProxyType)
    """
    def __init__(self):
        self.config = MappingProxyType({...})
```

### 2. Keep Internal Reference Private

```python
class Config:
    def __init__(self):
        self._config = {}  # Private, mutable
        self.config = MappingProxyType(self._config)  # Public, readonly
```

### 3. Use for API Boundaries

```python
# Good boundary
def get_settings():
    return MappingProxyType(internal_settings)

# Bad boundary
def get_settings():
    return internal_settings  # Can be modified!
```

### 4. Consider Deep Immutability

For nested structures, either:
- Document that nested objects are mutable
- Recursively wrap with MappingProxyType
- Convert nested lists to tuples

## Common Pitfalls

### 1. Forgetting About Nested Objects

```python
proxy = MappingProxyType({"list": [1, 2, 3]})
proxy["list"].append(4)  # Works! List is mutable
```

### 2. Not Keeping Original Reference

```python
proxy = MappingProxyType({"a": 1})
# Lost reference to original dict
# Can't update even through official API!
```

Keep the original:

```python
self._data = {"a": 1}
self.data = MappingProxyType(self._data)
# Can update self._data
```

### 3. Trying to Hash It

```python
proxy = MappingProxyType({"a": 1})
{proxy: "value"}  # TypeError! Not hashable
```

MappingProxyType is not hashable (even though it's read-only).

### 4. Assuming It's a Copy

```python
data = {"count": 0}
proxy = MappingProxyType(data)
data["count"] = 10
# proxy["count"] is now 10!
```

It's a view, not a snapshot.

## Performance

- **Creation:** O(1) - no copying
- **Access:** Same as dict (minimal overhead)
- **Memory:** Minimal (just the wrapper)

```python
# No performance penalty for read operations
big_dict = {i: i for i in range(1000000)}
proxy = MappingProxyType(big_dict)  # Instant
proxy[500000]  # Just as fast as dict
```

## Type Hints

```python
from types import MappingProxyType
from typing import Mapping

def process(config: Mapping[str, int]):
    # Accepts dict, MappingProxyType, etc.
    pass

# More specific
def process(config: MappingProxyType):
    pass
```

## When NOT to Use

- **Need deep immutability:** Use immutable data structures
- **Need hashability:** Use frozendict (third-party) or tuple
- **Frequent updates:** Just use dict
- **Snapshot needed:** Use dict.copy()

## Real-World Examples

### Django Settings

Django exposes settings as a read-only object (not exactly MappingProxyType, but similar concept).

### Configuration Management

```python
class AppConfig:
    def __init__(self):
        self._settings = load_config()
        self.settings = MappingProxyType(self._settings)
    
    def reload(self):
        self._settings.clear()
        self._settings.update(load_config())
```

### API Responses

```python
@dataclass
class User:
    data: MappingProxyType
    
    @classmethod
    def from_api(cls, response):
        return cls(MappingProxyType(response))
```

## Further Reading

- [types.MappingProxyType Documentation](https://docs.python.org/3/library/types.html#types.MappingProxyType)
- [PEP 416 - Adding read-only proxy](https://www.python.org/dev/peps/pep-0416/)
- [Python Data Model - Mapping Types](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)

## Key Takeaways

✓ Creates truly read-only dict views  
✓ Zero copy overhead - just a wrapper  
✓ Dynamic view - reflects underlying changes  
✓ Python uses it for `class.__dict__`  
✓ Perfect for config, API responses, defaults  
✓ Protection is shallow (nested objects still mutable)  
✓ Not hashable (can't use as dict key)  
✓ Minimal performance overhead

