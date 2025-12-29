# Context Variables (`contextvars`)

## Overview

`contextvars` provides async-safe context-local state. Unlike `threading.local`, it works correctly with async/await, preserving context across async operations.

Introduced in Python 3.7 (PEP 567), it's essential for modern async Python applications.

## The Problem with `threading.local`

```python
import threading

local_data = threading.local()

async def handler():
    local_data.request_id = "req-123"
    await process()  # Context might switch!
    print(local_data.request_id)  # Might be different!
```

**Problem:** `threading.local` doesn't understand async tasks. Multiple async tasks on the same thread share the same "local" storage.

## The Solution: Context Variables

```python
from contextvars import ContextVar

request_id = ContextVar('request_id')

async def handler():
    request_id.set("req-123")
    await process()  # Context preserved!
    print(request_id.get())  # Always "req-123"
```

**Solution:** Each async task gets its own context, automatically.

## Basic Usage

### Creating Context Variables

```python
from contextvars import ContextVar

# With default
request_id = ContextVar('request_id', default='no-request')

# Without default
user_id = ContextVar('user_id')
```

### Setting Values

```python
token = request_id.set("req-123")
# Returns a token for later reset
```

### Getting Values

```python
# With default
value = request_id.get()

# Without default (raises LookupError if not set)
try:
    value = user_id.get()
except LookupError:
    value = None

# With fallback
value = user_id.get("guest")
```

### Resetting Values

```python
token = request_id.set("req-123")
# ... do work ...
request_id.reset(token)  # Restore previous value
```

## How It Works

### Execution Contexts

Python maintains an execution context for:
- Main thread
- Each thread
- Each async task
- Each manually created context

```python
async def task1():
    request_id.set("A")
    await asyncio.sleep(0.1)
    print(request_id.get())  # Always "A"

async def task2():
    request_id.set("B")
    await asyncio.sleep(0.1)
    print(request_id.get())  # Always "B"

# Both tasks run concurrently
await asyncio.gather(task1(), task2())
```

### Context Inheritance

Child tasks inherit parent context:

```python
request_id.set("parent")

async def child():
    print(request_id.get())  # "parent"
    request_id.set("child")
    print(request_id.get())  # "child"

await child()
print(request_id.get())  # Still "parent"!
```

Child modifications don't affect parent.

## Common Use Cases

### 1. Request Tracking

```python
request_id = ContextVar('request_id')

def log(message):
    rid = request_id.get()
    print(f"[{rid}] {message}")

async def handle_request(rid):
    request_id.set(rid)
    log("Starting")
    await process()
    log("Done")
```

### 2. Authentication Context

```python
current_user = ContextVar('current_user', default=None)

async def require_auth():
    user = current_user.get()
    if user is None:
        raise Unauthorized()

async def endpoint():
    await require_auth()
    # ...
```

### 3. Database Sessions

```python
db_session = ContextVar('db_session')

async def get_session():
    return db_session.get()

async def request_handler():
    session = create_session()
    db_session.set(session)
    try:
        await handle()
    finally:
        session.close()
```

### 4. Logging Context

```python
logger_context = ContextVar('logger_context', default={})

def log(level, message):
    context = logger_context.get()
    print(f"{level} {context} {message}")

async def operation():
    ctx = logger_context.get().copy()
    ctx['operation'] = 'process_data'
    logger_context.set(ctx)
    log('INFO', 'Processing...')
```

## Advanced Features

### Context Copying

```python
from contextvars import copy_context

# Copy current context
ctx = copy_context()

# Run function in copied context
result = ctx.run(function, *args)
```

### Manual Context Management

```python
import contextvars

# Create new context
ctx = contextvars.Context()

# Run in context
ctx.run(lambda: print(request_id.get()))
```

### Context Variables as Context Managers

```python
class var_context:
    def __init__(self, var, value):
        self.var = var
        self.value = value
        self.token = None
    
    def __enter__(self):
        self.token = self.var.set(self.value)
    
    def __exit__(self, *args):
        self.var.reset(self.token)

with var_context(request_id, "temp"):
    print(request_id.get())  # "temp"
# Automatically restored
```

## Real-World Patterns

### Web Framework Middleware

```python
request_var = ContextVar('request')

class RequestMiddleware:
    async def __call__(self, request):
        request_var.set(request)
        try:
            return await self.next(request)
        finally:
            # Context auto-cleaned on task completion
            pass

# Anywhere in the code
def get_current_request():
    return request_var.get()
```

### Distributed Tracing

```python
trace_id = ContextVar('trace_id')
span_id = ContextVar('span_id')

async def traced_operation(name):
    parent_span = span_id.get()
    new_span = create_span(parent_span, name)
    span_id.set(new_span)
    
    try:
        await do_work()
    finally:
        end_span(new_span)
```

