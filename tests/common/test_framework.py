from functools import wraps
import inspect
import sys
from typing import Any, Callable, Iterable, Optional, Type, Union


def testcase(fn: Callable) -> Callable:
    """
    Decorator marking a method as a test method.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    setattr(wrapper, '_is_testcase', True)
    return wrapper


class SimpleTestCase:
    
    def config(self) -> None:
        """
        Common configuration for all tests (run once). Override in child class.
        """
        pass

    def run(self) -> None:
        """
        Finds methods with the @testcase decorator and runs them one by one.
        Prints: "[test script name] method_name: True/False"
        """
        script_name = (sys.argv[0].split('/')[-1] or __name__).strip()
        
        # --- Run config() once. ---:
        try:
            self.config()
        except Exception as ex:
            msg = f'{script_name} config: False'
            print(msg)
            raise

        # --- Test collection. ---:
        methods = [
            (name, method)
            for name, method in inspect.getmembers(self, predicate=inspect.ismethod)
            if getattr(method, '_is_testcase', False)
        ]

        for name, method in methods:
            ok = True
            try:
                method()
            except AssertionError:
                ok = False
            except Exception:
                ok = False
            print(f'[{script_name}] {name}: {str(ok)}')
    
    # region ASSERTION METHODS

    def _fail(self, message: Optional[str] = None) -> None:
        raise AssertionError(message or 'Assertion failed.')
    
    def assert_true(self, condition: bool, message: Optional[str] = None) -> None:
        if not condition:
            self._fail(message or 'Expected condition to be True.')
    
    def are_equal(self, value: Any, expected_value: Any, message: Optional[str] = None) -> None:
        if value != expected_value:
            self._fail(message or f'Expected equality. Actual={value!r}, Expected={expected_value!r}')
    
    def are_not_equal(self, value: Any, unexpected_value: Any, message: Optional[str] = None) -> None:
        if value == unexpected_value:
            self._fail(message or f'Expected not equal to {unexpected_value!r}')
    
    def are_same(self, value: Any, expected_value: Any, message: Optional[str] = None) -> None:
        if value is not expected_value:
            self._fail(message or 'Expected both references to be the same object.')
    
    def are_not_same(self, value: Any, unexpected_value: Any, message: Optional[str] = None) -> None:
        if value is unexpected_value:
            self._fail(message or 'Expected references to be different objects.')
    
    def contains(self, value: Union[str, Iterable], inner_value: Any, message: Optional[str] = None) -> None:
        try:
            ok = inner_value in value  # type: ignore[operator]
        except Exception:
            ok = False
        if not ok:
            self._fail(message or f'Expected {value!r} to contain {inner_value!r}')
    
    def does_not_contain(self, value: Union[str, Iterable], unexpected_inner_value: Any, message: Optional[str] = None) -> None:
        try:
            ok = unexpected_inner_value not in value  # type: ignore[operator]
        except Exception:
            ok = True
        if not ok:
            self._fail(message or f'Expected {value!r} NOT to contain {unexpected_inner_value!r}')
    
    def ends_with(self, value: Any, expected_ending: Any, message: Optional[str] = None) -> None:
        ok = False
        if isinstance(value, str) and isinstance(expected_ending, str):
            ok = value.endswith(expected_ending)
        else:
            try:
                ok = list(value)[-len(expected_ending):] == list(expected_ending)  # type: ignore[index]
            except Exception:
                ok = False
        if not ok:
            self._fail(message or f'Expected {value!r} to end with {expected_ending!r}')
    
    def fail(self, message: Optional[str] = None) -> None:
        self._fail(message or 'Forced failure.')
    
    def has_count(self, enumerable_value: Iterable, exptected_count: int, message: Optional[str] = None) -> None:
        try:
            count = len(enumerable_value)  # type: ignore[arg-type]
        except Exception:
            count = sum(1 for _ in enumerable_value)
        if count != exptected_count:
            self._fail(message or f'Expected count {exptected_count}, got {count}')
    
    def is_empty(self, value: Any, message: Optional[str] = None) -> None:
        try:
            ok = len(value) == 0
        except Exception:
            ok = not bool(value)
        if not ok:
            self._fail(message or f'Expected empty value, got {value!r}')
    
    def is_false(self, value: Any, message: Optional[str] = None) -> None:
        if bool(value) is not False:
            self._fail(message or f'Expected False, got {value!r}')
    
    def is_greater_than(self, value: Any, threshold: Any, message: Optional[str] = None) -> None:
        if not (value > threshold):
            self._fail(message or f'Expected {value!r} > {threshold!r}')
    
    def is_greater_than_or_equal_to(self, value: Any, threshold: Any, message: Optional[str] = None) -> None:
        if not (value >= threshold):
            self._fail(message or f'Expected {value!r} >= {threshold!r}')
    
    def is_in_range(self, value: Any, low: Any, high: Any, inclusive: bool = True, message: Optional[str] = None) -> None:
        if inclusive:
            ok = (low <= value <= high)
        else:
            ok = (low < value < high)
        if not ok:
            self._fail(message or f'Expected {value!r} in range {low!r}..{high!r} (inclusive={inclusive})')
    
    def is_instance_of_type(self, value: Any, expected_type: Union[Type, tuple], message: Optional[str] = None) -> None:
        if not isinstance(value, expected_type):
            self._fail(message or f'Expected instance of {expected_type}, got {type(value)}')
    
    def is_less_than(self, value: Any, threshold: Any, message: Optional[str] = None) -> None:
        if not (value < threshold):
            self._fail(message or f'Expected {value!r} < {threshold!r}')
    
    def is_negative(self, value: Any, message: Optional[str] = None) -> None:
        try:
            ok = value < 0
        except Exception:
            ok = False
        if not ok:
            self._fail(message or f'Expected negative value, got {value!r}')
    
    def is_not_empty(self, value: Any, message: Optional[str] = None) -> None:
        try:
            ok = len(value) > 0
        except Exception:
            ok = bool(value)
        if not ok:
            self._fail(message or f'Expected non-empty value')

    def is_not_instance_of_type(self, value: Any, unexpected_type: Union[Type, tuple], message: Optional[str] = None) -> None:
        if isinstance(value, unexpected_type):
            self._fail(message or f'Expected NOT instance of {unexpected_type}, got {type(value)}')

    def is_not_null(self, value: Any, message: Optional[str] = None) -> None:
        if value is None:
            self._fail(message or 'Expected value not to be None')
    
    def is_null(self, value: Any, message: Optional[str] = None) -> None:
        if value is not None:
            self._fail(message or 'Expected value to be None')
    
    def is_positive(self, value: Any, message: Optional[str] = None) -> None:
        try:
            ok = value > 0
        except Exception:
            ok = False
        if not ok:
            self._fail(message or f'Expected positive value, got {value!r}')
    
    def is_true(self, value: Any, message: Optional[str] = None) -> None:
        if bool(value) is not True:
            self._fail(message or f'Expected True, got {value!r}')
    
    def start_with(self, value: Any, expected_start: Any, message: Optional[str] = None) -> None:
        ok = False
        if isinstance(value, str) and isinstance(expected_start, str):
            ok = value.startswith(expected_start)
        else:
            try:
                ok = list(value)[: len(expected_start)] == list(expected_start)  # type: ignore[index]
            except Exception:
                ok = False
        if not ok:
            self._fail(message or f'Expected {value!r} to start with {expected_start!r}')

    # endregion