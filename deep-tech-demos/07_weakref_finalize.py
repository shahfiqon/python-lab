"""
weakref.finalize - Deep Python Techniques Demo
Related to: .notes/10-python-deep-techs.md Section 7

weakref.finalize provides reliable object finalization without the pitfalls
of __del__. It's the recommended way to clean up resources when objects are
garbage collected.
"""

import weakref
import gc
import time


def demo_basic_finalize():
    """Basic weakref.finalize usage"""
    print("=" * 60)
    print("DEMO 1: Basic Finalization")
    print("=" * 60)
    
    class Resource:
        def __init__(self, name):
            self.name = name
            print(f"  Created resource: {name}")
            # Register cleanup function
            weakref.finalize(self, self._cleanup, name)
        
        @staticmethod
        def _cleanup(name):
            print(f"  Cleaning up resource: {name}")
    
    print("\nCreating resource:")
    resource = Resource("DatabaseConnection")
    
    print("\nDeleting resource:")
    del resource
    gc.collect()
    print("  ✓ Cleanup called automatically")


def demo_vs_del():
    """Compare finalize with __del__"""
    print("\n" + "=" * 60)
    print("DEMO 2: finalize vs __del__")
    print("=" * 60)
    
    print("With __del__ (unreliable):")
    
    class ResourceWithDel:
        def __init__(self, name):
            self.name = name
            print(f"  Created: {name}")
        
        def __del__(self):
            print(f"  __del__ called for: {self.name}")
    
    obj1 = ResourceWithDel("obj1")
    obj2 = ResourceWithDel("obj2")
    
    # Create circular reference
    obj1.ref = obj2
    obj2.ref = obj1
    
    print("  Created circular reference: obj1 ↔ obj2")
    del obj1, obj2
    gc.collect()
    print("  (Circular refs may delay __del__ or prevent it entirely)")
    
    print("\nWith weakref.finalize (reliable):")
    
    class ResourceWithFinalize:
        def __init__(self, name):
            self.name = name
            print(f"  Created: {name}")
            weakref.finalize(self, print, f"  finalize called for: {name}")
    
    obj3 = ResourceWithFinalize("obj3")
    obj4 = ResourceWithFinalize("obj4")
    
    # Create circular reference
    obj3.ref = obj4
    obj4.ref = obj3
    
    print("  Created circular reference: obj3 ↔ obj4")
    del obj3, obj4
    gc.collect()
    print("  ✓ finalize works even with circular references")


def demo_explicit_cleanup():
    """Manually trigger finalization"""
    print("\n" + "=" * 60)
    print("DEMO 3: Explicit Cleanup")
    print("=" * 60)
    
    class FileResource:
        def __init__(self, filename):
            self.filename = filename
            self.finalizer = weakref.finalize(
                self,
                print,
                f"  Auto-closing: {filename}"
            )
            print(f"  Opened: {filename}")
        
        def close(self):
            """Explicitly clean up"""
            if self.finalizer.alive:
                print(f"  Manually closing: {self.filename}")
                self.finalizer()  # Call explicitly
    
    print("\nAuto cleanup (no close call):")
    f1 = FileResource("auto.txt")
    del f1
    gc.collect()
    
    print("\nManual cleanup (close called):")
    f2 = FileResource("manual.txt")
    f2.close()
    print("  Cleanup already done")
    del f2
    gc.collect()
    print("  (finalize not called again - already executed)")


def demo_cleanup_with_args():
    """Pass arguments to cleanup function"""
    print("\n" + "=" * 60)
    print("DEMO 4: Cleanup with Arguments")
    print("=" * 60)
    
    def cleanup_connection(host, port, connection_id):
        print(f"  Closing connection:")
        print(f"    Host: {host}")
        print(f"    Port: {port}")
        print(f"    ID: {connection_id}")
    
    class Connection:
        _next_id = 1
        
        def __init__(self, host, port):
            self.host = host
            self.port = port
            self.connection_id = Connection._next_id
            Connection._next_id += 1
            
            weakref.finalize(
                self,
                cleanup_connection,
                host, port, self.connection_id
            )
            
            print(f"  Opened connection #{self.connection_id} to {host}:{port}")
    
    print("\nCreating connections:")
    conn1 = Connection("localhost", 5432)
    conn2 = Connection("db.example.com", 3306)
    
    print("\nDeleting connections:")
    del conn1
    gc.collect()
    
    del conn2
    gc.collect()


def demo_check_alive():
    """Check if finalizer is still alive"""
    print("\n" + "=" * 60)
    print("DEMO 5: Checking Finalizer Status")
    print("=" * 60)
    
    class ManagedResource:
        def __init__(self, name):
            self.name = name
            self.finalizer = weakref.finalize(
                self,
                print,
                f"  Finalizing: {name}"
            )
            print(f"  Created: {name}")
        
        def is_alive(self):
            return self.finalizer.alive
        
        def cleanup(self):
            if self.finalizer.alive:
                self.finalizer()
    
    print("\nCreating resource:")
    res = ManagedResource("Resource1")
    print(f"  Finalizer alive? {res.is_alive()}")
    
    print("\nCalling cleanup:")
    res.cleanup()
    print(f"  Finalizer alive? {res.is_alive()}")
    
    print("\nDeleting resource:")
    del res
    gc.collect()
    print("  (Finalizer already ran, won't run again)")


