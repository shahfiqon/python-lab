"""
__init_subclass__ - Deep Python Techniques Demo
Related to: .notes/10-python-deep-techs.md Section 2

__init_subclass__ is called when a class is subclassed. It's a cleaner alternative
to metaclasses for many common use cases like plugin registration, validation,
and automatic configuration.
"""


def demo_plugin_registry():
    """Auto-register plugins when they're defined"""
    print("=" * 60)
    print("DEMO 1: Plugin Registry")
    print("=" * 60)
    
    class PluginBase:
        registry = {}
        
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            # Auto-register every subclass
            PluginBase.registry[cls.__name__] = cls
            print(f"  Registered plugin: {cls.__name__}")
        
        def process(self, data):
            raise NotImplementedError
    
    print("\nDefining plugins...")
    
    class JSONPlugin(PluginBase):
        def process(self, data):
            return f"Processing {data} as JSON"
    
    class XMLPlugin(PluginBase):
        def process(self, data):
            return f"Processing {data} as XML"
    
    class CSVPlugin(PluginBase):
        def process(self, data):
            return f"Processing {data} as CSV"
    
    print(f"\nRegistry contains: {list(PluginBase.registry.keys())}")
    
    # Use plugins dynamically
    print("\nUsing plugins:")
    for name, plugin_cls in PluginBase.registry.items():
        plugin = plugin_cls()
        result = plugin.process("data.txt")
        print(f"  {name}: {result}")


def demo_validation_on_creation():
    """Validate class definition at creation time"""
    print("\n" + "=" * 60)
    print("DEMO 2: Class Definition Validation")
    print("=" * 60)
    
    class APIEndpoint:
        required_attributes = ['path', 'method', 'handler']
        
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            
            # Validate that required attributes are defined
            missing = []
            for attr in cls.required_attributes:
                if not hasattr(cls, attr):
                    missing.append(attr)
            
            if missing:
                raise TypeError(
                    f"{cls.__name__} must define: {', '.join(missing)}"
                )
            
            print(f"  ✓ {cls.__name__} validated successfully")
    
    print("\nDefining valid endpoint:")
    
    class UserEndpoint(APIEndpoint):
        path = "/api/users"
        method = "GET"
        handler = lambda self, req: {"users": []}
    
    print("\nTrying to define invalid endpoint:")
    
    try:
        class BadEndpoint(APIEndpoint):
            path = "/api/bad"
            # Missing 'method' and 'handler'
    except TypeError as e:
        print(f"  ✗ Error caught: {e}")


def demo_parameterized_subclass():
    """Use keyword arguments in subclass definition"""
    print("\n" + "=" * 60)
    print("DEMO 3: Parameterized Subclassing")
    print("=" * 60)
    
    class ConfigurableBase:
        def __init_subclass__(cls, db_table=None, cache_timeout=None, **kwargs):
            super().__init_subclass__(**kwargs)
            cls.db_table = db_table or cls.__name__.lower()
            cls.cache_timeout = cache_timeout or 300
            print(f"  Configured {cls.__name__}:")
            print(f"    - db_table: {cls.db_table}")
            print(f"    - cache_timeout: {cls.cache_timeout}s")
    
    print("\nDefining models with custom configuration:")
    
    class User(ConfigurableBase, db_table="users_table", cache_timeout=600):
        pass
    
    class Product(ConfigurableBase, db_table="products"):
        # Uses default cache_timeout
        pass
    
    class Order(ConfigurableBase):
        # Uses all defaults
        pass
    
    print(f"\nAccessing configuration:")
    print(f"  User table: {User.db_table}, cache: {User.cache_timeout}s")
    print(f"  Product table: {Product.db_table}, cache: {Product.cache_timeout}s")
    print(f"  Order table: {Order.db_table}, cache: {Order.cache_timeout}s")


def demo_method_wrapping():
    """Automatically wrap methods at class creation"""
    print("\n" + "=" * 60)
    print("DEMO 4: Automatic Method Wrapping")
    print("=" * 60)
    
    class LoggedClass:
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            
            # Wrap all public methods with logging
            for name, method in cls.__dict__.items():
                if callable(method) and not name.startswith('_'):
                    setattr(cls, name, cls._wrap_with_logging(name, method))
            
            print(f"  Wrapped methods in {cls.__name__}")
        
        @staticmethod
        def _wrap_with_logging(method_name, method):
            def wrapper(self, *args, **kwargs):
                print(f"    → Calling {method_name}{args}")
                result = method(self, *args, **kwargs)
                print(f"    ← {method_name} returned {result}")
                return result
            return wrapper
    
    print("\nDefining logged class:")
    
    class Calculator(LoggedClass):
        def add(self, a, b):
            return a + b
        
        def multiply(self, a, b):
            return a * b
    
    print("\nUsing calculator (all calls logged automatically):")
    calc = Calculator()
    calc.add(5, 3)
    calc.multiply(4, 7)


def demo_inheritance_tree():
    """Track class hierarchy automatically"""
    print("\n" + "=" * 60)
    print("DEMO 5: Automatic Hierarchy Tracking")
    print("=" * 60)
    
    class TrackedBase:
        _hierarchy = {}
        
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            
            # Track parent-child relationships
            parents = [base for base in cls.__bases__ 
                      if issubclass(base, TrackedBase)]
            
            cls._hierarchy[cls.__name__] = {
                'class': cls,
                'parents': [p.__name__ for p in parents],
                'children': []
            }
            
            # Update parent's children list
            for parent in parents:
                if parent.__name__ in cls._hierarchy:
                    cls._hierarchy[parent.__name__]['children'].append(cls.__name__)
            
            print(f"  Tracked: {cls.__name__} (parents: {cls._hierarchy[cls.__name__]['parents']})")
    
    print("\nBuilding class hierarchy:")
    
    class Animal(TrackedBase):
        pass
    
    class Mammal(Animal):
        pass
    
    class Bird(Animal):
        pass
    
    class Dog(Mammal):
        pass
    
    class Cat(Mammal):
        pass
    
    class Eagle(Bird):
        pass
    
    print("\nHierarchy map:")
    for name, info in TrackedBase._hierarchy.items():
        print(f"  {name}:")
        if info['parents']:
            print(f"    Parents: {', '.join(info['parents'])}")
        if info['children']:
            print(f"    Children: {', '.join(info['children'])}")


def demo_vs_metaclass():
    """Show why __init_subclass__ is often better than metaclasses"""
    print("\n" + "=" * 60)
    print("DEMO 6: __init_subclass__ vs Metaclass")
    print("=" * 60)
    
    print("With metaclass (complex):")
    print("""
    class PluginMeta(type):
        def __new__(mcs, name, bases, namespace):
            cls = super().__new__(mcs, name, bases, namespace)
            # Registration logic here
            return cls
    
    class Plugin(metaclass=PluginMeta):
        pass
    """)
    print("  - Requires understanding metaclasses")
    print("  - More complex to debug")
    print("  - Can conflict with other metaclasses")
    
    print("\nWith __init_subclass__ (simple):")
    print("""
    class Plugin:
        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            # Registration logic here
    """)
    print("  - No metaclass magic")
    print("  - Easy to understand and maintain")
    print("  - Works well with multiple inheritance")
    
    print("\n✓ Use __init_subclass__ unless you need metaclass features")


if __name__ == "__main__":
    demo_plugin_registry()
    demo_validation_on_creation()
    demo_parameterized_subclass()
    demo_method_wrapping()
    demo_inheritance_tree()
    demo_vs_metaclass()
    
    print("\n" + "=" * 60)
    print("All __init_subclass__ demos completed!")
    print("=" * 60)

