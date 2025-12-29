"""
Evaluation Order Guarantees - Deep Python Techniques Demo
Related to: .notes/10-python-deep-techs.md Section 4

Python guarantees left-to-right evaluation order for expressions. This is not
true in all languages (C, C++ have undefined behavior here), but Python's
guarantee makes behavior predictable and reliable.
"""


def demo_basic_evaluation_order():
    """Basic left-to-right evaluation"""
    print("=" * 60)
    print("DEMO 1: Basic Left-to-Right Evaluation")
    print("=" * 60)
    
    def f(x):
        print(f"  Called f({x})")
        return x
    
    print("\nEvaluating: f(1) + f(2) * f(3)")
    result = f(1) + f(2) * f(3)
    print(f"  Result: {result}")
    print("\n  Order: f(1), then f(2), then f(3)")
    print("  (Even though * has higher precedence, f(2) is called before f(3))")


def demo_function_arguments():
    """Arguments evaluated left to right"""
    print("\n" + "=" * 60)
    print("DEMO 2: Function Arguments")
    print("=" * 60)
    
    def logger(msg):
        print(f"  Logging: {msg}")
        return msg
    
    def process(a, b, c):
        print(f"  Processing: {a}, {b}, {c}")
        return a + b + c
    
    print("\nCalling: process(logger('first'), logger('second'), logger('third'))")
    result = process(logger('first'), logger('second'), logger('third'))
    print(f"  Result: {result}")
    print("\n✓ Arguments always evaluated left to right")


def demo_boolean_short_circuit():
    """Short-circuit evaluation with guaranteed order"""
    print("\n" + "=" * 60)
    print("DEMO 3: Boolean Short-Circuit Evaluation")
    print("=" * 60)
    
    def check(name, value):
        print(f"  Checking {name}: {value}")
        return value
    
    print("\nTesting: check('A', False) and check('B', True)")
    result = check('A', False) and check('B', True)
    print(f"  Result: {result}")
    print("  ✓ B not evaluated (short-circuited)")
    
    print("\nTesting: check('C', True) and check('D', False)")
    result = check('C', True) and check('D', False)
    print(f"  Result: {result}")
    print("  ✓ Both evaluated (C was True)")
    
    print("\nTesting: check('E', True) or check('F', False)")
    result = check('E', True) or check('F', False)
    print(f"  Result: {result}")
    print("  ✓ F not evaluated (short-circuited)")


def demo_chained_comparisons():
    """Chained comparisons evaluate left to right"""
    print("\n" + "=" * 60)
    print("DEMO 4: Chained Comparisons")
    print("=" * 60)
    
    def get_value(name, value):
        print(f"  Getting {name} = {value}")
        return value
    
    print("\nTesting: 1 < get_value('x', 5) < get_value('y', 10)")
    result = 1 < get_value('x', 5) < get_value('y', 10)
    print(f"  Result: {result}")
    
    print("\nTesting: 1 < get_value('a', 5) < get_value('b', 3)")
    result = 1 < get_value('a', 5) < get_value('b', 3)
    print(f"  Result: {result}")
    print("  ✓ Both values evaluated even though result is False")
    
    print("\nTesting with short-circuit: 10 < get_value('m', 5) < get_value('n', 20)")
    result = 10 < get_value('m', 5) < get_value('n', 20)
    print(f"  Result: {result}")
    print("  ✓ 'n' not evaluated (10 < 5 is already False)")


def demo_assignment_evaluation():
    """Assignment expression evaluation order"""
    print("\n" + "=" * 60)
    print("DEMO 5: Assignment and Augmented Assignment")
    print("=" * 60)
    
    class Tracker:
        def __init__(self, name, value):
            self.name = name
            self.value = value
        
        def __repr__(self):
            return f"Tracker({self.name}={self.value})"
        
        def __add__(self, other):
            print(f"  {self.name}({self.value}) + {other.name}({other.value})")
            return Tracker(f"{self.name}+{other.name}", self.value + other.value)
    
    a = Tracker('a', 5)
    b = Tracker('b', 3)
    
    print("\nEvaluating: a + b")
    c = a + b
    print(f"  Result: {c}")
    
    print("\nAugmented assignment: a += b")
    a += b
    print(f"  Result: {a}")


def demo_list_comprehension_order():
    """List comprehension evaluation order"""
    print("\n" + "=" * 60)
    print("DEMO 6: List Comprehension Evaluation")
    print("=" * 60)
    
    def transform(x):
        print(f"  Transform({x})")
        return x * 2
    
    def condition(x):
        print(f"  Condition({x})")
        return x % 2 == 0
    
    print("\nList comp: [transform(x) for x in [1, 2, 3, 4] if condition(x)]")
    result = [transform(x) for x in [1, 2, 3, 4] if condition(x)]
    print(f"  Result: {result}")
    print("\n  Order: condition checked before transform called")


