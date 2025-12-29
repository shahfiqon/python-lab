# Deep Python Techniques - Proof of Concept Demos

This directory contains executable demonstrations of 10 advanced Python features discussed in [`.notes/10-python-deep-techs.md`](../.notes/10-python-deep-techs.md).

## Quick Start

Run any demo directly:

```bash
python 01_descriptor_protocol.py
python 02_init_subclass.py
# ... and so on
```

## Available Demos

| # | Feature | Script | Documentation |
|---|---------|--------|---------------|
| 1 | Descriptor Protocol | `01_descriptor_protocol.py` | [docs/01_descriptor_protocol.md](docs/01_descriptor_protocol.md) |
| 2 | `__init_subclass__` | `02_init_subclass.py` | [docs/02_init_subclass.md](docs/02_init_subclass.md) |
| 3 | Weak References | `03_weak_references.py` | [docs/03_weak_references.md](docs/03_weak_references.md) |
| 4 | Evaluation Order | `04_evaluation_order.py` | [docs/04_evaluation_order.md](docs/04_evaluation_order.md) |
| 5 | Frame Objects | `05_frame_objects.py` | [docs/05_frame_objects.md](docs/05_frame_objects.md) |
| 6 | Custom Import Hooks | `06_custom_import_hooks.py` | [docs/06_custom_import_hooks.md](docs/06_custom_import_hooks.md) |
| 7 | `weakref.finalize` | `07_weakref_finalize.py` | [docs/07_weakref_finalize.md](docs/07_weakref_finalize.md) |
| 8 | MappingProxyType | `08_mapping_proxy_type.py` | [docs/08_mapping_proxy_type.md](docs/08_mapping_proxy_type.md) |
| 9 | Late-Bound Defaults | `09_late_bound_defaults.py` | [docs/09_late_bound_defaults.md](docs/09_late_bound_defaults.md) |
| 10 | Context Variables | `10_contextvars.py` | [docs/10_contextvars.md](docs/10_contextvars.md) |

## Requirements

- Python 3.10 or higher recommended
- Standard library only (no external dependencies)

## Documentation

Each demo has its own documentation file in the `docs/` directory with:
- Detailed explanations
- Real-world use cases
- Common pitfalls
- Further reading

## Adding New Demos

When adding new features:
1. Create `NN_feature_name.py` with executable examples
2. Create `docs/NN_feature_name.md` with documentation
3. Update this README table

