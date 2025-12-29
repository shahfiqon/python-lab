# `__init_subclass__`

## Overview

`__init_subclass__` is a special method that runs when a class is subclassed. It's Python's answer to the common pattern of needing to do something whenever a new class is created.

Introduced in Python 3.6 (PEP 487), it provides a simpler alternative to metaclasses for many common use cases.

## How It Works

```python
class Base:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        print(f"{cls.__name__} was just created!")

class Child(Base):  # Prints: "Child was just created!"
    pass
```

The method is called **at class creation time**, not when instances are created.

## Key Parameters

- `cls`: The newly created subclass
- `**kwargs`: Any keyword arguments passed in the class definition

## Common Use Cases

### 1. Plugin Registration

Automatically register classes when they're defined:

```python
class PluginBase:
    registry = {}
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        PluginBase.registry[cls.__name__] = cls
```

This is how many plugin systems work - plugins register themselves just by being imported.

### 2. Validation

Enforce rules about class definitions:

```python
class APIEndpoint:
    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, 'path'):
            raise TypeError(f"{cls.__name__} must define 'path'")
```

Catches errors at import time, not runtime.

### 3. Configuration

Accept parameters in the class definition:

```python
class Model:
    def __init_subclass__(cls, table_name=None, **kwargs):
        cls.table_name = table_name or cls.__name__.lower()

class User(Model, table_name="users_table"):
    pass
```

Clean syntax for class-level configuration.

### 4. Automatic Decoration

Wrap methods or add functionality automatically:

```python
class AutoLogged:
    def __init_subclass__(cls, **kwargs):
        for name, method in cls.__dict__.items():
            if callable(method) and not name.startswith('_'):
                setattr(cls, name, log_wrapper(method))
```

## vs Metaclasses

### When to Use `__init_subclass__`
- ✓ Plugin registration
- ✓ Validation
- ✓ Configuration
- ✓ Method decoration
- ✓ Simpler inheritance patterns

### When You Still Need Metaclasses
- Creating new types with custom behavior
- Modifying class creation fundamentally
- Complex multiple inheritance scenarios
- Custom attribute access at the class level

**Rule of thumb:** Start with `__init_subclass__`. Only reach for metaclasses when you actually need them.

## Best Practices

### 1. Always call `super()`

```python
def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)  # Important!
    # Your logic here
```

This ensures compatibility with multiple inheritance.

### 2. Accept `**kwargs`

Even if you don't use them, accept `**kwargs` to play nicely with other classes in the inheritance chain.

### 3. Validate Early

Put validation in `__init_subclass__` to catch errors at import time:

```python
def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    if not hasattr(cls, 'required_attr'):
        raise TypeError(f"Missing required_attr in {cls.__name__}")
```

### 4. Document Parameters

If your class accepts keyword arguments, document them:

```python
class Configurable:
    """
    Base class for configurable components.
    
    Subclass parameters:
        timeout (int): Operation timeout in seconds (default: 30)
        retry (bool): Whether to retry on failure (default: True)
    """
    def __init_subclass__(cls, timeout=30, retry=True, **kwargs):
        ...
```

## Real-World Examples

### Django Model Fields

Django uses `__init_subclass__` internally for model field registration:

```python
class Model:
    def __init_subclass__(cls, **kwargs):
        # Collect all field definitions
        # Register with Django's model system
```

### Abstract Base Classes

The `abc` module uses similar mechanisms:

```python
from abc import ABC, abstractmethod

class MyABC(ABC):  # ABC uses __init_subclass__ internally
    @abstractmethod
    def required_method(self):
        pass
```

### Type Checking Libraries

Libraries like `pydantic` use it for validation setup:

```python
class BaseModel:
    def __init_subclass__(cls, **kwargs):
        # Build validation schema from type hints
        # Set up serializers/deserializers
```

## Common Pitfalls

1. **Forgetting `super()`**: Breaks multiple inheritance
2. **Doing too much work**: Keep it fast - this runs at import time
3. **Not handling kwargs**: Can break when combined with other classes
4. **Modifying the wrong class**: Remember `cls` is the subclass, not the base class

## Performance Considerations

- Runs once at class definition time
- No runtime overhead for instances
- Keep the logic lightweight - it affects import time

## When NOT to Use

- Don't use it for instance initialization (use `__init__` instead)
- Don't use it for complex metaclass-level operations
- Don't use it if you need to modify class creation itself

## Further Reading

- [PEP 487 - Simpler customization of class creation](https://www.python.org/dev/peps/pep-0487/)
- [Python Data Model - __init_subclass__](https://docs.python.org/3/reference/datamodel.html#object.__init_subclass__)
- Raymond Hettinger's talks on Python's class mechanics

## Key Takeaways

✓ Runs at class creation time, not instance creation  
✓ Simpler alternative to metaclasses for most use cases  
✓ Perfect for plugin systems, validation, and configuration  
✓ Always call `super().__init_subclass__(**kwargs)`  
✓ Catches errors early, at import time

