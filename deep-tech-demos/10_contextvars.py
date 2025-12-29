"""
Context Variables (contextvars) - Deep Python Techniques Demo
Related to: .notes/10-python-deep-techs.md Section 10

contextvars provides async-safe context-local state. Unlike threading.local,
it works correctly with async/await and preserves context across async operations.
"""

from contextvars import ContextVar, copy_context
import asyncio
import threading
import time


# Create context variables
request_id = ContextVar('request_id', default='no-request')
user_id = ContextVar('user_id', default=None)


def demo_basic_usage():
    """Basic context variable usage"""
    print("=" * 60)
    print("DEMO 1: Basic Context Variable")
    print("=" * 60)
    
    counter = ContextVar('counter', default=0)
    
    print(f"\n  Initial value: {counter.get()}")
    
    print("\n  Setting value:")
    counter.set(42)
    print(f"    counter.get() = {counter.get()}")
    
    print("\n  Setting again:")
    counter.set(100)
    print(f"    counter.get() = {counter.get()}")


def demo_vs_global():
    """Compare with global variables"""
    print("\n" + "=" * 60)
    print("DEMO 2: Context Variable vs Global")
    print("=" * 60)
    
    # Global variable
    global_value = "initial"
    
    # Context variable
    context_value = ContextVar('context_value', default="initial")
    
    def modify_values():
        global global_value
        global_value = "modified"
        context_value.set("modified")
    
    print("\n  Before modification:")
    print(f"    global_value = {global_value}")
    print(f"    context_value = {context_value.get()}")
    
    print("\n  Calling modify_values():")
    modify_values()
    
    print("\n  After modification:")
    print(f"    global_value = {global_value}")
    print(f"    context_value = {context_value.get()}")
    
    print("\n  ✓ Both changed in the same execution context")


def demo_threading_isolation():
    """Context variables are isolated per execution context"""
    print("\n" + "=" * 60)
    print("DEMO 3: Thread Isolation")
    print("=" * 60)
    
    counter = ContextVar('thread_counter', default=0)
    
    def worker(thread_id, value):
        counter.set(value)
        print(f"  Thread {thread_id}: set to {value}")
        time.sleep(0.1)  # Simulate work
        print(f"  Thread {thread_id}: still {counter.get()}")
    
    print("\n  Starting threads:")
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(i, i * 10))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"\n  Main thread: {counter.get()}")
    print("  ✓ Each thread has its own context")


async def demo_async_isolation():
    """Context variables work correctly with async/await"""
    print("\n" + "=" * 60)
    print("DEMO 4: Async Isolation")
    print("=" * 60)
    
    task_id = ContextVar('task_id', default='none')
    
    async def async_worker(worker_id):
        task_id.set(f"task-{worker_id}")
        print(f"  Worker {worker_id}: set task_id to {task_id.get()}")
        
        await asyncio.sleep(0.1)  # Simulate async work
        
        print(f"  Worker {worker_id}: task_id still {task_id.get()}")
        return task_id.get()
    
    print("\n  Running async tasks:")
    tasks = [async_worker(i) for i in range(3)]
    results = await asyncio.gather(*tasks)
    
    print(f"\n  Results: {results}")
    print("  ✓ Each async task maintained its own context")


def demo_request_tracking():
    """Practical example: Request tracking"""
    print("\n" + "=" * 60)
    print("DEMO 5: Request Tracking (Synchronous)")
    print("=" * 60)
    
    def log(message):
        """Logger that automatically includes request_id"""
        rid = request_id.get()
        print(f"  [{rid}] {message}")
    
    def handle_request(rid):
        request_id.set(rid)
        log("Request started")
        process_request()
        log("Request completed")
    
    def process_request():
        log("Processing...")
        validate_data()
        save_to_database()
    
    def validate_data():
        log("Validating data")
    
    def save_to_database():
        log("Saving to database")
    
    print("\n  Handling request 1:")
    handle_request("req-001")
    
    print("\n  Handling request 2:")
    handle_request("req-002")
    
    print("\n  ✓ Each request automatically tracked throughout call stack")


async def demo_async_request_tracking():
    """Async version of request tracking"""
    print("\n" + "=" * 60)
    print("DEMO 6: Async Request Tracking")
    print("=" * 60)
    
    def log(message):
        """Logger that includes both request_id and user_id"""
        rid = request_id.get()
        uid = user_id.get()
        print(f"  [{rid}] [user:{uid}] {message}")
    
    async def handle_request(rid, uid):
        request_id.set(rid)
        user_id.set(uid)
        log("Request started")
        
        await process_async_request()
        
        log("Request completed")
    
    async def process_async_request():
        log("Processing...")
        await asyncio.sleep(0.01)  # Simulate async work
        log("Still processing...")
    
    print("\n  Handling multiple async requests:")
    await asyncio.gather(
        handle_request("req-A", "user-1"),
        handle_request("req-B", "user-2"),
        handle_request("req-C", "user-3")
    )
    
    print("\n  ✓ Context preserved across async boundaries")


