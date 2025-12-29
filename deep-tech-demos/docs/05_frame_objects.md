# Frame Objects (`sys._getframe`)

## Overview

Frame objects represent Python's execution stack frames at runtime. They provide deep introspection capabilities, allowing you to inspect the call stack, access local variables, and understand the execution context of your code.

**Important:** `sys._getframe` is a private API (note the leading underscore), but it's widely used in production tools and is stable across Python versions.

## What is a Frame?

When Python executes code, it maintains a call stack of **frames**. Each frame represents:
- A function call
- Local variables
- The line being executed
- A reference to the calling frame

```python
import sys

def example():
    frame = sys._getframe(0)  # Get current frame
    print(frame.f_code.co_name)  # 'example'
    print(frame.f_lineno)        # current line number
```

## Frame Object Attributes

### `f_code` - Code Object
Contains information about the function:
- `co_name` - Function name
- `co_filename` - File path
- `co_argcount` - Number of arguments
- `co_varnames` - Variable names

### `f_locals` - Local Variables
Dictionary of local variables in the frame.

### `f_globals` - Global Variables
Dictionary of global variables accessible from the frame.

### `f_back` - Previous Frame
Reference to the calling frame (or `None` for the bottom).

### `f_lineno` - Line Number
Current line number being executed.

### `f_lasti` - Last Instruction
Index of the last attempted instruction in bytecode.

## Using `sys._getframe(depth)`

The `depth` parameter specifies which frame to retrieve:
- `0` - Current frame
- `1` - Caller's frame
- `2` - Caller's caller, etc.

```python
def outer():
    def inner():
        frame0 = sys._getframe(0)  # inner's frame
        frame1 = sys._getframe(1)  # outer's frame
        
        print(frame0.f_code.co_name)  # 'inner'
        print(frame1.f_code.co_name)  # 'outer'
    inner()
```

## Common Use Cases

### 1. Debugging and Introspection

```python
def debug_print(var_name):
    frame = sys._getframe(1)
    value = frame.f_locals.get(var_name, '<not found>')
    print(f"{frame.f_code.co_name}:{frame.f_lineno} {var_name}={value}")
```

### 2. Automatic Logging with Context

```python
class Logger:
    @staticmethod
    def log(message):
        frame = sys._getframe(1)
        print(f"[{frame.f_code.co_name}:{frame.f_lineno}] {message}")
```

### 3. Call Stack Analysis

```python
def print_stack():
    frame = sys._getframe(1)
    while frame:
        print(f"{frame.f_code.co_name} at line {frame.f_lineno}")
        frame = frame.f_back
```

### 4. Performance Profiling

```python
def profile(func):
    def wrapper(*args, **kwargs):
        frame = sys._getframe(1)
        caller = frame.f_code.co_name
        # Log timing with caller context
        return func(*args, **kwargs)
    return wrapper
```

### 5. Test Framework Magic

Pytest and other test frameworks use frame inspection to:
- Provide better error messages
- Capture local variables on failure
- Show execution context

## vs `inspect` Module

The `inspect` module provides a higher-level API built on top of frame objects:

```python
import inspect

# These are equivalent:
sys._getframe(0)
inspect.currentframe()

# inspect provides more features:
inspect.stack()        # Full stack with context
inspect.getframeinfo() # Structured frame info
```

**When to use which:**
- **`inspect`** - Recommended public API for most use cases
- **`sys._getframe`** - When you need maximum speed or specific frame access

## Real-World Usage

### Django Debug Toolbar
Uses frame inspection to capture local variables and call stacks during request processing.

### pytest
Captures frames on test failure to show local variable state:
```python
def test_example():
    x = 10
    y = 20
    assert x + y == 50  # pytest shows x=10, y=20 on failure
```

### Coverage.py
Uses frames to track which lines of code are executed.

### Logging Libraries
Advanced loggers use frames to automatically include:
- Function names
- Line numbers
- Module paths
- Variable context

### Debuggers (pdb, ipdb)
Debuggers extensively use frame objects to:
- Step through code
- Inspect variables
- Evaluate expressions in different scopes

## Best Practices

### 1. Use `inspect` When Possible

```python
# Prefer this
import inspect
frame = inspect.currentframe()

# Over this (unless you need the speed)
frame = sys._getframe(0)
```

### 2. Handle Frame Depth Carefully

