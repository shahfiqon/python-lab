# Weak References

## Overview

Weak references allow you to reference objects without preventing them from being garbage collected. They're essential for building caches, event systems, and any situation where you want to keep track of objects without keeping them alive.

## The Problem

Python uses reference counting for garbage collection. An object is kept alive as long as there's at least one reference to it:

```python
obj = SomeObject()  # ref count = 1
another_ref = obj   # ref count = 2
del obj             # ref count = 1
del another_ref     # ref count = 0, object is deleted
```

Sometimes you want to reference an object without keeping it alive. That's where weak references come in.

## How Weak References Work

```python
import weakref

obj = SomeObject()
weak = weakref.ref(obj)  # Doesn't increase ref count

# Access the object
print(weak())  # Returns obj if it's still alive

del obj  # Object can be garbage collected
print(weak())  # Returns None, object is gone
```

## Key Types

### 1. `weakref.ref`

Basic weak reference to any object:

```python
weak = weakref.ref(obj)
obj_or_none = weak()  # Call to get the object
```

### 2. `weakref.WeakValueDictionary`

Dictionary with weak references as values:

```python
cache = weakref.WeakValueDictionary()
cache['key'] = obj  # Weakly referenced
# When obj is deleted elsewhere, 'key' is auto-removed
```

### 3. `weakref.WeakKeyDictionary`

Dictionary with weak references as keys:

```python
metadata = weakref.WeakKeyDictionary()
metadata[obj] = {'info': 'data'}
# When obj is deleted, entry is auto-removed
```

### 4. `weakref.WeakSet`

Set of weak references:

```python
objects = weakref.WeakSet()
objects.add(obj)
# When obj is deleted, it's auto-removed from set
```

### 5. `weakref.WeakMethod`

Weak reference to a bound method:

```python
weak_method = weakref.WeakMethod(obj.method)
```

## Common Use Cases

### 1. Caching Without Memory Leaks

```python
class Cache:
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()
    
    def get_or_create(self, key, factory):
        if key in self._cache:
            return self._cache[key]
        obj = factory()
        self._cache[key] = obj
        return obj
```

Benefits:
- Objects are cached while in use
- Automatically cleared when no longer needed
- No manual cache invalidation required

### 2. Observer/Event Systems

```python
class EventBus:
    def __init__(self):
        self._listeners = weakref.WeakSet()
    
    def subscribe(self, listener):
        self._listeners.add(listener)
    
    def publish(self, event):
        for listener in self._listeners:
            listener.handle(event)
```

Benefits:
- Listeners don't need to manually unsubscribe
- No memory leaks from forgotten subscriptions
- Clean automatic cleanup

### 3. Metadata Storage

```python
# Store extra data about objects without modifying them
metadata = weakref.WeakKeyDictionary()
metadata[some_object] = {'created': time.time(), 'source': 'api'}
```

### 4. Circular Reference Breaking

```python
class Node:
    def __init__(self, value):
        self.value = value
        self._parent = None  # Use weak ref to avoid cycle
    
    def set_parent(self, parent):
        self._parent = weakref.ref(parent)
    
    @property
    def parent(self):
        return self._parent() if self._parent else None
```

## What Can Be Weakly Referenced?

**Can:**
- Class instances
- Functions
- Bound methods (use `WeakMethod`)
- Class objects
- Files
- Most objects

**Cannot:**
- `int`, `str`, `tuple` (immutable built-ins)
- `list`, `dict` (mutable built-ins) *
- Some extension types

\* Note: While you can't weakref a plain `list`, you can weakref a subclass of `list`.

## Best Practices

### 1. Always Check for None

```python
weak = weakref.ref(obj)
obj = weak()
if obj is not None:
    # Use obj
    pass
```

### 2. Use Appropriate Collection Types

- `WeakValueDictionary` - Cache-like structures
- `WeakKeyDictionary` - Metadata on objects you don't own
- `WeakSet` - Tracking without ownership

### 3. Combine with `__del__` Carefully

Don't rely on `__del__` for critical cleanup when using weak references. The timing can be unpredictable.

### 4. Document Weak Reference Usage

Make it clear in documentation when weak references are used:

```python
class Cache:
    """
    LRU cache using weak references.
    
    Note: Cached objects are kept alive only while external
    references exist. Objects may be evicted due to garbage
    collection.
    """
```

## Common Pitfalls

### 1. Short-Lived Objects

```python
cache = weakref.WeakValueDictionary()
cache['key'] = SomeObject()  # Object immediately GC'd!
```

Fix: Keep a strong reference while needed.

### 2. Forgetting About GC Timing

Garbage collection is not immediate:

```python
del obj
print(weak())  # Might still return obj!
gc.collect()   # Force collection
print(weak())  # Now returns None
```

### 3. WeakMethod Pitfalls

```python
# This doesn't work as expected
weak = weakref.ref(obj.method)  # Wrong!

# Use WeakMethod instead
weak = weakref.WeakMethod(obj.method)  # Correct
```

### 4. Weak References in Data Structures

Weak references themselves can't be compared or hashed reliably:

```python
weak1 = weakref.ref(obj)
weak2 = weakref.ref(obj)
weak1 == weak2  # False! Different weak ref objects
```

## Performance Considerations

- Weak references have minimal overhead
- `WeakValueDictionary` is slightly slower than `dict`
- Callback overhead when objects are destroyed
- Consider strong references if performance is critical

## Debugging Tips

### Print Active Weak References

```python
import weakref
print(weakref.getweakrefs(obj))
```

### Count References

```python
import sys
print(sys.getrefcount(obj))
```

### Force Garbage Collection

```python
import gc
gc.collect()
```

## Real-World Examples

### Django Query Caching

Django uses weak references internally to cache database query results without preventing objects from being freed.

### GUI Event Systems

Many GUI frameworks (Tkinter, PyQt, etc.) use weak references for event handlers to prevent circular references between widgets and callbacks.

### Object Pools

Connection pools and resource pools often use weak references to track checked-out resources without preventing their cleanup.

## Further Reading

- [Python weakref Module Documentation](https://docs.python.org/3/library/weakref.html)
- [Python Memory Management](https://docs.python.org/3/c-api/memory.html)
- [Python Garbage Collection](https://docs.python.org/3/library/gc.html)

## Key Takeaways

✓ Weak references don't prevent garbage collection  
✓ Essential for caches, observers, and event systems  
✓ Prevents many memory leaks automatically  
✓ Always check if weak reference is still alive (`weak() is not None`)  
✓ Use `WeakValueDictionary`, `WeakKeyDictionary`, and `WeakSet` for collections  
✓ Can't weakly reference built-in types like `int`, `str`, or `list`