def demo_context_copying():
    """Copy context for task spawning"""
    print("\n" + "=" * 60)
    print("DEMO 7: Copying Context")
    print("=" * 60)
    
    config = ContextVar('config', default={})
    
    def print_config(label):
        print(f"  {label}: config = {config.get()}")
    
    print("\n  Setting config in main context:")
    config.set({"debug": True, "timeout": 30})
    print_config("Main")
    
    print("\n  Copying context:")
    ctx = copy_context()
    
    print("\n  Running in copied context:")
    def modify_in_copy():
        print_config("Before modify")
        config.set({"debug": False, "timeout": 60})
        print_config("After modify")
    
    ctx.run(modify_in_copy)
    
    print("\n  Back in original context:")
    print_config("Original (unchanged)")


def demo_default_values():
    """Using default values"""
    print("\n" + "=" * 60)
    print("DEMO 8: Default Values")
    print("=" * 60)
    
    with_default = ContextVar('with_default', default='default_value')
    without_default = ContextVar('without_default')
    
    print("\n  Variable with default:")
    print(f"    with_default.get() = '{with_default.get()}'")
    
    print("\n  Variable without default:")
    try:
        value = without_default.get()
        print(f"    without_default.get() = {value}")
    except LookupError as e:
        print(f"    ✗ LookupError: {e}")
    
    print("\n  Using get() with fallback:")
    print(f"    without_default.get('fallback') = '{without_default.get('fallback')}'")


def demo_token_reset():
    """Using tokens to reset values"""
    print("\n" + "=" * 60)
    print("DEMO 9: Tokens and Reset")
    print("=" * 60)
    
    counter = ContextVar('counter', default=0)
    
    print(f"\n  Initial: counter = {counter.get()}")
    
    print("\n  Setting to 10:")
    token1 = counter.set(10)
    print(f"    counter = {counter.get()}")
    
    print("\n  Setting to 20:")
    token2 = counter.set(20)
    print(f"    counter = {counter.get()}")
    
    print("\n  Resetting to token1 (value 10):")
    counter.reset(token1)
    print(f"    counter = {counter.get()}")
    
    print("\n  ✓ Tokens allow reverting to previous values")


async def demo_practical_web_app():
    """Practical example: Web application"""
    print("\n" + "=" * 60)
    print("DEMO 10: Web Application Pattern")
    print("=" * 60)
    
    # Context variables for request handling
    request_context = ContextVar('request')
    auth_user = ContextVar('auth_user', default=None)
    
    class Request:
        def __init__(self, path, method):
            self.path = path
            self.method = method
    
    def get_current_request():
        """Get request from context (available anywhere)"""
        return request_context.get()
    
    def get_current_user():
        """Get authenticated user from context"""
        return auth_user.get()
    
    async def authenticate_middleware(request):
        """Middleware that sets auth context"""
        # Simulate authentication
        if "admin" in request.path:
            auth_user.set("admin_user")
        else:
            auth_user.set("guest_user")
    
    async def logging_middleware():
        """Middleware that logs using context"""
        req = get_current_request()
        user = get_current_user()
        print(f"    → {req.method} {req.path} (user: {user})")
    
    async def handle_request(path, method):
        """Request handler"""
        request = Request(path, method)
        request_context.set(request)
        
        await authenticate_middleware(request)
        await logging_middleware()
        
        # Business logic can access context
        await process_business_logic()
    
    async def process_business_logic():
        """Business logic accessing context"""
        req = get_current_request()
        user = get_current_user()
        print(f"      Processing for {user}")
    
    print("\n  Handling multiple requests concurrently:")
    await asyncio.gather(
        handle_request("/api/users", "GET"),
        handle_request("/admin/settings", "POST"),
        handle_request("/api/products", "GET")
    )
    
    print("\n  ✓ Context variables enable clean middleware patterns")
    print("  ✓ No need to pass request through every function call")


if __name__ == "__main__":
    print("Starting context variable demos...\n")
    
    demo_basic_usage()
    demo_vs_global()
    demo_threading_isolation()
    
    # Async demos
    asyncio.run(demo_async_isolation())
    
    demo_request_tracking()
    
    # More async demos
    asyncio.run(demo_async_request_tracking())
    
    demo_context_copying()
    demo_default_values()
    demo_token_reset()
    
    # Final practical example
    asyncio.run(demo_practical_web_app())
    
    print("\n" + "=" * 60)
    print("All contextvars demos completed!")
    print("=" * 60)
    print("\nKey lessons:")
    print("  ✓ Context variables are async-safe (unlike threading.local)")
    print("  ✓ Each execution context has its own values")
    print("  ✓ Perfect for request tracking, logging, auth")
    print("  ✓ Modern Python web frameworks rely on this heavily")

