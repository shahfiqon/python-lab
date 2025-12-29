# Late-Bound Defaults (Sentinel Pattern)

## Overview

The sentinel pattern solves Python's mutable default argument trap and allows distinguishing between "argument not provided" vs any actual value (including `None`, `0`, `False`, etc.).

## The Problem: Mutable Defaults

```python
def add_item(item, lst=[]):  # BUG!
    lst.append(item)
    return lst

add_item(1)  # [1]
add_item(2)  # [1, 2] - Oops!
add_item(3)  # [1, 2, 3] - Same list!
```

**Why:** Default arguments are evaluated once at function definition time, not at call time.

## Common Solution: None

```python
def add_item(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

Works, but has limitations:
- Can't distinguish "not provided" from "explicitly None"
- `None` might be a valid value

## The Sentinel Solution

```python
_sentinel = object()

def add_item(item, lst=_sentinel):
    if lst is _sentinel:
        lst = []
    lst.append(item)
    return lst
```

Benefits:
- ✓ Distinguishes "not provided" from any value
- ✓ Can accept `None` as a valid argument
- ✓ Zero performance overhead
- ✓ CPython uses this pattern internally

## How It Works

```python
_not_provided = object()
```

Creates a unique object that can only be compared with `is`:

```python
_not_provided == _not_provided  # Don't use ==
_not_provided is _not_provided  # ✓ Use is
```

## Use Cases

### 1. Distinguishing None from Not-Provided

```python
_not_provided = object()

def set_config(key, value=_not_provided):
    if value is _not_provided:
        # Keep existing value
        pass
    elif value is None:
        # Clear the value
        config[key] = None
    else:
        # Set new value
        config[key] = value
```

### 2. API Parameters

```python
_not_set = object()

def request(url, timeout=_not_set, retries=_not_set):
    if timeout is _not_set:
        timeout = DEFAULT_TIMEOUT
    if retries is _not_set:
        retries = DEFAULT_RETRIES
    # ...
```

### 3. Cache Functions

```python
_miss = object()

def get_or_create(key, default=_miss):
    if key in cache:
        return cache[key]
    
    if default is not _miss:
        return default
    else:
        raise KeyError(key)
```

### 4. Optional Function Arguments

```python
_no_callback = object()

def process(data, callback=_no_callback):
    result = transform(data)
    
    if callback is not _no_callback:
        callback(result)
    
    return result
```

## Named Sentinels

For better readability:

```python
class _Sentinel:
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f"<{self.name}>"

MISSING = _Sentinel("MISSING")
EMPTY = _Sentinel("EMPTY")

def process(value=MISSING):
    if value is MISSING:
        print("Not provided")
    elif value is EMPTY:
        print("Explicitly empty")
```

## CPython's Use

### dict.get()

```python
# Simplified CPython implementation
_sentinel = object()

def get(self, key, default=_sentinel):
    if key in self:
        return self[key]
    if default is _sentinel:
        return None
    return default
```

### functools

```python
# functools.lru_cache uses sentinel
_CacheInfo = namedtuple(...)
_sentinel = object()
```

### asyncio

```python
# asyncio uses _MISSING
_MISSING = object()

async def wait_for(fut, timeout=_MISSING):
    if timeout is _MISSING:
        return await fut
    # ...
```

## Best Practices

### 1. Module-Level Sentinel

```python
# At module level
_sentinel = object()

# Use in functions
def func(arg=_sentinel):
    if arg is _sentinel:
        arg = default_value()
```

### 2. Private Name (Leading Underscore)

```python
_sentinel = object()  # ✓ Private
sentinel = object()   # ✗ Looks public
```

### 3. Use `is`, Never `==`

```python
if arg is _sentinel:  # ✓
if arg == _sentinel:  # ✗ Wrong!
```

### 4. Document the Pattern

```python
def func(value=_sentinel):
    """
    Args:
        value: The value to process. If not provided, 
               defaults to calling get_default_value().
    """
