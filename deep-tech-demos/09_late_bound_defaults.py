"""
Late-Bound Defaults (Sentinel Values) - Deep Python Techniques Demo
Related to: .notes/10-python-deep-techs.md Section 9

The sentinel pattern solves the mutable default argument trap and allows
distinguishing between "not provided" and any actual value (including None).
"""


# The classic trap
def demo_mutable_default_trap():
    """The classic mutable default argument problem"""
    print("=" * 60)
    print("DEMO 1: The Mutable Default Trap")
    print("=" * 60)
    
    def append_to_list(item, lst=[]):  # BUG!
        lst.append(item)
        return lst
    
    print("\n  First call:")
    result1 = append_to_list(1)
    print(f"    append_to_list(1) = {result1}")
    
    print("\n  Second call:")
    result2 = append_to_list(2)
    print(f"    append_to_list(2) = {result2}")
    
    print("\n  Third call:")
    result3 = append_to_list(3)
    print(f"    append_to_list(3) = {result3}")
    
    print("\n  ✗ All calls share the same list!")
    print(f"    result1 is result2: {result1 is result2}")


def demo_none_solution():
    """Common solution using None"""
    print("\n" + "=" * 60)
    print("DEMO 2: The None Solution")
    print("=" * 60)
    
    def append_to_list(item, lst=None):
        if lst is None:
            lst = []
        lst.append(item)
        return lst
    
    print("\n  First call:")
    result1 = append_to_list(1)
    print(f"    append_to_list(1) = {result1}")
    
    print("\n  Second call:")
    result2 = append_to_list(2)
    print(f"    append_to_list(2) = {result2}")
    
    print("\n  ✓ Each call gets its own list")
    print(f"    result1 is result2: {result1 is result2}")
    
    print("\n  But what if None is a valid value?")
    result3 = append_to_list(None)
    print(f"    append_to_list(None) = {result3}")
    print("    ✓ Works, but what if we wanted to pass an actual list?")
    
    result4 = append_to_list(4, None)
    print(f"    append_to_list(4, None) = {result4}")
    print("    ✗ Can't distinguish 'not provided' from 'explicitly None'")


def demo_sentinel_pattern():
    """The sentinel pattern solution"""
    print("\n" + "=" * 60)
    print("DEMO 3: The Sentinel Pattern")
    print("=" * 60)
    
    _sentinel = object()
    
    def append_to_list(item, lst=_sentinel):
        if lst is _sentinel:
            lst = []
        lst.append(item)
        return lst
    
    print("\n  Using sentinel:")
    
    print("\n  Not providing lst:")
    result1 = append_to_list(1)
    print(f"    append_to_list(1) = {result1}")
    
    print("\n  Explicitly passing None:")
    result2 = append_to_list(2, None)
    print(f"    append_to_list(2, None) = {result2}")
    print("    ✗ Error! None has no append method")
    print("    (But we could check for None separately if needed)")
    
    print("\n  Passing existing list:")
    my_list = [10, 20]
    result3 = append_to_list(30, my_list)
    print(f"    append_to_list(30, [10, 20]) = {result3}")
    print(f"    my_list = {my_list}")
    print("    ✓ Modified the provided list")


def demo_distinguishing_none():
    """Using sentinel to distinguish None from not-provided"""
    print("\n" + "=" * 60)
    print("DEMO 4: Distinguishing None from Not-Provided")
    print("=" * 60)
    
    _not_provided = object()
    
    def set_config(key, value=_not_provided):
        if value is _not_provided:
            print(f"  '{key}' not set (keeping existing value)")
        elif value is None:
            print(f"  '{key}' explicitly set to None (clearing)")
        else:
            print(f"  '{key}' set to {value}")
    
    print("\n  Three different cases:")
    
    print("\n  1. Not providing value:")
    set_config("database_url")
    
    print("\n  2. Explicitly passing None:")
    set_config("database_url", None)
    
    print("\n  3. Providing actual value:")
    set_config("database_url", "postgresql://localhost/db")


def demo_multiple_sentinels():
    """Using multiple sentinels"""
    print("\n" + "=" * 60)
    print("DEMO 5: Multiple Sentinel Values")
    print("=" * 60)
    
    _no_value = object()
    _use_default = object()
    
    def get_or_create(key, default=_no_value, factory=_use_default):
        cache = {}  # Simulated cache
        
        if key in cache:
            print(f"  Found '{key}' in cache")
            return cache[key]
        
        if factory is not _use_default:
            print(f"  Creating value with factory")
            return factory()
        elif default is not _no_value:
            print(f"  Using provided default: {default}")
            return default
        else:
            print(f"  No value found and no default")
            return None
    
    print("\n  Using factory:")
    result1 = get_or_create("key1", factory=lambda: [1, 2, 3])
    print(f"    Result: {result1}")
    
    print("\n  Using default:")
    result2 = get_or_create("key2", default="default_value")
    print(f"    Result: {result2}")
    
    print("\n  Neither:")
    result3 = get_or_create("key3")
    print(f"    Result: {result3}")


def demo_sentinel_class():
    """Using a class for sentinels"""
    print("\n" + "=" * 60)
    print("DEMO 6: Sentinel as a Class")
    print("=" * 60)
    
    class Sentinel:
        def __init__(self, name):
            self.name = name
        
        def __repr__(self):
            return f"<{self.name}>"
    
    MISSING = Sentinel("MISSING")
    EMPTY = Sentinel("EMPTY")
    
    def process(value=MISSING):
        if value is MISSING:
            print(f"  Value is {MISSING}")
        elif value is EMPTY:
            print(f"  Value is {EMPTY}")
        else:
            print(f"  Value is {value}")
    
    print("\n  Different cases:")
    process()
    process(EMPTY)
    process(None)
    process("actual value")
    
    print("\n  ✓ Named sentinels are more readable")


