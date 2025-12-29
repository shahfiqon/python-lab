"""
Frame Objects (sys._getframe) - Deep Python Techniques Demo
Related to: .notes/10-python-deep-techs.md Section 5

Frame objects provide runtime introspection of Python's call stack. They allow
you to inspect local variables, line numbers, and caller information at runtime.

NOTE: sys._getframe is a private API (leading underscore) but widely used
in production tools like debuggers, profilers, and test frameworks.
"""

import sys
import inspect


def demo_basic_frame_inspection():
    """Basic frame object inspection"""
    print("=" * 60)
    print("DEMO 1: Basic Frame Inspection")
    print("=" * 60)
    
    def inner_function():
        frame = sys._getframe(0)  # Current frame
        print(f"  Function name: {frame.f_code.co_name}")
        print(f"  Filename: {frame.f_code.co_filename}")
        print(f"  Line number: {frame.f_lineno}")
        print(f"  Local variables: {list(frame.f_locals.keys())}")
        
        local_var = "I'm a local variable"
        frame = sys._getframe(0)  # Refresh to see new variable
        print(f"  Updated locals: {list(frame.f_locals.keys())}")
        print(f"  Value of 'local_var': {frame.f_locals['local_var']}")
    
    print("\nInspecting inner_function:")
    inner_function()


def demo_caller_info():
    """Find out who called you"""
    print("\n" + "=" * 60)
    print("DEMO 2: Discovering Your Caller")
    print("=" * 60)
    
    def who_called_me():
        """Returns information about the calling function"""
        frame = sys._getframe(1)  # Caller's frame
        return {
            'function': frame.f_code.co_name,
            'filename': frame.f_code.co_filename,
            'line': frame.f_lineno
        }
    
    def function_a():
        print("  function_a calling who_called_me:")
        info = who_called_me()
        print(f"    Called from: {info['function']} at line {info['line']}")
    
    def function_b():
        print("  function_b calling who_called_me:")
        info = who_called_me()
        print(f"    Called from: {info['function']} at line {info['line']}")
    
    function_a()
    function_b()


def demo_call_stack():
    """Walk the entire call stack"""
    print("\n" + "=" * 60)
    print("DEMO 3: Walking the Call Stack")
    print("=" * 60)
    
    def print_stack():
        """Print the complete call stack"""
        print("  Call stack:")
        frame = sys._getframe(0)
        depth = 0
        while frame is not None:
            code = frame.f_code
            print(f"    [{depth}] {code.co_name} at {code.co_filename}:{frame.f_lineno}")
            frame = frame.f_back
            depth += 1
            if depth > 10:  # Prevent infinite loop
                print("    ... (truncated)")
                break
    
    def level_3():
        print_stack()
    
    def level_2():
        level_3()
    
    def level_1():
        level_2()
    
    print("\nCalling nested functions:")
    level_1()


def demo_local_variable_access():
    """Access caller's local variables"""
    print("\n" + "=" * 60)
    print("DEMO 4: Accessing Caller's Variables")
    print("=" * 60)
    
    def inspect_caller_locals():
        """Inspect the caller's local variables"""
        frame = sys._getframe(1)
        print("  Caller's local variables:")
        for name, value in frame.f_locals.items():
            if not name.startswith('_'):
                print(f"    {name} = {value}")
    
    def example_function():
        x = 10
        y = 20
        message = "Hello from example_function"
        z = x + y
        
        print("\n  example_function calling inspect_caller_locals:")
        inspect_caller_locals()
    
    example_function()


def demo_custom_debugger():
    """Simple debugger using frame inspection"""
    print("\n" + "=" * 60)
    print("DEMO 5: Simple Debugger")
    print("=" * 60)
    
    class SimpleDebugger:
        @staticmethod
        def debug_print(var_name):
            """Print variable from caller's scope with context"""
            frame = sys._getframe(1)
            
            # Get the variable value
            if var_name in frame.f_locals:
                value = frame.f_locals[var_name]
            elif var_name in frame.f_globals:
                value = frame.f_globals[var_name]
            else:
                value = "<not found>"
            
            # Print with context
            print(f"  DEBUG [{frame.f_code.co_name}:{frame.f_lineno}] {var_name} = {value}")
        
        @staticmethod
        def trace():
            """Print current execution context"""
            frame = sys._getframe(1)
            print(f"  TRACE: {frame.f_code.co_name} at line {frame.f_lineno}")
            print(f"         Locals: {list(frame.f_locals.keys())}")
    
    def buggy_function(x, y):
        result = x + y
        SimpleDebugger.debug_print('result')
        SimpleDebugger.trace()
        
        result = result * 2
        SimpleDebugger.debug_print('result')
        
        return result
    
    print("\nDebugging a function:")
    final = buggy_function(5, 3)
    print(f"  Final result: {final}")


