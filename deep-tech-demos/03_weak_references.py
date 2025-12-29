"""
Weak References - Deep Python Techniques Demo
Related to: .notes/10-python-deep-techs.md Section 3

Weak references allow you to reference objects without preventing them from being
garbage collected. Essential for caches, event systems, and avoiding memory leaks.
"""

import weakref
import gc


def demo_basic_weakref():
    """Basic weak reference behavior"""
    print("=" * 60)
    print("DEMO 1: Basic Weak Reference")
    print("=" * 60)
    
    class BigObject:
        def __init__(self, name):
            self.name = name
            print(f"  Created {self.name}")
        
        def __del__(self):
            print(f"  Deleted {self.name}")
    
    # Strong reference
    print("\nWith strong reference:")
    obj = BigObject("object1")
    ref = obj  # Another strong reference
    print("  Two strong references exist")
    del obj
    print("  After 'del obj', object still exists (ref keeps it alive)")
    del ref
    print("  After 'del ref', object is garbage collected")
    
    # Weak reference
    print("\nWith weak reference:")
    obj = BigObject("object2")
    weak = weakref.ref(obj)  # Weak reference
    print(f"  Weak reference points to: {weak()}")
    print("  Deleting strong reference...")
    del obj
    gc.collect()  # Force garbage collection
    print(f"  Weak reference now points to: {weak()}")


def demo_weak_value_dict():
    """Cache that doesn't prevent garbage collection"""
    print("\n" + "=" * 60)
    print("DEMO 2: WeakValueDictionary Cache")
    print("=" * 60)
    
    class ExpensiveObject:
        def __init__(self, id_):
            self.id = id_
            print(f"  Creating expensive object {id_}")
        
        def __del__(self):
            print(f"  Garbage collecting object {self.id}")
    
    class SmartCache:
        def __init__(self):
            self._cache = weakref.WeakValueDictionary()
        
        def get(self, key):
            if key in self._cache:
                print(f"  Cache HIT for {key}")
                return self._cache[key]
            else:
                print(f"  Cache MISS for {key}")
                obj = ExpensiveObject(key)
                self._cache[key] = obj
                return obj
    
    cache = SmartCache()
    
    print("\nFirst access (creates object):")
    obj1 = cache.get("item1")
    
    print("\nSecond access (cache hit):")
    obj2 = cache.get("item1")
    print(f"  Same object? {obj1 is obj2}")
    
    print("\nDeleting references:")
    del obj1, obj2
    gc.collect()
    
    print("\nThird access (object was GC'd, cache miss):")
    obj3 = cache.get("item1")
    
    print("\nKeeping reference alive:")
    obj4 = cache.get("item2")
    print("  Object 'item2' has a strong reference")
    
    print("\nForcing garbage collection:")
    gc.collect()
    print("  item2 still alive because we hold obj4")
    
    print("\nAccessing again:")
    obj5 = cache.get("item2")
    print(f"  Same object? {obj4 is obj5}")


def demo_observer_pattern():
    """Event system without memory leaks"""
    print("\n" + "=" * 60)
    print("DEMO 3: Observer Pattern with Weak References")
    print("=" * 60)
    
    class EventEmitter:
        def __init__(self):
            self._listeners = []
        
        def add_listener(self, listener):
            """Add listener using weak reference"""
            # Use WeakMethod for bound methods
            weak_listener = weakref.WeakMethod(listener)
            self._listeners.append(weak_listener)
            print(f"  Added listener: {listener.__self__.__class__.__name__}")
        
        def emit(self, event):
            """Notify all alive listeners"""
            print(f"  Emitting: {event}")
            # Clean up dead references
            alive_listeners = []
            for weak_listener in self._listeners:
                listener = weak_listener()
                if listener is not None:
                    listener(event)
                    alive_listeners.append(weak_listener)
            self._listeners = alive_listeners
            print(f"  Active listeners: {len(self._listeners)}")
    
    class Observer:
        def __init__(self, name):
            self.name = name
            print(f"  Created observer: {name}")
        
        def on_event(self, event):
            print(f"    → {self.name} received: {event}")
        
        def __del__(self):
            print(f"  Observer {self.name} deleted")
    
    emitter = EventEmitter()
    
    print("\nCreating observers:")
    obs1 = Observer("Observer1")
    obs2 = Observer("Observer2")
    obs3 = Observer("Observer3")
    
    print("\nRegistering listeners:")
    emitter.add_listener(obs1.on_event)
    emitter.add_listener(obs2.on_event)
    emitter.add_listener(obs3.on_event)
    
    print("\nEmitting event (all observers alive):")
    emitter.emit("event1")
    
    print("\nDeleting obs2:")
    del obs2
    gc.collect()
    
    print("\nEmitting event (obs2 automatically removed):")
    emitter.emit("event2")
    
    print("\nDeleting remaining observers:")
    del obs1, obs3
    gc.collect()
    
    print("\nEmitting event (no listeners):")
    emitter.emit("event3")


