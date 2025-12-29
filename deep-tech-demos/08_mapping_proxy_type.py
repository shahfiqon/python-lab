"""
MappingProxyType - Deep Python Techniques Demo
Related to: .notes/10-python-deep-techs.md Section 8

MappingProxyType creates a read-only view of a dictionary. It's truly immutable
at runtime, preventing accidental modifications.
"""

from types import MappingProxyType


def demo_basic_usage():
    """Basic MappingProxyType usage"""
    print("=" * 60)
    print("DEMO 1: Basic Read-Only Dictionary")
    print("=" * 60)
    
    # Original mutable dict
    config = {"debug": False, "timeout": 30, "retries": 3}
    print(f"  Original config: {config}")
    
    # Create read-only view
    readonly_config = MappingProxyType(config)
    print(f"  Read-only view: {readonly_config}")
    
    print("\n  Accessing values:")
    print(f"    readonly_config['debug'] = {readonly_config['debug']}")
    print(f"    readonly_config.get('timeout') = {readonly_config.get('timeout')}")
    
    print("\n  Trying to modify:")
    try:
        readonly_config['debug'] = True
    except TypeError as e:
        print(f"    ✓ Error: {e}")
    
    try:
        readonly_config['new_key'] = 'value'
    except TypeError as e:
        print(f"    ✓ Error: {e}")
    
    try:
        del readonly_config['timeout']
    except TypeError as e:
        print(f"    ✓ Error: {e}")


def demo_underlying_changes():
    """Changes to underlying dict are visible"""
    print("\n" + "=" * 60)
    print("DEMO 2: Dynamic View (Reflects Changes)")
    print("=" * 60)
    
    data = {"count": 0, "status": "idle"}
    readonly = MappingProxyType(data)
    
    print(f"  Initial readonly view: {readonly}")
    
    print("\n  Modifying underlying dict:")
    data["count"] = 10
    data["status"] = "active"
    
    print(f"  Updated readonly view: {readonly}")
    print("  ✓ MappingProxyType reflects changes to underlying dict")
    
    print("\n  Adding to underlying dict:")
    data["new_field"] = "appeared"
    print(f"  Updated readonly view: {readonly}")


def demo_vs_frozen():
    """Compare with other immutability patterns"""
    print("\n" + "=" * 60)
    print("DEMO 3: MappingProxyType vs Other Patterns")
    print("=" * 60)
    
    print("1. Plain dict (mutable):")
    plain = {"a": 1, "b": 2}
    plain["c"] = 3  # Works
    print(f"   Can modify: {plain}")
    
    print("\n2. Tuple of items (immutable but awkward):")
    frozen = (("a", 1), ("b", 2))
    print(f"   Immutable: {frozen}")
    print("   But no dict interface (no frozen['a'])")
    
    print("\n3. dict.copy() (snapshot, not protection):")
    original = {"a": 1, "b": 2}
    snapshot = original.copy()
    snapshot["c"] = 3  # Can still modify the copy
    print(f"   Original: {original}")
    print(f"   Snapshot (modified): {snapshot}")
    
    print("\n4. MappingProxyType (read-only view):")
    source = {"a": 1, "b": 2}
    proxy = MappingProxyType(source)
    try:
        proxy["c"] = 3
        print("   ✗ Should have failed!")
    except TypeError:
        print("   ✓ Truly read-only")
        print(f"   Proxy: {proxy}")


def demo_config_system():
    """Practical example: Configuration system"""
    print("\n" + "=" * 60)
    print("DEMO 4: Configuration System")
    print("=" * 60)
    
    class Config:
        def __init__(self):
            self._config = {
                "database_url": "postgresql://localhost/db",
                "cache_timeout": 300,
                "debug": False,
                "max_connections": 10
            }
            # Expose read-only view
            self.settings = MappingProxyType(self._config)
        
        def update(self, **kwargs):
            """Controlled update through API"""
            print(f"  Admin updating config: {kwargs}")
            self._config.update(kwargs)
        
        def reset(self):
            """Reset to defaults"""
            print("  Resetting config to defaults")
            self._config.clear()
            self._config.update({
                "database_url": "postgresql://localhost/db",
                "cache_timeout": 300,
                "debug": False,
                "max_connections": 10
            })
    
    config = Config()
    
    print("\nApplication code (read-only access):")
    print(f"  Database URL: {config.settings['database_url']}")
    print(f"  Cache timeout: {config.settings['cache_timeout']}")
    
    print("\nTrying to modify from application:")
    try:
        config.settings['debug'] = True
    except TypeError:
        print("  ✓ Cannot modify - protection works!")
    
    print("\nAdmin updating config:")
    config.update(debug=True, max_connections=20)
    print(f"  New debug value: {config.settings['debug']}")
    print(f"  New max_connections: {config.settings['max_connections']}")


def demo_class_namespace():
    """Understanding class __dict__ as MappingProxyType"""
    print("\n" + "=" * 60)
    print("DEMO 5: Class Namespace Protection")
    print("=" * 60)
    
    class Example:
        class_var = 42
        
        def method(self):
            pass
    
    print("  Class __dict__ type:")
    print(f"    {type(Example.__dict__)}")
    print(f"    {Example.__dict__}")
    
    print("\n  Accessing class attributes:")
    print(f"    Example.__dict__['class_var'] = {Example.__dict__['class_var']}")
    print(f"    'method' in Example.__dict__ = {'method' in Example.__dict__}")
    
    print("\n  Trying to modify class.__dict__:")
    try:
        Example.__dict__['new_attr'] = 'value'
    except TypeError as e:
        print(f"    ✓ Protected: {e}")
    
    print("\n  ✓ Python uses MappingProxyType to protect class namespaces")