```

## vs Other Approaches

### 1. None (Common but Limited)

```python
def func(arg=None):
    if arg is None:
        arg = []
```

**Problem:** Can't pass `None` as a valid value.

### 2. `**kwargs` (Overcomplicated)

```python
def func(**kwargs):
    arg = kwargs.get('arg', default)
```

**Problem:** Loses explicit parameter listing.

### 3. Sentinel (Best)

```python
_sentinel = object()

def func(arg=_sentinel):
    if arg is _sentinel:
        arg = []
```

**Benefits:** Clear, explicit, handles all cases.

## Common Pitfalls

### 1. Using == Instead of is

```python
_sentinel = object()

if arg == _sentinel:  # Wrong! Use 'is'
    pass
```

### 2. Creating New Sentinel Each Time

```python
# Bad - new object each time
def func(arg=object()):
    if arg is object():  # Never true!
        pass

# Good - module-level
_sentinel = object()
def func(arg=_sentinel):
    if arg is _sentinel:  # Works!
        pass
```

### 3. Not Documenting It

```python
# Bad - unclear what _sentinel means
def func(arg=_sentinel):
    pass

# Good - documented
def func(arg=_sentinel):
    """
    Args:
        arg: Value to process. Defaults to empty list if not provided.
    """
```

### 4. Multiple Functions, Multiple Sentinels

```python
# Avoid
_sentinel1 = object()
_sentinel2 = object()

# Better - one per module
_not_provided = object()
```

## Performance

```python
import time

_sentinel = object()

# Test 1: None approach
def func_none(arg=None):
    if arg is None:
        arg = []

# Test 2: Sentinel approach  
def func_sentinel(arg=_sentinel):
    if arg is _sentinel:
        arg = []

# Both have identical performance
# ~20ns per call (CPython 3.11)
```

**Takeaway:** Zero performance difference. Use sentinel for clarity, not speed.

## Type Hints

```python
from typing import Optional, Union

# With None
def func(arg: Optional[list] = None) -> list:
    pass

# With sentinel (more complex)
_sentinel = object()
_Sentinel = type(_sentinel)

def func(arg: Union[list, _Sentinel] = _sentinel) -> list:
    pass

# Or use overloads
from typing import overload

@overload
def func(arg: list) -> list: ...
@overload
def func() -> list: ...

def func(arg=_sentinel):
    pass
```

## When to Use Sentinel

Use sentinel when:
- ✓ `None` is a valid value
- ✓ Need to distinguish "not provided"
- ✓ Function has expensive default
- ✓ Following CPython's pattern

Use `None` when:
- ✓ `None` is never a valid value
- ✓ Simpler is better
- ✓ Type hints are important

## Real-World Examples

### Dataclasses

```python
from dataclasses import dataclass, field, MISSING

@dataclass
class User:
    name: str
    tags: list = field(default_factory=list)

# Internally uses MISSING sentinel
```

### Django ORM

```python
# Django's NOT_PROVIDED sentinel
from django.db.models import NOT_PROVIDED

class Field:
    def __init__(self, default=NOT_PROVIDED):
        self.default = default
```

### FastAPI

```python
from fastapi import Query

@app.get("/items")
def items(q: str = Query(None)):
    # Uses sentinel internally
    pass
```

## Further Reading

- [Python Default Arguments](https://docs.python.org/3/reference/compound_stmts.html#function-definitions)
- [PEP 661 - Sentinel Values](https://www.python.org/dev/peps/pep-0661/)
- [Fluent Python - Default Values](https://www.oreilly.com/library/view/fluent-python/9781491946237/)

## Key Takeaways

✓ Use `_sentinel = object()` for late-bound defaults  
✓ Distinguishes "not provided" from any value including `None`  
✓ Compare with `is`, never `==`  
✓ Zero performance overhead  
✓ CPython uses this pattern extensively  
✓ More explicit than `None` for optional args  
✓ Module-level sentinels are best practice  
✓ Document the pattern for maintainability

