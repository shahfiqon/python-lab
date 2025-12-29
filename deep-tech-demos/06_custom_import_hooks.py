"""
Custom Import Hooks - Deep Python Techniques Demo
Related to: .notes/10-python-deep-techs.md Section 6

Python's import system is completely customizable through import hooks. This allows
you to control what gets imported, transform code during import, or even create
modules dynamically.
"""

import sys
import importlib.abc
import importlib.util
from importlib.machinery import ModuleSpec


def demo_basic_import_blocker():
    """Block specific imports"""
    print("=" * 60)
    print("DEMO 1: Import Blocker")
    print("=" * 60)
    
    class ImportBlocker(importlib.abc.MetaPathFinder):
        def __init__(self, blocked_modules):
            self.blocked_modules = set(blocked_modules)
        
        def find_spec(self, fullname, path, target=None):
            if fullname in self.blocked_modules:
                print(f"  ✗ Blocked import of '{fullname}'")
                raise ImportError(f"Import of '{fullname}' is not allowed")
            return None  # Let other finders handle it
    
    # Install the blocker
    blocker = ImportBlocker(['json', 'os'])
    sys.meta_path.insert(0, blocker)
    
    print("\nTrying to import allowed modules:")
    try:
        import sys as sys_test
        print("  ✓ 'sys' imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed: {e}")
    
    print("\nTrying to import blocked modules:")
    try:
        import json
        print("  ✗ 'json' should have been blocked!")
    except ImportError as e:
        print(f"  ✓ Blocked: {e}")
    
    try:
        import os
        print("  ✗ 'os' should have been blocked!")
    except ImportError as e:
        print(f"  ✓ Blocked: {e}")
    
    # Clean up
    sys.meta_path.remove(blocker)
    print("\n  Import blocker removed")


def demo_import_logger():
    """Log all import attempts"""
    print("\n" + "=" * 60)
    print("DEMO 2: Import Logger")
    print("=" * 60)
    
    class ImportLogger(importlib.abc.MetaPathFinder):
        def __init__(self):
            self.imports = []
        
        def find_spec(self, fullname, path, target=None):
            self.imports.append(fullname)
            print(f"  → Importing: {fullname}")
            return None  # Let normal import proceed
    
    logger = ImportLogger()
    sys.meta_path.insert(0, logger)
    
    print("\nImporting some modules:")
    import datetime
    import collections
    
    print(f"\n  Total imports logged: {len(logger.imports)}")
    print(f"  Modules: {logger.imports[:10]}")  # Show first 10
    
    # Clean up
    sys.meta_path.remove(logger)


def demo_dynamic_module_creation():
    """Create modules dynamically without files"""
    print("\n" + "=" * 60)
    print("DEMO 3: Dynamic Module Creation")
    print("=" * 60)
    
    class DynamicModuleFinder(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path, target=None):
            if fullname.startswith('dynamic_'):
                print(f"  Creating dynamic module: {fullname}")
                return ModuleSpec(fullname, DynamicModuleLoader())
            return None
    
    class DynamicModuleLoader(importlib.abc.Loader):
        def create_module(self, spec):
            return None  # Use default module creation
        
        def exec_module(self, module):
            # Add dynamic content to the module
            module.message = "I'm a dynamically created module!"
            module.value = 42
            
            def greet(name):
                return f"Hello {name} from {module.__name__}!"
            
            module.greet = greet
            print(f"  ✓ Initialized {module.__name__}")
    
    finder = DynamicModuleFinder()
    sys.meta_path.insert(0, finder)
    
    print("\nImporting dynamic modules:")
    import dynamic_test_module
    print(f"  message: {dynamic_test_module.message}")
    print(f"  value: {dynamic_test_module.value}")
    print(f"  greet('World'): {dynamic_test_module.greet('World')}")
    
    import dynamic_another_module
    print(f"  another.message: {dynamic_another_module.message}")
    
    # Clean up
    sys.meta_path.remove(finder)
    # Remove from sys.modules
    if 'dynamic_test_module' in sys.modules:
        del sys.modules['dynamic_test_module']
    if 'dynamic_another_module' in sys.modules:
        del sys.modules['dynamic_another_module']


