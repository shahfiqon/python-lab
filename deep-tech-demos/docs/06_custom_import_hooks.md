# Custom Import Hooks

## Overview

Python's `import` statement is not just a keyword - it's a fully customizable protocol. Custom import hooks let you control what gets imported, transform code during import, create virtual modules, and implement sophisticated import behaviors.

## The Import System

When you write `import foo`, Python:
1. Checks `sys.modules` (already imported?)
2. Iterates through `sys.meta_path` (meta path finders)
3. Each finder gets a chance to handle the import
4. Returns the module or raises `ImportError`

## `sys.meta_path`

The list of **meta path finders** that Python consults for imports:

```python
import sys
print(sys.meta_path)
# [
#   <class '_frozen_importlib.BuiltinImporter'>,
#   <class '_frozen_importlib.FrozenImporter'>,
#   <class '_frozen_importlib_external.PathFinder'>
# ]
```

You can insert your own finders at the beginning for highest priority.

## Creating an Import Hook

### Basic Structure

```python
import importlib.abc
from importlib.machinery import ModuleSpec

class MyFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        # fullname: 'package.module'
        # Return ModuleSpec to handle, or None to pass
        if should_handle(fullname):
            return ModuleSpec(fullname, MyLoader())
        return None

class MyLoader(importlib.abc.Loader):
    def create_module(self, spec):
        return None  # Use default module creation
    
    def exec_module(self, module):
        # Initialize the module here
        module.some_attribute = "value"
```

### Installing the Hook

```python
finder = MyFinder()
sys.meta_path.insert(0, finder)  # Highest priority

# Do imports...

sys.meta_path.remove(finder)  # Clean up
```

## Common Use Cases

### 1. Import Blocking

Prevent specific modules from being imported:

```python
class ImportBlocker(importlib.abc.MetaPathFinder):
    def __init__(self, blocked):
        self.blocked = set(blocked)
    
    def find_spec(self, fullname, path, target=None):
        if fullname in self.blocked:
            raise ImportError(f"{fullname} is blocked")
        return None
```

**Use cases:**
- Security sandboxes
- Testing (prevent network/filesystem access)
- Enforcing architectural boundaries

### 2. Import Logging

Track all import activity:

```python
class ImportLogger(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        log(f"Importing {fullname}")
        return None  # Let normal import proceed
```

**Use cases:**
- Debugging import issues
- Performance profiling
- Dependency analysis

### 3. Dynamic Module Creation

Create modules without files:

```python
class VirtualFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname.startswith('virtual_'):
            return ModuleSpec(fullname, VirtualLoader())
        return None

class VirtualLoader(importlib.abc.Loader):
    def create_module(self, spec):
        return None
    
    def exec_module(self, module):
        module.data = "I don't exist on disk!"
```

**Use cases:**
- Configuration modules generated at runtime
- Testing with mock modules
- Plugin systems

### 4. Import Redirection

Redirect one module to another:

```python
class Redirector(importlib.abc.MetaPathFinder):
    def __init__(self, redirects):
        self.redirects = redirects
    
    def find_spec(self, fullname, path, target=None):
        if fullname in self.redirects:
            return importlib.util.find_spec(self.redirects[fullname])
        return None
```

**Use cases:**
- Compatibility layers
- Deprecated module migrations
- Mock replacements for testing

### 5. Lazy Loading

Defer module loading until actually used:

```python
class LazyModule:
    def __init__(self, name):
        self._name = name
        self._module = None
    
    def _load(self):
        if self._module is None:
            self._module = importlib.import_module(self._name)
        return self._module
    
    def __getattr__(self, attr):
        return getattr(self._load(), attr)
```

**Use cases:**
- Reduce startup time
- Conditional imports
- Large optional dependencies

### 6. Code Transformation

Transform source code during import:

```python
class TransformingLoader(importlib.abc.Loader):
    def exec_module(self, module):
        source = get_source(module.__name__)
        transformed = transform_code(source)
        exec(transformed, module.__dict__)
```

**Use cases:**
- Macro systems
- Code instrumentation
- Automatic optimization

## Real-World Examples

### pytest

Rewrites assert statements to provide detailed failure messages:

```python
assert a == b
# Transformed to show: "1 == 2" instead of just "AssertionError"
```

### Coverage.py

Instruments code during import to track execution:

```python
# Each line gets: coverage.track(filename, lineno)
```

### Hot Reload Systems

Detect file changes and reload modules:

```python
class HotReloadFinder:
    def find_spec(self, fullname, path, target=None):
        if file_changed(fullname):
            reload_module(fullname)
```

### Import Freezers (PyInstaller, cx_Freeze)

Bundle Python code into executables by providing frozen imports.

### Django

Uses import hooks for:
- App auto-discovery
- Settings module management
- URL configuration loading

## Best Practices

### 1. Always Return `None` for Unhandled Imports

