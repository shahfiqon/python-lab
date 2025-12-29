# Descriptor Protocol

## Overview

The descriptor protocol is one of Python's most powerful but least understood features. It's the mechanism that makes `@property`, `@classmethod`, `@staticmethod`, and many ORM frameworks work.

## What is a Descriptor?

A descriptor is any object that defines at least one of these methods:

- `__get__(self, instance, owner)` - Called on attribute access
- `__set__(self, instance, value)` - Called on attribute assignment
- `__delete__(self, instance)` - Called on attribute deletion

## How It Works

When you access an attribute on an instance, Python checks if the class attribute is a descriptor. If it is, Python calls the descriptor's `__get__` method instead of just returning the value.

```python
class MyDescriptor:
    def __get__(self, instance, owner):
        print("__get__ called")
        return 42

class MyClass:
    attr = MyDescriptor()

obj = MyClass()
print(obj.attr)  # Calls MyDescriptor.__get__(), prints "__get__ called", returns 42
```

## Use Cases

### 1. Type Validation

The `Typed` descriptor in the demo enforces type checking at the attribute level:

```python
class User:
    age = Typed("age", int)
    name = Typed("name", str)
```

This is how libraries like `attrs` and `pydantic` implement type validation internally.

### 2. Lazy Evaluation

The `LazyProperty` descriptor computes a value once and caches it:

- First access: Runs the computation
- Subsequent accesses: Returns cached value
- Useful for expensive operations (database queries, file parsing, etc.)

### 3. Validation Logic

Custom validators can enforce business rules:

```python
class Account:
    balance = Validator("balance", lambda x: x >= 0, "Cannot be negative")
```

This centralizes validation logic and makes it reusable.

## Descriptor vs @property

### @property Approach
- Must write getter/setter for each attribute
- Lots of boilerplate
- Hard to share logic across classes

### Descriptor Approach
- Write once, use everywhere
- Centralized logic
- More abstract but more powerful

**Rule of thumb:** Use `@property` for one-off attribute logic. Use descriptors when you need the same behavior across multiple attributes or classes.

## Data vs Non-Data Descriptors

- **Data descriptor**: Defines `__set__` or `__delete__`
  - Takes priority over instance `__dict__`
  - Example: `property`, `Typed` descriptor

- **Non-data descriptor**: Only defines `__get__`
  - Instance `__dict__` takes priority
  - Example: Functions, `@classmethod`, `@staticmethod`

This distinction matters for attribute lookup order.

## Real-World Examples

### ORMs
```python
class User(Model):
    id = IntegerField()
    email = CharField()
```

`IntegerField` and `CharField` are descriptors that handle database interactions.

### Django Forms
```python
class ContactForm(Form):
    name = CharField(max_length=100)
    email = EmailField()
```

Form fields are descriptors that handle validation and cleaning.

### Dataclasses
Python's `@dataclass` decorator uses descriptors internally for field validation and default values.

## Common Pitfalls

1. **Forgetting the `name` parameter**: Descriptors need to know where to store data in `instance.__dict__`

2. **Not handling `instance is None`**: When accessed from the class (not instance), `instance` is `None`

3. **Circular imports**: Descriptors are powerful but can create complex dependencies

## Performance Considerations

- Descriptors add a small overhead to attribute access
- For performance-critical code, profile first
- The clarity and maintainability often outweigh the minimal performance cost

## Further Reading

- [Python Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html)
- [Descriptor Protocol PEP](https://www.python.org/dev/peps/pep-0252/)
- Raymond Hettinger's [Descriptor Guide](https://docs.python.org/3/howto/descriptor.html)

## Key Takeaways

✓ Descriptors control attribute access at the class level  
✓ They're the foundation of `@property`, `classmethod`, and more  
✓ Use them to centralize validation, type checking, and lazy computation  
✓ They're metaprogramming without metaclasses