def demo_import_deprecation():
    """Warn on deprecated module imports"""
    print("\n" + "=" * 60)
    print("DEMO 4: Deprecation Warnings")
    print("=" * 60)
    
    import warnings
    
    class DeprecationChecker(importlib.abc.MetaPathFinder):
        def __init__(self, deprecated_modules):
            self.deprecated_modules = deprecated_modules
        
        def find_spec(self, fullname, path, target=None):
            if fullname in self.deprecated_modules:
                message = self.deprecated_modules[fullname]
                warnings.warn(
                    f"Module '{fullname}' is deprecated: {message}",
                    DeprecationWarning,
                    stacklevel=2
                )
            return None  # Continue with normal import
    
    checker = DeprecationChecker({
        'old_module': 'Use new_module instead',
        'legacy_api': 'Removed in version 2.0'
    })
    sys.meta_path.insert(0, checker)
    
    print("\nImporting deprecated module (simulated):")
    # We'll simulate this since we don't have actual old_module
    print("  import old_module")
    print("  ⚠ DeprecationWarning: Module 'old_module' is deprecated: Use new_module instead")
    
    # Clean up
    sys.meta_path.remove(checker)


def demo_import_redirect():
    """Redirect imports to different modules"""
    print("\n" + "=" * 60)
    print("DEMO 5: Import Redirection")
    print("=" * 60)
    
    class ImportRedirector(importlib.abc.MetaPathFinder):
        def __init__(self, redirects):
            self.redirects = redirects
        
        def find_spec(self, fullname, path, target=None):
            if fullname in self.redirects:
                new_name = self.redirects[fullname]
                print(f"  Redirecting '{fullname}' → '{new_name}'")
                # Import the target module
                return importlib.util.find_spec(new_name)
            return None
    
    redirector = ImportRedirector({
        'mymath': 'math',  # Redirect mymath to math
        'myjson': 'json'   # Redirect myjson to json
    })
    sys.meta_path.insert(0, redirector)
    
    print("\nImporting with redirection:")
    import mymath
    print(f"  mymath.pi = {mymath.pi}")
    print(f"  mymath.sqrt(16) = {mymath.sqrt(16)}")
    
    # Clean up
    sys.meta_path.remove(redirector)
    if 'mymath' in sys.modules:
        del sys.modules['mymath']


def demo_lazy_import():
    """Lazy module loading"""
    print("\n" + "=" * 60)
    print("DEMO 6: Lazy Import System")
    print("=" * 60)
    
    class LazyModule:
        def __init__(self, name):
            self._name = name
            self._module = None
            print(f"  LazyModule created for '{name}' (not loaded yet)")
        
        def _load(self):
            if self._module is None:
                print(f"  Loading '{self._name}' now...")
                self._module = importlib.import_module(self._name)
            return self._module
        
        def __getattr__(self, name):
            return getattr(self._load(), name)
    
    print("\nCreating lazy imports:")
    lazy_math = LazyModule('math')
    lazy_random = LazyModule('random')
    
    print("\nModules created but not loaded yet")
    print("\nNow accessing lazy_math.pi:")
    print(f"  pi = {lazy_math.pi}")
    
    print("\nNow accessing lazy_random.randint:")
    print(f"  random number = {lazy_random.randint(1, 10)}")


def demo_namespace_packages():
    """Understanding namespace packages"""
    print("\n" + "=" * 60)
    print("DEMO 7: Namespace Package Finder")
    print("=" * 60)
    
    class NamespacePackageFinder(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path, target=None):
            if fullname.startswith('myns.'):
                print(f"  Found namespace package: {fullname}")
                # Create a namespace package spec
                spec = ModuleSpec(fullname, None, is_package=True)
                return spec
            return None
    
    print("\nThis demo shows the concept of namespace packages")
    print("Namespace packages allow splitting a package across directories")
    print("\nExample structure:")
    print("  project1/myns/module_a.py")
    print("  project2/myns/module_b.py")
    print("\n  Both contribute to the 'myns' namespace")