def demo_detach():
    """Detach finalizer to prevent cleanup"""
    print("\n" + "=" * 60)
    print("DEMO 6: Detaching Finalizers")
    print("=" * 60)
    
    class CancelableResource:
        def __init__(self, name):
            self.name = name
            self.finalizer = weakref.finalize(
                self,
                print,
                f"  Cleanup: {name}"
            )
            print(f"  Created: {name}")
        
        def cancel_cleanup(self):
            """Prevent cleanup from happening"""
            self.finalizer.detach()
            print(f"  Cleanup canceled for: {self.name}")
    
    print("\nNormal cleanup:")
    res1 = CancelableResource("Resource1")
    del res1
    gc.collect()
    
    print("\nCanceled cleanup:")
    res2 = CancelableResource("Resource2")
    res2.cancel_cleanup()
    del res2
    gc.collect()
    print("  (No cleanup - detached)")


def demo_atexit_comparison():
    """Compare with atexit module"""
    print("\n" + "=" * 60)
    print("DEMO 7: finalize vs atexit")
    print("=" * 60)
    
    import atexit
    
    print("\natexit:")
    print("  - Runs at program exit")
    print("  - All registered functions execute")
    print("  - No object awareness")
    
    def exit_cleanup():
        print("  atexit: Cleanup at program exit")
    
    atexit.register(exit_cleanup)
    print("  Registered atexit handler")
    
    print("\nweakref.finalize:")
    print("  - Runs when object is garbage collected")
    print("  - Only runs if object is deleted")
    print("  - Tied to object lifetime")
    
    class Resource:
        def __init__(self, name):
            weakref.finalize(self, print, f"  finalize: {name} collected")
            print(f"  Created: {name}")
    
    res = Resource("MyResource")
    del res
    gc.collect()
    
    print("\n  ✓ finalize already ran")
    print("  ✓ atexit will run at program exit")


def demo_practical_file_handle():
    """Practical example: File handle cleanup"""
    print("\n" + "=" * 60)
    print("DEMO 8: File Handle Cleanup")
    print("=" * 60)
    
    class ManagedFile:
        def __init__(self, filename, mode='r'):
            self.filename = filename
            self._file = None
            self._open(mode)
            
            # Register cleanup
            weakref.finalize(self, self._cleanup, self._file)
        
        def _open(self, mode):
            print(f"  Opening: {self.filename}")
            # In real code: self._file = open(self.filename, mode)
            self._file = f"<file handle for {self.filename}>"
        
        @staticmethod
        def _cleanup(file_handle):
            print(f"  Closing: {file_handle}")
            # In real code: file_handle.close()
        
        def read(self):
            return f"<contents of {self.filename}>"
    
    print("\nUsing managed file:")
    file1 = ManagedFile("data.txt")
    content = file1.read()
    
    print("\nDeleting file object:")
    del file1
    gc.collect()
    print("  ✓ File handle closed automatically")


def demo_practical_database():
    """Practical example: Database connection"""
    print("\n" + "=" * 60)
    print("DEMO 9: Database Connection Pool")
    print("=" * 60)
    
    class ConnectionPool:
        def __init__(self):
            self.active_connections = 0
            self.total_created = 0
        
        def create_connection(self, database):
            self.active_connections += 1
            self.total_created += 1
            conn_id = self.total_created
            
            print(f"  Pool: Created connection #{conn_id} (active: {self.active_connections})")
            
            # Return connection with auto-cleanup
            conn = type('Connection', (), {
                'id': conn_id,
                'database': database
            })()
            
            weakref.finalize(
                conn,
                self._return_connection,
                conn_id
            )
            
            return conn
        
        def _return_connection(self, conn_id):
            self.active_connections -= 1
            print(f"  Pool: Returned connection #{conn_id} (active: {self.active_connections})")
    
    pool = ConnectionPool()
    
    print("\nCreating connections:")
    conn1 = pool.create_connection("users_db")
    conn2 = pool.create_connection("products_db")
    conn3 = pool.create_connection("orders_db")
    
    print("\nDeleting some connections:")
    del conn1
    gc.collect()
    
    del conn2
    gc.collect()
    
    print("\nDeleting last connection:")
    del conn3
    gc.collect()
    
    print(f"\n  Final pool stats:")
    print(f"    Total created: {pool.total_created}")
    print(f"    Active: {pool.active_connections}")


def demo_resurrection_safe():
    """finalize is safe from object resurrection"""
    print("\n" + "=" * 60)
    print("DEMO 10: Resurrection Safety")
    print("=" * 60)
    
    print("\n__del__ problem: Object resurrection")
    print("  class Bad:")
    print("      def __del__(self):")
    print("          global resurrected")
    print("          resurrected = self  # Object lives again!")
    print("\n  This causes __del__ to run only once,")
    print("  but object might be deleted again later")
    
    print("\nweakref.finalize solution:")
    print("  - Finalizer runs when object is collected")
    print("  - Even if object is resurrected, finalizer won't run again")
    print("  - No double-cleanup bugs")
    print("  - No resurrection bugs")
    
    class SafeResource:
        def __init__(self, name):
            self.name = name
            self.finalizer = weakref.finalize(
                self,
                print,
                f"  finalize: {name} - called exactly once"
            )
    
    print("\nCreating resource:")
    res = SafeResource("TestResource")
    
    print("Deleting resource:")
    del res
    gc.collect()
    
    print("\n✓ finalize prevents resurrection issues")
    print("✓ Cleanup happens exactly once, reliably")


if __name__ == "__main__":
    demo_basic_finalize()
    demo_vs_del()
    demo_explicit_cleanup()
    demo_cleanup_with_args()
    demo_check_alive()
    demo_detach()
    demo_atexit_comparison()
    demo_practical_file_handle()
    demo_practical_database()
    demo_resurrection_safe()
    
    print("\n" + "=" * 60)
    print("All weakref.finalize demos completed!")
    print("=" * 60)
    print("\nKey lessons:")
    print("  ✓ Use finalize instead of __del__")
    print("  ✓ Works with circular references")
    print("  ✓ Can be called explicitly")
    print("  ✓ Prevents resurrection bugs")