```python
def find_spec(self, fullname, path, target=None):
    if not_my_responsibility(fullname):
        return None  # Let other finders handle it
    # Handle the import
```

### 2. Clean Up After Yourself

```python
finder = MyFinder()
sys.meta_path.insert(0, finder)
try:
    # Do stuff
finally:
    sys.meta_path.remove(finder)
```

### 3. Use Context Managers

```python
class ImportHook:
    def __enter__(self):
        self.finder = MyFinder()
        sys.meta_path.insert(0, self.finder)
        return self
    
    def __exit__(self, *args):
        sys.meta_path.remove(self.finder)

with ImportHook():
    import my_module  # Uses custom hook
# Hook automatically cleaned up
```

### 4. Be Careful with Performance

Import hooks run for **every** import, including:
- Standard library
- Third-party packages
- Submodules

Keep `find_spec` fast!

### 5. Handle Edge Cases

```python
def find_spec(self, fullname, path, target=None):
    # Handle package imports
    if fullname.endswith('.__init__'):
        pass
    
    # Handle relative imports
    if path is not None:
        pass
    
    # Handle namespace packages
    if is_namespace_package(fullname):
        pass
```

## Common Pitfalls

### 1. Forgetting to Clean Up

```python
# Bad
sys.meta_path.insert(0, MyFinder())
# Finder persists forever!

# Good
finder = MyFinder()
sys.meta_path.insert(0, finder)
# ... use it ...
sys.meta_path.remove(finder)
```

### 2. Infinite Recursion

```python
class BadFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        import some_module  # Triggers another import!
        # This can cause infinite recursion
```

Import dependencies before installing the hook.

### 3. Not Checking `sys.modules`

```python
# Modules are cached in sys.modules
# Your hook won't run for already-imported modules
if 'my_module' in sys.modules:
    del sys.modules['my_module']  # Force re-import
```

### 4. Modifying Global State

Import hooks affect the **entire process**, including:
- Other libraries
- The REPL
- Test runners

Be surgical and clean up properly.

### 5. Thread Safety

Import hooks must be thread-safe if your application is multi-threaded.

## Advanced Techniques

### Import Hooks for Testing

```python
@contextmanager
def mock_imports(**mocks):
    """Replace imports with mocks"""
    class MockFinder(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path, target=None):
            if fullname in mocks:
                # Return mock module
                pass
    
    finder = MockFinder()
    sys.meta_path.insert(0, finder)
    try:
        yield
    finally:
        sys.meta_path.remove(finder)

with mock_imports(requests=MockRequests()):
    # 'import requests' returns MockRequests
    pass
```

### Namespace Packages

Allow splitting a package across multiple directories:

```python
# project1/myns/module_a.py
# project2/myns/module_b.py

import myns.module_a  # From project1
import myns.module_b  # From project2
```

### Source Code Transformation

```python
import ast

class ASTTransformer(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        # Modify the AST
        return node

class TransformingLoader:
    def exec_module(self, module):
        source = get_source(module)
        tree = ast.parse(source)
        tree = ASTTransformer().visit(tree)
        code = compile(tree, module.__file__, 'exec')
        exec(code, module.__dict__)
```

## Security Considerations

Import hooks are powerful and can be dangerous:

1. **Validate input:** Don't trust module names
2. **Whitelist, don't blacklist:** It's easy to forget dangerous modules
3. **Isolate:** Use separate processes for untrusted code
4. **Audit:** Log all import attempts in security-sensitive contexts

## Performance Considerations

- `find_spec` is called for every import
- Keep it fast (< 1ms)
- Cache results when possible
- Avoid expensive operations (filesystem I/O, network)

## Debugging Import Hooks

### Enable Import Verbosity

```bash
python -v script.py  # Shows all imports
```

### Print sys.meta_path

```python
import sys
for finder in sys.meta_path:
    print(type(finder))
```

### Use `-X importtime`

```bash
python -X importtime script.py  # Profile import times
```

## Further Reading

- [PEP 302 - New Import Hooks](https://www.python.org/dev/peps/pep-0302/)
- [PEP 451 - ModuleSpec](https://www.python.org/dev/peps/pep-0451/)
- [importlib Documentation](https://docs.python.org/3/library/importlib.html)
- [Python Import System](https://docs.python.org/3/reference/import.html)

## Key Takeaways

✓ `import` is a customizable protocol, not just a keyword  
✓ `sys.meta_path` contains the list of meta path finders  
✓ Insert custom finders at position 0 for highest priority  
✓ Return `None` from `find_spec` to pass to next finder  
✓ Always clean up by removing finders when done  
✓ Import hooks affect the entire process  
✓ Used by debuggers, test frameworks, and hot-reload systems  
✓ Keep `find_spec` fast - it's called for every import  
✓ Great for: blocking, logging, mocking, code transformation

