# Evaluation Order Guarantees

## Overview

Python guarantees **strict left-to-right evaluation order** for all expressions. This is a formal part of the language specification, making Python more predictable and safer than languages like C or C++ where evaluation order can be undefined.

## The Guarantee

> **Python Language Specification:** "Python evaluates expressions from left to right."

This applies to:
- Arithmetic operations
- Function calls
- Boolean operations
- Assignments
- Comprehensions
- Everything

## Why This Matters

### In Other Languages

```c
// C/C++ - UNDEFINED BEHAVIOR
int i = 0;
int result = i++ + i++;  // Could be 0, 1, or 2!
```

The C standard says this is "undefined behavior" - the compiler can do anything.

### In Python

```python
# Python - DEFINED BEHAVIOR
i = 0
result = f(i) + g(i)  # Always calls f first, then g
```

**Guaranteed.** Always. Forever.

## Key Implications

### 1. Predictable Side Effects

```python
def log_and_compute(name, value):
    log(name)  # Side effect
    return value

result = log_and_compute('A', 1) + log_and_compute('B', 2)
# Logs always appear: A, then B
```

This makes logging, debugging, and auditing predictable.

### 2. Safe Exception Handling

```python
result = safe_operation() + might_fail() + never_called()
# If might_fail() raises, never_called() is never executed
```

No mystery side effects from functions that "shouldn't have been called."

### 3. Reliable Short-Circuiting

```python
if expensive_check() and another_check():
    pass
# another_check() only runs if expensive_check() returns True
```

You can rely on this for optimization and safety.

### 4. Consistent Chained Comparisons

```python
if 0 < x < 10:  # Evaluates left to right
    pass
# Equivalent to: (0 < x) and (x < 10)
# x only evaluated once
```

## Examples in Practice

### Financial Systems

```python
# Banking transaction
balance = (
    get_starting_balance() +
    process_deposits() -
    process_withdrawals()
)
```

The order matters for audit trails. Python guarantees it.

### Data Pipelines

```python
result = (
    fetch_data() |
    transform() |
    validate() |
    save()
)
```

Each stage depends on the previous. Order is critical.

### Logging Systems

```python
logger.info(
    f"User {get_user()} performed {get_action()} at {get_timestamp()}"
)
```

Logs appear in the order written, always.

## Operator Precedence vs Evaluation Order

**Important distinction:**

```python
result = f(1) + f(2) * f(3)
```

- **Precedence:** Determines the result (1 + (2 * 3))
- **Evaluation order:** Determines the call order (f(1), f(2), f(3))

Python guarantees left-to-right evaluation **regardless of precedence**.

## Short-Circuit Evaluation

### `and` Operator

```python
a and b and c
```

Evaluates left to right, stops at first falsy value:
1. Evaluate `a`
2. If falsy, return `a` (don't evaluate `b` or `c`)
3. Otherwise, evaluate `b`
4. If falsy, return `b` (don't evaluate `c`)
5. Otherwise, evaluate and return `c`

### `or` Operator

```python
a or b or c
```

Evaluates left to right, stops at first truthy value:
1. Evaluate `a`
2. If truthy, return `a` (don't evaluate `b` or `c`)
3. Otherwise, evaluate `b`
4. If truthy, return `b` (don't evaluate `c`)
5. Otherwise, evaluate and return `c`

## Function Arguments

```python
func(arg1(), arg2(), arg3())
```

Arguments are **always** evaluated left to right before the function is called.

This includes:
- Positional arguments
- Keyword arguments (keys evaluated left to right, then values)
- `*args` and `**kwargs` expansions

## Comprehensions and Generators

```python
[f(x) for x in iterable if condition(x)]
```

Evaluation order:
1. Iterate through `iterable` left to right
2. For each `x`, evaluate `condition(x)`
3. If true, evaluate `f(x)` and include in result

## Dictionary Order (Python 3.7+)

```python
d = {key1(): value1(), key2(): value2()}
```

Guaranteed order:
1. Evaluate `key1()`
2. Evaluate `value1()`
3. Evaluate `key2()`
4. Evaluate `value2()`

Insertion order is also preserved in the dict.

## Assignment Expressions (Walrus Operator)

```python
if (n := expensive_function()) > 0:
    use(n)
```

The assignment happens as part of the evaluation:
1. Call `expensive_function()`
2. Assign to `n`
3. Compare with `0`

## Chained Assignments

```python
a = b = c = expression()
```

Evaluation order:
1. Evaluate `expression()` **once**
2. Assign to `c`
3. Assign to `b`
4. Assign to `a`

All variables reference the same object.

## Augmented Assignment

```python
x += f()
```

Evaluation order:
1. Evaluate `x` (look up the variable)
2. Evaluate `f()`
3. Perform `x = x + f()`

This matters when `x` is a complex expression:

```python
array[index()] += value()
```

1. Evaluate `index()` **once**
2. Evaluate `value()`
3. Update `array[index_result]`

## Exception Guarantees

```python
result = f1() + f2() + f3()
```

If `f2()` raises an exception:
- `f1()` has already executed (and its side effects are done)
- `f3()` will **never** execute

This guarantee makes exception handling predictable.

## Performance Implications

The evaluation order guarantee means:

1. **No reordering optimizations:** The compiler can't rearrange expressions
2. **Predictable overhead:** You know exactly what gets called
3. **Safe for side effects:** You can rely on order for logging, metrics, etc.

Trade-off: Slightly less optimization potential, but way more predictable.

## Best Practices

### 1. Use Evaluation Order for Safety

```python
if obj is not None and obj.method():
    # Safe: obj.method() only called if obj is not None
    pass
```

### 2. Document Side-Effect Dependencies

```python
def process():
    """
    Process data in order:
    1. Validates input
    2. Logs action
    3. Performs operation
    
    Order is critical for audit trail.
    """
    return validate() and log() and operate()
```

### 3. Avoid Relying on Order for Performance

Don't write code that depends on specific timing:

```python
# Bad: Relies on evaluation order for performance
result = quick_check() and slow_check()  # OK
result = slow_check() and quick_check()  # Slower but works

# Better: Be explicit
if quick_check():
    result = slow_check()
```

### 4. Use Short-Circuiting Wisely

```python
# Good: Prevent errors
if user is not None and user.is_admin():
    pass

# Good: Optimize
if cache.has(key) or expensive_compute(key):
    pass
```

## Common Misconceptions

### "Precedence determines evaluation order"

**FALSE.** Precedence determines how to group operations, not the order they execute.

```python
result = a() + b() * c()
# Calls: a(), b(), c() (left to right)
# Computes: a() + (b() * c()) (precedence)
```

### "Python can optimize away function calls"

**MOSTLY FALSE.** Python can't skip calls that might have side effects, which is nearly all functions.

### "Evaluation order doesn't matter for pure functions"

**TRUE** for correctness, but you can still rely on it for debugging and logging.

## Further Reading

- [Python Language Reference - Evaluation Order](https://docs.python.org/3/reference/expressions.html#evaluation-order)
- [PEP 8 - Expression Evaluation](https://www.python.org/dev/peps/pep-0008/)
- "Fluent Python" by Luciano Ramalho - Chapter on expression evaluation

## Key Takeaways

✓ Python guarantees strict left-to-right evaluation  
✓ No undefined behavior like C/C++  
✓ Safe for side effects (logging, metrics, auditing)  
✓ Predictable exception handling  
✓ Short-circuit evaluation is reliable  
✓ You can depend on this guarantee in production code  
✓ This is why Python is trusted for financial and critical systems

