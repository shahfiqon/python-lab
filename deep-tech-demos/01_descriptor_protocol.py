"""
Descriptor Protocol - Deep Python Techniques Demo
Related to: .notes/10-python-deep-techs.md Section 1

The descriptor protocol is the mechanism behind @property, classmethod, staticmethod,
and much more. It allows you to customize attribute access at the class level.
"""


class Typed:
    """Type-checking descriptor"""
    def __init__(self, name, expected_type):
        self.name = name
        self.expected_type = expected_type

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"{self.name} must be {self.expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        del instance.__dict__[self.name]


class LazyProperty:
    """Descriptor that computes value once and caches it"""
    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        # Compute once and cache
        if self.name not in instance.__dict__:
            instance.__dict__[self.name] = self.func(instance)
        return instance.__dict__[self.name]


class Validator:
    """Generic validation descriptor"""
    def __init__(self, name, validator_func, error_msg):
        self.name = name
        self.validator_func = validator_func
        self.error_msg = error_msg

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if not self.validator_func(value):
            raise ValueError(f"{self.name}: {self.error_msg}")
        instance.__dict__[self.name] = value


def demo_basic_typed():
    """Basic type-checking descriptor"""
    print("=" * 60)
    print("DEMO 1: Type-Checking Descriptor")
    print("=" * 60)
    
    class User:
        age = Typed("age", int)
        name = Typed("name", str)
        
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    # Valid usage
    user = User("Alice", 30)
    print(f"Created user: {user.name}, age {user.age}")
    
    # Type validation works
    user.age = 31
    print(f"Updated age to: {user.age}")
    
    # Try invalid type
    try:
        user.age = "thirty-one"
    except TypeError as e:
        print(f"✓ Type error caught: {e}")
    
    # Try another invalid type
    try:
        user.name = 12345
    except TypeError as e:
        print(f"✓ Type error caught: {e}")


def demo_lazy_property():
    """Lazy computation with descriptors"""
    print("\n" + "=" * 60)
    print("DEMO 2: Lazy Property Descriptor")
    print("=" * 60)
    
    class DataProcessor:
        def __init__(self, data):
            self.data = data
            self.computation_count = 0
        
        @LazyProperty
        def expensive_result(self):
            """This will only compute once"""
            self.computation_count += 1
            print(f"  Computing expensive result (call #{self.computation_count})...")
            return sum(x ** 2 for x in self.data)
    
    processor = DataProcessor([1, 2, 3, 4, 5])
    
    print("First access:")
    result1 = processor.expensive_result
    print(f"  Result: {result1}")
    
    print("\nSecond access (should use cached value):")
    result2 = processor.expensive_result
    print(f"  Result: {result2}")
    
    print("\nThird access:")
    result3 = processor.expensive_result
    print(f"  Result: {result3}")
    
    print(f"\n✓ Computation ran only {processor.computation_count} time(s)")


def demo_validator():
    """Custom validation with descriptors"""
    print("\n" + "=" * 60)
    print("DEMO 3: Validation Descriptor")
    print("=" * 60)
    
    class Account:
        balance = Validator(
            "balance",
            lambda x: x >= 0,
            "Balance cannot be negative"
        )
        
        email = Validator(
            "email",
            lambda x: isinstance(x, str) and "@" in x,
            "Email must contain @"
        )
        
        def __init__(self, email, balance):
            self.email = email
            self.balance = balance
    
    # Valid account
    account = Account("user@example.com", 1000)
    print(f"Created account: {account.email}, balance ${account.balance}")
    
    # Valid withdrawal
    account.balance = 500
    print(f"After withdrawal: ${account.balance}")
    
    # Try negative balance
    try:
        account.balance = -100
    except ValueError as e:
        print(f"✓ Validation error caught: {e}")
    
    # Try invalid email
    try:
        account.email = "invalid-email"
    except ValueError as e:
        print(f"✓ Validation error caught: {e}")


def demo_comparison_with_property():
    """Compare descriptor with @property"""
    print("\n" + "=" * 60)
    print("DEMO 4: Descriptor vs @property")
    print("=" * 60)
    
    print("With @property (per-class boilerplate):")
    
    class PersonProperty:
        def __init__(self, name, age):
            self._name = name
            self._age = age
        
        @property
        def name(self):
            return self._name
        
        @name.setter
        def name(self, value):
            if not isinstance(value, str):
                raise TypeError("name must be str")
            self._name = value
        
        @property
        def age(self):
            return self._age
        
        @age.setter
        def age(self, value):
            if not isinstance(value, int):
                raise TypeError("age must be int")
            self._age = value
    
    print("  - Requires separate @property for each attribute")
    print("  - Lots of repetitive code")
    print("  - Hard to maintain consistency")
    
    print("\nWith Descriptors (reusable):")
    
    class PersonDescriptor:
        name = Typed("name", str)
        age = Typed("age", int)
        
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    print("  - Single descriptor class handles all attributes")
    print("  - Validation logic centralized")
    print("  - Easily reusable across classes")
    
    # Both work the same
    p1 = PersonProperty("Bob", 25)
    p2 = PersonDescriptor("Bob", 25)
    
    print(f"\n✓ Both approaches work: {p1.name}, {p2.name}")


def demo_descriptor_access_on_class():
    """Understanding descriptor access from class vs instance"""
    print("\n" + "=" * 60)
    print("DEMO 5: Descriptor Access - Class vs Instance")
    print("=" * 60)
    
    class RevealingDescriptor:
        def __init__(self, name):
            self.name = name
        
        def __get__(self, instance, owner):
            if instance is None:
                print(f"  Accessed from class {owner.__name__}")
                return self
            else:
                print(f"  Accessed from instance of {owner.__name__}")
                return instance.__dict__.get(self.name, "not set")
        
        def __set__(self, instance, value):
            print(f"  Setting {self.name} to {value}")
            instance.__dict__[self.name] = value
    
    class Example:
        attr = RevealingDescriptor("attr")
    
    print("Access from class:")
    descriptor = Example.attr
    print(f"  Got: {descriptor}")
    
    print("\nAccess from instance:")
    obj = Example()
    value = obj.attr
    print(f"  Got: {value}")
    
    print("\nSetting value:")
    obj.attr = "hello"
    
    print("\nAccess again:")
    value = obj.attr
    print(f"  Got: {value}")


if __name__ == "__main__":
    demo_basic_typed()
    demo_lazy_property()
    demo_validator()
    demo_comparison_with_property()
    demo_descriptor_access_on_class()
    
    print("\n" + "=" * 60)
    print("All descriptor demos completed!")
    print("=" * 60)

