from abc import ABC, abstractmethod
import copy
import json
import os
import tempfile
import threading
from typing import Any, ClassVar, Dict, Optional


class BaseJsonStorage(ABC):
    """Base JSON-backed storage with optional caching and thread-safe operations."""

    _ENCODING: ClassVar[str] = 'utf-8'

    def __init__(self, db_path: Optional[str], *, enable_cache: bool = True) -> None:
        """Initialize the JSON storage with a file path and optional caching."""
        if not db_path:
            raise ValueError('db_path is required')
        
        self._db_path = db_path

        # Lock to protect cache and IO operations (multi-threading within a process)
        self._lock = threading.RLock()

        # Cache
        self._cache_enabled = enable_cache
        self._cache_data: Optional[Dict[str, Any]] = None
        self._cache_mtime: Optional[float] = None  # mtime of the file, for invalidation

        self._ensure_parent_dir()
        if not os.path.exists(self._db_path):
            self._atomic_write(self._build_initial_data())
    
    # --------------------------------------------------------------------------
    # --- READ & WRITE METHODS ---
    # --------------------------------------------------------------------------

    def _ensure_parent_dir(self) -> None:
        """Ensure the parent directory of the database file exists."""
        os.makedirs(self._parent_dir(), exist_ok=True)

    def _parent_dir(self) -> str:
        """Return the directory containing the storage file."""
        return os.path.dirname(self._db_path) or '.'

    def _read(self) -> Dict[str, Any]:
        """Read JSON data from disk or cache with thread-safe access."""
        with self._lock:
            if self._cache_enabled and self._cache_data is not None:
                try:
                    current_mtime = os.path.getmtime(self._db_path)
                except FileNotFoundError:
                    data = self._build_initial_data()
                    self._cache_data = copy.deepcopy(data)
                    self._cache_mtime = None
                    return copy.deepcopy(data)

                # If mtime hasn't changed, return cached copy.
                if self._cache_mtime is not None and current_mtime == self._cache_mtime:
                    return copy.deepcopy(self._cache_data)
            
            # No cache or outdated, read from disk.
            try:
                with open(self._db_path, 'r', encoding=self._ENCODING) as f:
                    data = json.load(f)
            except FileNotFoundError:
                # If file is missing, rebuild default structure.
                data = self._build_initial_data()
            
            if self._cache_enabled:
                # Cache and mtime update:
                try:
                    self._cache_mtime = os.path.getmtime(self._db_path)
                except FileNotFoundError:
                    self._cache_mtime = None
                self._cache_data = copy.deepcopy(data)
            
            return copy.deepcopy(data)

    def _atomic_write(self, data: Dict[str, Any]) -> None:
        """Write JSON data atomically using a temporary file and replace operation."""
        with self._lock:
            dirpath = self._parent_dir()
            # Writing to a temporary file in the same directory.
            with tempfile.NamedTemporaryFile('w', delete=False, dir=dirpath, encoding=self._ENCODING) as tf:
                json.dump(data, tf, ensure_ascii=False, indent=2)
                tmp_name = tf.name
            os.replace(tmp_name, self._db_path)

            # Refresh cache and mtime.
            if self._cache_enabled:
                self._cache_data = copy.deepcopy(data)
                try:
                    self._cache_mtime = os.path.getmtime(self._db_path)
                except FileNotFoundError:
                    # Theoretically it shouldn't happen after os.replace, but guard is left
                    self._cache_mtime = None
    
    # --------------------------------------------------------------------------
    # --- DATA INITIALIZATION METHODS ---
    # --------------------------------------------------------------------------

    @abstractmethod
    def _build_initial_data(self) -> Dict[str, Any]:
        """Return the initial empty structure for the JSON storage."""
        raise NotImplementedError('The _build_initial_data() method must be overridden in the derived class.')
    
    # --------------------------------------------------------------------------
    # --- CACHE MANAGEMENT METHODS ---
    # --------------------------------------------------------------------------

    def invalidate_cache(self) -> None:
        """Clear the in-memory cache and force future reads to reload from disk."""
        with self._lock:
            self._cache_data = None
            self._cache_mtime = None

    def get_snapshot(self) -> Dict[str, Any]:
        """Return a deep-copied snapshot of the current JSON data."""
        return self._read()