### Database Transaction Management

```python
transaction = ContextVar('transaction', default=None)

async def atomic():
    txn = begin_transaction()
    transaction.set(txn)
    try:
        yield txn
        commit(txn)
    except:
        rollback(txn)
        raise

async def handler():
    async with atomic():
        await save_user()
        await save_profile()
    # Auto-committed or rolled back
```

## vs threading.local

### threading.local Issues

```python
local = threading.local()

async def task1():
    local.value = "A"
    await asyncio.sleep(0)
    print(local.value)  # Might print "B"!

async def task2():
    local.value = "B"
    await asyncio.sleep(0)
    print(local.value)  # Might print "A"!
```

Both tasks share the same thread's local storage.

### contextvars Solution

```python
value = ContextVar('value')

async def task1():
    value.set("A")
    await asyncio.sleep(0)
    print(value.get())  # Always "A"

async def task2():
    value.set("B")
    await asyncio.sleep(0)
    print(value.get())  # Always "B"
```

Each async task has its own context.

## Best Practices

### 1. Module-Level Declaration

```python
# Good - module level
request_id = ContextVar('request_id')

# Bad - inside function
def handler():
    request_id = ContextVar('request_id')  # New var each call!
```

### 2. Provide Defaults When Reasonable

```python
# Good for optional context
user_id = ContextVar('user_id', default=None)

# Good for required context (forces explicit set)
transaction = ContextVar('transaction')  # No default
```

### 3. Use Descriptive Names

```python
# Good
current_user = ContextVar('current_user')
db_session = ContextVar('db_session')

# Bad
x = ContextVar('x')
data = ContextVar('data')
```

### 4. Clean Up in Finally Blocks

```python
async def handler():
    token = context_var.set(value)
    try:
        await process()
    finally:
        context_var.reset(token)
```

### 5. Document Context Requirements

```python
async def process_order():
    """
    Process an order.
    
    Requires:
        - current_user: User making the order
        - db_session: Active database session
    """
    user = current_user.get()
    session = db_session.get()
```

## Common Pitfalls

### 1. Creating ContextVar in Functions

```python
# Bad - new ContextVar each call
def handler():
    request_id = ContextVar('request_id')
    request_id.set("123")

# Good - module-level
request_id = ContextVar('request_id')

def handler():
    request_id.set("123")
```

### 2. Forgetting Default Can Raise

```python
var = ContextVar('var')  # No default

# This raises LookupError if not set
value = var.get()

# Use fallback or default
value = var.get(None)
```

### 3. Modifying Mutable Defaults

```python
# Dangerous
default_config = {"timeout": 30}
config = ContextVar('config', default=default_config)

# Better - use immutable default
config = ContextVar('config', default=None)
```

### 4. Expecting Cross-Context Sharing

```python
var = ContextVar('var')

def thread_func():
    var.set("value")

thread = threading.Thread(target=thread_func)
thread.start()
thread.join()

# Main thread's context unchanged
print(var.get())  # Still default/unset
```

## Performance

- Fast: ~20ns per get() (CPython 3.11)
- Negligible memory overhead
- No locks (thread-safe by design)
- Scales with number of contexts, not variables

## Type Hints

```python
from contextvars import ContextVar
from typing import Optional

request_id: ContextVar[str] = ContextVar('request_id')
user_id: ContextVar[Optional[int]] = ContextVar('user_id', default=None)

# In functions
def get_request() -> str:
    return request_id.get()
```

## Framework Support

### FastAPI

```python
from starlette.requests import Request

# FastAPI sets request in context automatically
def get_request() -> Request:
    return request_context_var.get()
```

### Starlette

Uses contextvars internally for request/response access.

### aiohttp

```python
# aiohttp uses contextvars
from aiohttp import web

async def handler(request):
    # request available via context
    pass
```

## Further Reading

- [PEP 567 - Context Variables](https://www.python.org/dev/peps/pep-0567/)
- [contextvars Documentation](https://docs.python.org/3/library/contextvars.html)
- [asyncio and Context Variables](https://docs.python.org/3/library/asyncio-task.html#asyncio-context-vars)

## Key Takeaways

✓ Async-safe alternative to `threading.local`  
✓ Each async task gets its own context automatically  
✓ Context inherited by child tasks (but changes don't propagate up)  
✓ Essential for request tracking, auth, logging in async apps  
✓ Modern Python web frameworks rely on this heavily  
✓ Declare context variables at module level  
✓ Provide defaults for optional context  
✓ Fast and lightweight  
✓ If you write async Python, you need to understand this