def demo_dict_evaluation_order():
    """Dictionary evaluation order (Python 3.7+)"""
    print("\n" + "=" * 60)
    print("DEMO 7: Dictionary Evaluation Order")
    print("=" * 60)
    
    def key(name):
        print(f"  Key: {name}")
        return name
    
    def value(val):
        print(f"  Value: {val}")
        return val
    
    print("\nCreating dict with: {key('a'): value(1), key('b'): value(2)}")
    d = {key('a'): value(1), key('b'): value(2)}
    print(f"  Result: {d}")
    print("\n✓ Evaluation order: key('a'), value(1), key('b'), value(2)")
    print("✓ Insertion order preserved (Python 3.7+)")


def demo_exception_safety():
    """Evaluation order guarantees exception safety"""
    print("\n" + "=" * 60)
    print("DEMO 8: Exception Safety")
    print("=" * 60)
    
    def safe_operation(name, will_fail=False):
        print(f"  Executing {name}")
        if will_fail:
            raise ValueError(f"{name} failed")
        return name
    
    print("\nTrying: safe_operation('A') + safe_operation('B', True) + safe_operation('C')")
    try:
        result = safe_operation('A') + safe_operation('B', True) + safe_operation('C')
    except ValueError as e:
        print(f"  Exception: {e}")
        print("  ✓ C never executed (B raised exception first)")
    
    print("\n✓ Left-to-right order guarantees predictable exception behavior")


def demo_walrus_operator():
    """Walrus operator (:=) with evaluation order"""
    print("\n" + "=" * 60)
    print("DEMO 9: Walrus Operator (Assignment Expression)")
    print("=" * 60)
    
    def expensive_computation(x):
        print(f"  Computing with {x}")
        return x * x
    
    print("\nUsing walrus in if statement:")
    data = [1, 2, 3, 4, 5]
    
    print("Checking: if (result := expensive_computation(3)) > 5:")
    if (result := expensive_computation(3)) > 5:
        print(f"    Result {result} is greater than 5")
    else:
        print(f"    Result {result} is not greater than 5")
    
    print("\nUsing walrus in list comprehension:")
    print("[y for x in [1, 2, 3] if (y := expensive_computation(x)) > 2]")
    results = [y for x in [1, 2, 3] if (y := expensive_computation(x)) > 2]
    print(f"  Results: {results}")


def demo_side_effects():
    """Side effects with guaranteed evaluation order"""
    print("\n" + "=" * 60)
    print("DEMO 10: Side Effects and Logging")
    print("=" * 60)
    
    logs = []
    
    def log_and_return(name, value):
        logs.append(name)
        print(f"  Logged: {name}")
        return value
    
    print("\nExpression with side effects:")
    result = (
        log_and_return('step1', 10) +
        log_and_return('step2', 20) +
        log_and_return('step3', 30)
    )
    print(f"  Result: {result}")
    print(f"  Log order: {logs}")
    print("\n✓ Logs always appear in predictable order")
    print("✓ This is why Python is trusted for financial/audit systems")


def demo_comparison_with_c():
    """Compare with undefined behavior in C"""
    print("\n" + "=" * 60)
    print("DEMO 11: Why This Matters (vs C/C++)") 
    print("=" * 60)
    
    print("\nIn C/C++, this has undefined behavior:")
    print("  int i = 1;")
    print("  int result = i++ + i++;  // UNDEFINED!")
    print("  Could be 2, 3, or 4 depending on compiler")
    
    print("\nIn Python, behavior is always defined:")
    
    class Counter:
        def __init__(self):
            self.value = 1
        
        def increment(self):
            result = self.value
            self.value += 1
            print(f"    increment() -> {result}, counter now {self.value}")
            return result
    
    counter = Counter()
    result = counter.increment() + counter.increment()
    print(f"  Result: {result}")
    print("  ✓ Always 1 + 2 = 3 (left-to-right guaranteed)")


if __name__ == "__main__":
    demo_basic_evaluation_order()
    demo_function_arguments()
    demo_boolean_short_circuit()
    demo_chained_comparisons()
    demo_assignment_evaluation()
    demo_list_comprehension_order()
    demo_dict_evaluation_order()
    demo_exception_safety()
    demo_walrus_operator()
    demo_side_effects()
    demo_comparison_with_c()
    
    print("\n" + "=" * 60)
    print("All evaluation order demos completed!")
    print("=" * 60)

