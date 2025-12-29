# `weakref.finalize`

## Overview

`weakref.finalize` provides reliable object finalization. It's the recommended way to clean up resources when objects are garbage collected, replacing the unreliable `__del__` method.

## The Problem with `__del__`

```python
class Resource:
    def __del__(self):
        # Clean up resources
        pass
```

Problems:
- May never be called (circular references)
- Timing is unpredictable
- Can cause object resurrection
- Not reliable for critical cleanup

## The Solution: `weakref.finalize`

```python
import weakref

class Resource:
    def __init__(self, name):
        self.name = name
        weakref.finalize(self, self.cleanup, name)
    
    @staticmethod
    def cleanup(name):
        print(f"Cleaning up {name}")
```

Benefits:
- ✓ Reliable - always runs
- ✓ Works with circular references
- ✓ Can be called manually
- ✓ No resurrection bugs

## How It Works

```python
finalizer = weakref.finalize(obj, callback, *args, **kwargs)
```

- `obj` - Object to track
- `callback` - Function to call on finalization
- `*args, **kwargs` - Arguments for callback

When `obj` is garbage collected, Python calls `callback(*args, **kwargs)`.

## Key Features

### 1. Automatic Cleanup

```python
class FileHandle:
    def __init__(self, filename):
        self.file = open(filename)
        weakref.finalize(self, self.file.close)
```

File closes automatically when object is deleted.

### 2. Manual Cleanup

```python
class Resource:
    def __init__(self):
        self.finalizer = weakref.finalize(self, cleanup_func)
    
    def close(self):
        self.finalizer()  # Call explicitly
```

Can trigger cleanup manually without waiting for GC.

### 3. Check Status

```python
if finalizer.alive:
    print("Finalizer hasn't run yet")
```

### 4. Detach

```python
finalizer.detach()  # Prevent cleanup from happening
```

### 5. Get Info

```python
finalizer.alive      # Is it still active?
finalizer.atexit     # Will it run at exit?
finalizer.detach()   # Unregister
```

## vs `__del__`

### `__del__` Issues

```python
class Bad:
    def __init__(self):
        self.ref = None
    
    def __del__(self):
        print("Cleaning up")

# Circular reference
a = Bad()
b = Bad()
a.ref = b
b.ref = a
del a, b  # __del__ may not run!
```

### `weakref.finalize` Solution

```python
class Good:
    def __init__(self):
        self.ref = None
        weakref.finalize(self, print, "Cleaning up")

# Circular reference
a = Good()
b = Good()
a.ref = b
b.ref = a
del a, b  # Cleanup WILL run
```

## Common Use Cases

### 1. File Handles

```python
class ManagedFile:
    def __init__(self, filename):
        self.file = open(filename)
        weakref.finalize(self, self.file.close)
```

### 2. Database Connections

```python
class Connection:
    def __init__(self, host):
        self.conn = connect(host)
        weakref.finalize(self, self.conn.close)
```

### 3. Resource Pools

```python
class PooledResource:
    def __init__(self, pool, resource):
        self.resource = resource
        weakref.finalize(self, pool.return_resource, resource)
```

### 4. Temporary Files

```python
class TempFile:
    def __init__(self):
        self.path = create_temp_file()
        weakref.finalize(self, os.unlink, self.path)
```

## Best Practices

### 1. Use Static Methods or Functions

```python
# Good - static method
class Resource:
    def __init__(self):
        weakref.finalize(self, Resource._cleanup, self.data)
    
    @staticmethod
    def _cleanup(data):
        # Clean up data
        pass

# Good - standalone function
def cleanup(data):
    # Clean up data
    pass

class Resource:
    def __init__(self):
        weakref.finalize(self, cleanup, self.data)
```

Don't capture `self` in the cleanup function!

### 2. Store Finalizer If You Need Control

```python
class Resource:
    def __init__(self):
        self.finalizer = weakref.finalize(self, cleanup)
    
    def close(self):
        if self.finalizer.alive:
            self.finalizer()
```

### 3. Pass Data, Not Object

```python
# Bad - keeps object alive
weakref.finalize(obj, lambda: obj.cleanup())

# Good - pass data separately
weakref.finalize(obj, cleanup, obj.data)
```

### 4. Handle Exceptions

```python
def safe_cleanup(resource):
    try:
        resource.close()
    except Exception as e:
        log(f"Cleanup failed: {e}")

weakref.finalize(obj, safe_cleanup, resource)
```

## Common Pitfalls

### 1. Capturing Self

```python
# Bad - circular reference
class Bad:
    def __init__(self):
        weakref.finalize(self, self.cleanup)  # Keeps self alive!
    
    def cleanup(self):
        pass

# Good
class Good:
    def __init__(self):
        weakref.finalize(self, Good.cleanup)
    
    @staticmethod
    def cleanup():
        pass
```

### 2. Forgetting GC

```python
obj = Resource()
del obj
# Finalizer may not run immediately!

import gc
gc.collect()  # Force collection if needed
```

### 3. Relying on Execution Order

Multiple finalizers may run in any order:

```python
# Don't assume order!
a = Resource()
b = Resource()
# Cleanup order is undefined
```

### 4. Using Finalizer After Detach

```python
finalizer = weakref.finalize(obj, cleanup)
finalizer.detach()
finalizer()  # Error! Already detached
```

## vs atexit

### `atexit`
- Runs at program exit
- All registered functions run
- No object awareness

```python
import atexit
atexit.register(cleanup)
```

### `weakref.finalize`
- Runs when object dies
- Only for deleted objects
- Tied to object lifetime

```python
weakref.finalize(obj, cleanup)
```

**Use atexit for:** Program-wide cleanup  
**Use finalize for:** Per-object cleanup

## Performance

- Minimal overhead (~100ns per finalizer)
- Doesn't slow down object creation
- Cleanup happens during GC (already slow)

## Real-World Examples

### Python Standard Library

Used in:
- `subprocess.Popen` - Clean up processes
- `multiprocessing` - Clean up resources
- `concurrent.futures` - Thread pool cleanup

### Web Frameworks

```python
class Request:
    def __init__(self):
        self.temp_files = []
        weakref.finalize(self, cleanup_temp_files, self.temp_files)
```

### Database ORMs

```python
class Session:
    def __init__(self, engine):
        self.connection = engine.connect()
        weakref.finalize(self, self.connection.close)
```

## Further Reading

- [weakref.finalize Documentation](https://docs.python.org/3/library/weakref.html#weakref.finalize)
- [PEP 442 - Safe object finalization](https://www.python.org/dev/peps/pep-0442/)
- [Garbage Collection in Python](https://docs.python.org/3/library/gc.html)

## Key Takeaways

✓ Use `weakref.finalize` instead of `__del__`  
✓ Works reliably with circular references  
✓ Can be called explicitly with `finalizer()`  
✓ Check status with `finalizer.alive`  
✓ Pass data to callback, don't capture self  
✓ No resurrection bugs  
✓ Cleanup happens exactly once  
✓ Used extensively in Python standard library

