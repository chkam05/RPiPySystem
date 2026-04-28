from __future__ import annotations
from pathlib import Path
from types import ModuleType
import importlib.util
import sys


def load_childutils() -> ModuleType:
    try:
        from supervisor import childutils
        if hasattr(childutils, 'listener'):
            return childutils
    except Exception:
        pass

    current_tree = Path(__file__).resolve().parents[1]
    for path_entry in sys.path:
        if not path_entry:
            path_entry = '.'

        candidate = Path(path_entry).resolve() / 'supervisor' / 'childutils.py'
        if not candidate.exists():
            continue
        if current_tree in candidate.parents:
            continue

        spec = importlib.util.spec_from_file_location('_external_supervisor_childutils', candidate)
        if not spec or not spec.loader:
            continue

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, 'listener'):
            return module

    raise ImportError('Unable to load supervisor.childutils from the installed supervisor package.')