def demo_weak_key_dict():
    """Using WeakKeyDictionary for object metadata"""
    print("\n" + "=" * 60)
    print("DEMO 4: WeakKeyDictionary for Metadata")
    print("=" * 60)
    
    class Widget:
        def __init__(self, name):
            self.name = name
        
        def __repr__(self):
            return f"Widget({self.name})"
        
        def __del__(self):
            print(f"  Widget {self.name} deleted")
    
    # Store metadata without preventing GC
    metadata = weakref.WeakKeyDictionary()
    
    print("\nCreating widgets with metadata:")
    w1 = Widget("Button")
    w2 = Widget("Label")
    w3 = Widget("TextBox")
    
    metadata[w1] = {"clicks": 0, "visible": True}
    metadata[w2] = {"text": "Hello", "color": "blue"}
    metadata[w3] = {"value": "", "max_length": 100}
    
    print(f"  Metadata stored for {len(metadata)} widgets")
    for widget, data in metadata.items():
        print(f"    {widget}: {data}")
    
    print("\nDeleting w2:")
    del w2
    gc.collect()
    
    print(f"\nMetadata now contains {len(metadata)} entries:")
    for widget, data in metadata.items():
        print(f"    {widget}: {data}")
    
    print("\n✓ Metadata automatically cleaned up when widget is deleted")


def demo_callback_management():
    """Managing callbacks without memory leaks"""
    print("\n" + "=" * 60)
    print("DEMO 5: Callback Management")
    print("=" * 60)
    
    class CallbackManager:
        def __init__(self):
            self._callbacks = weakref.WeakSet()
        
        def register(self, callback):
            """Register a callback (must be a bound method or object)"""
            self._callbacks.add(callback)
            print(f"  Registered callback")
        
        def trigger(self):
            """Trigger all registered callbacks"""
            count = 0
            for callback in self._callbacks:
                callback.execute()
                count += 1
            print(f"  Triggered {count} callback(s)")
    
    class Task:
        def __init__(self, name):
            self.name = name
            print(f"  Created task: {name}")
        
        def execute(self):
            print(f"    → Executing {self.name}")
        
        def __del__(self):
            print(f"  Task {self.name} cleaned up")
    
    manager = CallbackManager()
    
    print("\nCreating and registering tasks:")
    task1 = Task("Task1")
    task2 = Task("Task2")
    task3 = Task("Task3")
    
    manager.register(task1)
    manager.register(task2)
    manager.register(task3)
    
    print("\nTriggering callbacks:")
    manager.trigger()
    
    print("\nDeleting task2:")
    del task2
    gc.collect()
    
    print("\nTriggering again (task2 auto-removed):")
    manager.trigger()
    
    print("\nCleanup:")
    del task1, task3
    gc.collect()
    manager.trigger()


def demo_circular_reference():
    """How weak references help with circular references"""
    print("\n" + "=" * 60)
    print("DEMO 6: Breaking Circular References")
    print("=" * 60)
    
    print("Without weak references (memory leak):")
    
    class Parent:
        def __init__(self, name):
            self.name = name
            self.child = None
        
        def __del__(self):
            print(f"  Parent {self.name} deleted")
    
    class Child:
        def __init__(self, name):
            self.name = name
            self.parent = None  # Strong reference
        
        def __del__(self):
            print(f"  Child {self.name} deleted")
    
    parent = Parent("Dad")
    child = Child("Kid")
    parent.child = child
    child.parent = parent  # Circular reference
    
    print("  Created circular reference: Parent ← → Child")
    del parent, child
    gc.collect()
    print("  Even after 'del', objects may not be GC'd immediately")
    
    print("\nWith weak references (no leak):")
    
    class SmartChild:
        def __init__(self, name):
            self.name = name
            self._parent_ref = None
        
        def set_parent(self, parent):
            self._parent_ref = weakref.ref(parent)
        
        @property
        def parent(self):
            if self._parent_ref:
                return self._parent_ref()
            return None
        
        def __del__(self):
            print(f"  SmartChild {self.name} deleted")
    
    parent2 = Parent("Mom")
    child2 = SmartChild("Kid2")
    parent2.child = child2
    child2.set_parent(parent2)  # Weak reference
    
    print("  Created smart reference: Parent → Child ⤏ Parent")
    print("  (Child uses weak reference to parent)")
    
    del parent2, child2
    gc.collect()
    print("  ✓ Both objects properly garbage collected")


if __name__ == "__main__":
    demo_basic_weakref()
    demo_weak_value_dict()
    demo_observer_pattern()
    demo_weak_key_dict()
    demo_callback_management()
    demo_circular_reference()
    
    print("\n" + "=" * 60)
    print("All weak reference demos completed!")
    print("=" * 60)