def demo_context_manager():
    """Context manager that logs entry/exit with caller info"""
    print("\n" + "=" * 60)
    print("DEMO 6: Context Manager with Caller Tracking")
    print("=" * 60)
    
    class ExecutionTracker:
        def __enter__(self):
            frame = sys._getframe(1)
            self.caller = frame.f_code.co_name
            self.line = frame.f_lineno
            print(f"  → Entering block in {self.caller} at line {self.line}")
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                print(f"  ← Exiting {self.caller} with exception: {exc_type.__name__}")
            else:
                print(f"  ← Exiting {self.caller} normally")
            return False
    
    def example_with_tracker():
        print("\nUsing ExecutionTracker:")
        with ExecutionTracker():
            print("    Doing some work...")
            x = 10 + 20
            print(f"    Computed x = {x}")
    
    example_with_tracker()


def demo_performance_profiler():
    """Simple profiler using frame inspection"""
    print("\n" + "=" * 60)
    print("DEMO 7: Performance Profiler")
    print("=" * 60)
    
    import time
    from functools import wraps
    
    def profile(func):
        """Decorator that profiles function execution"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get caller info
            frame = sys._getframe(1)
            caller = frame.f_code.co_name
            
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            
            print(f"  PROFILE: {func.__name__} (called from {caller})")
            print(f"           Duration: {elapsed*1000:.2f}ms")
            print(f"           Args: {args}, Kwargs: {kwargs}")
            
            return result
        return wrapper
    
    @profile
    def slow_function(n):
        """Simulate slow operation"""
        time.sleep(0.01)
        return sum(range(n))
    
    @profile
    def fast_function(x, y):
        """Fast operation"""
        return x + y
    
    def caller_function():
        slow_function(100)
        fast_function(5, 10)
    
    print("\nProfiling functions:")
    caller_function()


def demo_variable_injection():
    """Inject variables into caller's scope (dangerous!)"""
    print("\n" + "=" * 60)
    print("DEMO 8: Variable Injection (Advanced/Dangerous)")
    print("=" * 60)
    
    def inject_variable(name, value):
        """Inject a variable into the caller's scope"""
        frame = sys._getframe(1)
        frame.f_locals[name] = value
        # Note: This is tricky and doesn't always work reliably
        # It's mainly for demonstration
        print(f"  Attempted to inject '{name}' = {value}")
        print("  (Note: Injection to f_locals is unreliable)")
    
    def example():
        print("\n  Before injection:")
        print(f"    Locals: {list(locals().keys())}")
        
        inject_variable('injected_var', 42)
        
        print("  After injection:")
        print(f"    Locals: {list(locals().keys())}")
        # Note: May or may not contain 'injected_var'
        print("  ⚠ Variable injection to f_locals is unreliable")
        print("  ⚠ This is why it's not recommended for production")
    
    example()


def demo_inspect_comparison():
    """Compare sys._getframe with inspect module"""
    print("\n" + "=" * 60)
    print("DEMO 9: sys._getframe vs inspect module")
    print("=" * 60)
    
    def compare_approaches():
        # Using sys._getframe
        frame = sys._getframe(0)
        print("  Using sys._getframe:")
        print(f"    Function: {frame.f_code.co_name}")
        print(f"    Line: {frame.f_lineno}")
        
        # Using inspect module (built on _getframe)
        print("\n  Using inspect module:")
        print(f"    Function: {inspect.currentframe().f_code.co_name}")
        current_function = inspect.stack()[0]
        print(f"    Frame info: {current_function.function}")
        print(f"    Line: {current_function.lineno}")
        
        print("\n  ✓ inspect is the recommended public API")
        print("  ✓ sys._getframe is lower level but widely used")
    
    compare_approaches()


def demo_practical_logging():
    """Practical example: Smart logging with context"""
    print("\n" + "=" * 60)
    print("DEMO 10: Practical Smart Logger")
    print("=" * 60)
    
    class SmartLogger:
        @staticmethod
        def log(message):
            """Log with automatic context from caller"""
            frame = sys._getframe(1)
            
            # Extract context
            func_name = frame.f_code.co_name
            line_no = frame.f_lineno
            filename = frame.f_code.co_filename.split('/')[-1]
            
            # Find relevant local variables
            locals_str = ", ".join(
                f"{k}={v}" 
                for k, v in list(frame.f_locals.items())[:3]
                if not k.startswith('_')
            )
            
            print(f"  [{filename}:{line_no}] {func_name}() - {message}")
            if locals_str:
                print(f"    Context: {locals_str}")
    
    def process_order(order_id, amount):
        SmartLogger.log("Starting order processing")
        
        total = amount * 1.1  # Add tax
        SmartLogger.log("Calculated total with tax")
        
        status = "completed"
        SmartLogger.log("Order completed")
        
        return total
    
    print("\nProcessing order with smart logging:")
    result = process_order("ORD-123", 100.0)
    print(f"  Final total: ${result:.2f}")


if __name__ == "__main__":
    demo_basic_frame_inspection()
    demo_caller_info()
    demo_call_stack()
    demo_local_variable_access()
    demo_custom_debugger()
    demo_context_manager()
    demo_performance_profiler()
    demo_variable_injection()
    demo_inspect_comparison()
    demo_practical_logging()
    
    print("\n" + "=" * 60)
    print("All frame object demos completed!")
    print("=" * 60)
    print("\n⚠ Remember: sys._getframe is private API")
    print("For production, prefer the 'inspect' module when possible")