def demo_api_response():
    """Practical example: API response wrapper"""
    print("\n" + "=" * 60)
    print("DEMO 6: Immutable API Response")
    print("=" * 60)
    
    class APIResponse:
        def __init__(self, data):
            self._data = data
            self.data = MappingProxyType(data)
        
        def __repr__(self):
            return f"APIResponse({self.data})"
    
    # Simulate API call
    response_data = {
        "user_id": 123,
        "username": "alice",
        "email": "alice@example.com",
        "is_active": True
    }
    
    response = APIResponse(response_data)
    
    print("  API Response:")
    print(f"    {response}")
    
    print("\n  Accessing data:")
    print(f"    User: {response.data['username']}")
    print(f"    Email: {response.data['email']}")
    
    print("\n  Trying to modify response data:")
    try:
        response.data['username'] = 'hacker'
    except TypeError:
        print("    ✓ Response data protected from modification")
    
    print("\n  ✓ Clients can't accidentally corrupt response data")


def demo_nested_protection():
    """Protection is shallow, not deep"""
    print("\n" + "=" * 60)
    print("DEMO 7: Shallow Protection (Important!)") 
    print("=" * 60)
    
    data = {
        "simple": 42,
        "nested": {"inner": "value"}
    }
    
    proxy = MappingProxyType(data)
    
    print("  Original data:")
    print(f"    {proxy}")
    
    print("\n  Top-level is protected:")
    try:
        proxy["new_key"] = "value"
        print("    ✗ Should have failed!")
    except TypeError:
        print("    ✓ Cannot add top-level keys")
    
    print("\n  But nested dicts are NOT protected:")
    proxy["nested"]["inner"] = "MODIFIED"
    print(f"    proxy['nested']['inner'] = {proxy['nested']['inner']}")
    print("    ⚠ Nested structures can still be modified!")
    
    print("\n  Solution for deep immutability:")
    print("    - Recursively wrap nested dicts")
    print("    - Use immutable data structures (frozendict, tuple)")
    print("    - Copy nested structures as immutable types")


def demo_performance():
    """Performance characteristics"""
    print("\n" + "=" * 60)
    print("DEMO 8: Performance Characteristics")
    print("=" * 60)
    
    import time
    
    data = {f"key_{i}": i for i in range(10000)}
    proxy = MappingProxyType(data)
    
    # Read performance
    start = time.time()
    for _ in range(1000):
        _ = data["key_500"]
    dict_time = time.time() - start
    
    start = time.time()
    for _ in range(1000):
        _ = proxy["key_500"]
    proxy_time = time.time() - start
    
    print(f"  Dict read time: {dict_time*1000:.3f}ms")
    print(f"  MappingProxyType read time: {proxy_time*1000:.3f}ms")
    print(f"  Overhead: {((proxy_time/dict_time - 1) * 100):.1f}%")
    
    print("\n  ✓ MappingProxyType has minimal read overhead")
    print("  ✓ No additional memory for the proxy itself")
    print("  ✓ Just a lightweight wrapper around the dict")


def demo_iteration():
    """Iteration support"""
    print("\n" + "=" * 60)
    print("DEMO 9: Iteration and Dict Methods")
    print("=" * 60)
    
    data = {"a": 1, "b": 2, "c": 3}
    proxy = MappingProxyType(data)
    
    print("  Supports all read operations:")
    
    print("\n  Keys:")
    print(f"    {list(proxy.keys())}")
    
    print("\n  Values:")
    print(f"    {list(proxy.values())}")
    
    print("\n  Items:")
    print(f"    {list(proxy.items())}")
    
    print("\n  Iteration:")
    for key in proxy:
        print(f"    {key} = {proxy[key]}")
    
    print("\n  'in' operator:")
    print(f"    'a' in proxy = {'a' in proxy}")
    print(f"    'z' in proxy = {'z' in proxy}")
    
    print("\n  len():")
    print(f"    len(proxy) = {len(proxy)}")
    
    print("\n  get() with default:")
    print(f"    proxy.get('x', 'default') = {proxy.get('x', 'default')}")
    
    print("\n  ✓ Full read-only dict interface")


def demo_use_cases():
    """Summary of use cases"""
    print("\n" + "=" * 60)
    print("DEMO 10: When to Use MappingProxyType")
    print("=" * 60)
    
    print("\n  ✓ Configuration systems")
    print("    - Expose read-only config to application code")
    print("    - Controlled updates through admin interface")
    
    print("\n  ✓ API responses")
    print("    - Prevent accidental modification of response data")
    print("    - Ensure data integrity")
    
    print("\n  ✓ Caching results")
    print("    - Protect cached data from modification")
    print("    - Share cache safely across threads")
    
    print("\n  ✓ Default values")
    print("    - Provide read-only defaults")
    print("    - Users can't accidentally change defaults")
    
    print("\n  ✓ Class-level constants")
    print("    - Python already uses this for class.__dict__")
    print("    - You can use it for your own class-level data")
    
    print("\n  ✓ Anywhere you need 'defensive copying' but want efficiency")
    print("    - No copy overhead")
    print("    - Still protects from modification")


if __name__ == "__main__":
    demo_basic_usage()
    demo_underlying_changes()
    demo_vs_frozen()
    demo_config_system()
    demo_class_namespace()
    demo_api_response()
    demo_nested_protection()
    demo_performance()
    demo_iteration()
    demo_use_cases()
    
    print("\n" + "=" * 60)
    print("All MappingProxyType demos completed!")
    print("=" * 60)
    print("\nKey takeaways:")
    print("  ✓ Truly read-only at runtime")
    print("  ✓ Dynamic view (reflects underlying changes)")
    print("  ✓ Minimal overhead")
    print("  ✓ Python uses it internally for class.__dict__")