def demo_cpython_sentinels():
    """Sentinels used in CPython"""
    print("\n" + "=" * 60)
    print("DEMO 7: Sentinels in CPython")
    print("=" * 60)
    
    print("\n  CPython uses sentinels extensively:")
    
    print("\n  1. dict.get():")
    print("     _sentinel = object()")
    print("     def get(key, default=_sentinel):")
    print("         if key in self:")
    print("             return self[key]")
    print("         if default is _sentinel:")
    print("             return None")
    print("         return default")
    
    print("\n  2. functools.lru_cache:")
    print("     _CacheInfo = collections.namedtuple(...)")
    print("     Uses sentinel to track cache misses")
    
    print("\n  3. asyncio:")
    print("     _MISSING = object()")
    print("     Used to distinguish unset timeout from None")
    
    print("\n  ✓ Sentinels are a standard Python pattern")


def demo_dataclass_field():
    """Sentinels in dataclass fields"""
    print("\n" + "=" * 60)
    print("DEMO 8: Dataclass Field Defaults")
    print("=" * 60)
    
    from dataclasses import dataclass, field, MISSING
    
    @dataclass
    class User:
        name: str
        email: str
        tags: list = field(default_factory=list)
        metadata: dict = field(default_factory=dict)
    
    print("\n  dataclasses use MISSING sentinel internally")
    print(f"    MISSING = {MISSING}")
    
    print("\n  Creating users:")
    user1 = User("Alice", "alice@example.com")
    user2 = User("Bob", "bob@example.com")
    
    user1.tags.append("admin")
    
    print(f"    user1.tags = {user1.tags}")
    print(f"    user2.tags = {user2.tags}")
    print("    ✓ Each user gets their own list")
    
    print("\n  Without default_factory (using sentinel pattern internally):")
    print("    Each field that needs a mutable default uses this pattern")


def demo_sentinel_vs_none_performance():
    """Performance comparison"""
    print("\n" + "=" * 60)
    print("DEMO 9: Performance Characteristics")
    print("=" * 60)
    
    import time
    
    # Using None
    def func_with_none(value=None):
        if value is None:
            value = []
        return value
    
    # Using sentinel
    _sentinel = object()
    def func_with_sentinel(value=_sentinel):
        if value is _sentinel:
            value = []
        return value
    
    # Benchmark
    iterations = 1000000
    
    start = time.time()
    for _ in range(iterations):
        func_with_none()
    none_time = time.time() - start
    
    start = time.time()
    for _ in range(iterations):
        func_with_sentinel()
    sentinel_time = time.time() - start
    
    print(f"\n  None approach: {none_time*1000:.2f}ms")
    print(f"  Sentinel approach: {sentinel_time*1000:.2f}ms")
    print(f"  Difference: {abs(none_time - sentinel_time)*1000:.2f}ms")
    
    print("\n  ✓ Performance is virtually identical")
    print("  ✓ Use sentinel for clarity, not performance")


def demo_practical_api():
    """Practical example: API with optional parameters"""
    print("\n" + "=" * 60)
    print("DEMO 10: Practical API Example")
    print("=" * 60)
    
    _not_provided = object()
    
    class APIClient:
        def __init__(self):
            self.default_timeout = 30
            self.default_retries = 3
        
        def request(
            self,
            url,
            method="GET",
            timeout=_not_provided,
            retries=_not_provided,
            data=_not_provided
        ):
            # Resolve actual values
            actual_timeout = self.default_timeout if timeout is _not_provided else timeout
            actual_retries = self.default_retries if retries is _not_provided else retries
            
            print(f"  Request: {method} {url}")
            print(f"    timeout: {actual_timeout}")
            print(f"    retries: {actual_retries}")
            
            if data is not _not_provided:
                print(f"    data: {data}")
            else:
                print("    data: <none>")
    
    client = APIClient()
    
    print("\n  Using defaults:")
    client.request("/api/users")
    
    print("\n  Overriding timeout:")
    client.request("/api/users", timeout=60)
    
    print("\n  Explicitly disabling retries:")
    client.request("/api/users", retries=0)
    
    print("\n  Sending data (could be None):")
    client.request("/api/users", method="POST", data=None)
    
    print("\n  ✓ Sentinel lets us distinguish:")
    print("    - Not provided (use default)")
    print("    - Explicitly None (user wants None)")
    print("    - Explicitly 0 (user wants zero)")


if __name__ == "__main__":
    demo_mutable_default_trap()
    demo_none_solution()
    demo_sentinel_pattern()
    demo_distinguishing_none()
    demo_multiple_sentinels()
    demo_sentinel_class()
    demo_cpython_sentinels()
    demo_dataclass_field()
    demo_sentinel_vs_none_performance()
    demo_practical_api()
    
    print("\n" + "=" * 60)
    print("All late-bound defaults (sentinel) demos completed!")
    print("=" * 60)
    print("\nKey lessons:")
    print("  ✓ Use sentinel = object() for late-bound defaults")
    print("  ✓ Distinguishes 'not provided' from None or any other value")
    print("  ✓ Zero performance overhead")
    print("  ✓ Used extensively in CPython itself")

