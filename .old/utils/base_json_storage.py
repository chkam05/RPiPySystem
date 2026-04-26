import copy
import json
import os
import tempfile
from abc import ABC, abstractmethod
import threading
from typing import Any, ClassVar, Dict, Optional


class BaseJsonStorage(ABC):
    """
    Base class for simple data storage in a JSON file.
    """

    _ENCODING: ClassVar[str] = 'utf-8'

    def __init__(self, db_path: Optional[str], *, enable_cache: bool = True) -> None:
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

    # --- Read & Write methods ---

    def _ensure_parent_dir(self) -> None:
        os.makedirs(self._parent_dir(), exist_ok=True)

    def _parent_dir(self) -> str:
        """
        Returns the parent directory of db_path (or the current directory if missing).
        """
        return os.path.dirname(self._db_path) or '.'

    def _read(self) -> Dict[str, Any]:
        """
        Safe reading from cache or disk (with invalidation after mtime).
        """
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
        """
        Atomic JSON write to file & cache update (cross-thread consistency).
        """
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
    
    # --- Initialization methods ---

    @abstractmethod
    def _build_initial_data(self) -> Dict[str, Any]:
        """
        Returns the initial JSON structure for a specific implementation.
        """
        raise NotImplementedError('The _register_controllers() method must be overridden in the derived class.')
    
    # --- Cache Management methods ---

    def invalidate_cache(self) -> None:
        """
        Manual cache invalidation; next read will reload from disk.
        """
        with self._lock:
            self._cache_data = None
            self._cache_mtime = None

    def get_snapshot(self) -> Dict[str, Any]:
        """
        Returns a defensive copy of the current data (from cache or disk).
        """
        return self._read()