def demo_import_profiler():
    """Profile import times"""
    print("\n" + "=" * 60)
    print("DEMO 8: Import Time Profiler")
    print("=" * 60)
    
    import time
    
    class ImportProfiler(importlib.abc.MetaPathFinder):
        def __init__(self):
            self.times = {}
        
        def find_spec(self, fullname, path, target=None):
            start = time.time()
            # Let normal import happen, but we'll track the timing
            result = None
            for finder in sys.meta_path[1:]:  # Skip ourselves
                if hasattr(finder, 'find_spec'):
                    result = finder.find_spec(fullname, path, target)
                    if result:
                        break
            
            elapsed = (time.time() - start) * 1000
            self.times[fullname] = elapsed
            
            if elapsed > 0.1:  # Only log slow imports (>0.1ms)
                print(f"  {fullname}: {elapsed:.2f}ms")
            
            return result
    
    profiler = ImportProfiler()
    sys.meta_path.insert(0, profiler)
    
    print("\nImporting modules with profiling:")
    import hashlib
    import pathlib
    
    print(f"\n  Profiled {len(profiler.times)} imports")
    
    # Clean up
    sys.meta_path.remove(profiler)


def demo_security_sandbox():
    """Sandboxed imports for security"""
    print("\n" + "=" * 60)
    print("DEMO 9: Security Sandbox")
    print("=" * 60)
    
    class SecureFinder(importlib.abc.MetaPathFinder):
        def __init__(self, allowed_modules):
            self.allowed_modules = set(allowed_modules)
        
        def find_spec(self, fullname, path, target=None):
            # Check if module or parent package is allowed
            parts = fullname.split('.')
            for i in range(len(parts)):
                module_name = '.'.join(parts[:i+1])
                if module_name in self.allowed_modules:
                    return None  # Allow normal import
            
            # Not in whitelist
            print(f"  ✗ Security: Blocked '{fullname}'")
            raise ImportError(f"Module '{fullname}' not in security whitelist")
    
    print("\nCreating secure sandbox (whitelist: math, datetime, collections)")
    secure = SecureFinder(['math', 'datetime', 'collections'])
    
    # We won't actually install it to avoid breaking the demo
    print("  (Demo simulated - not actually installed)")
    print("\n  In a real sandbox:")
    print("    import math      # ✓ Allowed")
    print("    import datetime  # ✓ Allowed")
    print("    import os        # ✗ Blocked")
    print("    import sys       # ✗ Blocked")
    print("\n  Used in: Testing, plugin systems, sandboxed execution")


def demo_meta_path_inspection():
    """Inspect the current meta path"""
    print("\n" + "=" * 60)
    print("DEMO 10: Inspecting sys.meta_path")
    print("=" * 60)
    
    print("\nCurrent import finders in sys.meta_path:")
    for i, finder in enumerate(sys.meta_path):
        print(f"  [{i}] {finder.__class__.__name__}")
        print(f"      {finder.__class__.__module__}.{finder.__class__.__name__}")
    
    print("\n  These finders are checked in order for each import")
    print("  Custom finders inserted at [0] have highest priority")


if __name__ == "__main__":
    demo_basic_import_blocker()
    demo_import_logger()
    demo_dynamic_module_creation()
    demo_import_deprecation()
    demo_import_redirect()
    demo_lazy_import()
    demo_namespace_packages()
    demo_import_profiler()
    demo_security_sandbox()
    demo_meta_path_inspection()
    
    print("\n" + "=" * 60)
    print("All custom import hook demos completed!")
    print("=" * 60)
    print("\n⚠ Remember: Import hooks affect the entire process")
    print("Always clean up (remove from sys.meta_path) when done")