```python
def safe_get_caller():
    try:
        return sys._getframe(1).f_code.co_name
    except ValueError:
        return '<unknown>'  # No caller (depth too high)
```

### 3. Don't Modify `f_locals`

```python
# This is unreliable and not recommended
frame = sys._getframe(1)
frame.f_locals['new_var'] = 42  # Don't do this!
```

Changes to `f_locals` may not persist. Use it for reading only.

### 4. Be Careful with Performance

Frame inspection has overhead. Don't use it in hot loops:

```python
# Bad: Frame inspection in loop
for i in range(1000000):
    frame = sys._getframe(0)  # Slow!

# Good: Outside loop or conditional
if DEBUG:
    frame = sys._getframe(0)
```

### 5. Clean Up Frame References

Frame objects can create reference cycles:

```python
frame = sys._getframe(0)
# Use frame...
del frame  # Clean up when done
```

## Common Pitfalls

### 1. Depth Errors

```python
sys._getframe(100)  # ValueError: call stack is not deep enough
```

Always handle potential `ValueError`.

### 2. Frame References Keep Objects Alive

```python
def leaky():
    big_data = [1] * 1000000
    frame = sys._getframe(0)
    # frame.f_locals contains big_data
    # big_data won't be GC'd while frame exists
    return frame  # Don't do this!
```

### 3. Modifying `f_locals` Doesn't Work

Changes to `f_locals` dict don't affect actual local variables. It's a read-only view (mostly).

### 4. Frame Inspection in Different Interpreters

Frame objects are CPython-specific. PyPy and other implementations may have different behavior.

## Performance Considerations

- `sys._getframe()` - Very fast (~100ns)
- Accessing frame attributes - Fast (~10ns)
- `inspect.stack()` - Slower (~1-10μs), builds full stack
- `inspect.getframeinfo()` - Moderate (~100-500ns)

**Rule of thumb:** Frame inspection is cheap for debugging/logging, but avoid in tight loops.

## Security Considerations

Frame inspection can expose sensitive information:
- Local variables (passwords, tokens)
- Execution paths
- Internal state

**Be careful when:**
- Logging frame data to external services
- Exposing frame info in API responses
- Serializing frame information

## Alternatives

### For Caller Info: `inspect.stack()`

```python
import inspect
caller = inspect.stack()[1]
print(f"Called from {caller.function} at line {caller.lineno}")
```

### For Variable Inspection: `locals()` and `globals()`

```python
def example():
    x = 10
    print(locals())  # {'x': 10}
```

### For Debugging: `pdb` or `breakpoint()`

```python
def buggy_function():
    x = 10
    breakpoint()  # Interactive debugger
    y = x + 20
```

## Advanced Techniques

### Custom Exception Context

```python
class ContextualError(Exception):
    def __init__(self, message):
        frame = sys._getframe(1)
        context = f"{frame.f_code.co_name}:{frame.f_lineno}"
        super().__init__(f"{context} - {message}")
```

### Variable Tracking

```python
def track_changes(var_name):
    """Monitor when a variable changes"""
    frame = sys._getframe(1)
    original = frame.f_locals.get(var_name)
    # ... later check if it changed ...
```

### Dynamic Scoping Simulation

```python
def get_dynamic_variable(name):
    """Search up the stack for a variable"""
    frame = sys._getframe(1)
    while frame:
        if name in frame.f_locals:
            return frame.f_locals[name]
        frame = frame.f_back
    raise NameError(f"{name} not found in call stack")
```

## Further Reading

- [Python Data Model - Frame Objects](https://docs.python.org/3/reference/datamodel.html#frame-objects)
- [inspect Module Documentation](https://docs.python.org/3/library/inspect.html)
- [sys Module - _getframe](https://docs.python.org/3/library/sys.html#sys._getframe)
- David Beazley's talks on Python internals

## Key Takeaways

✓ Frame objects provide runtime introspection of the call stack  
✓ `sys._getframe(n)` gets frame at depth n (0 = current)  
✓ Access function names, line numbers, and local variables  
✓ Widely used in debuggers, profilers, and test frameworks  
✓ Prefer `inspect` module for public API when possible  
✓ Don't modify `f_locals` - it's unreliable  
✓ Clean up frame references to avoid memory leaks  
✓ Has performance cost - avoid in hot loops

