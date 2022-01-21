import sys
from asyncio import wait_for
from functools import lru_cache
from importlib.abc import Loader
from importlib.util import module_from_spec, spec_from_file_location
from typing import (Any, Awaitable, Callable, Iterable, List, Optional, Set,
                    Tuple, TypeVar, Union)

T = TypeVar("T")


def try_call(callable: Callable[..., T], *args) -> Union[Tuple[T, None], Tuple[None, Exception]]:
    """
    Tries calling a function with the given arguments, returning a tuple of the result or an Exception,
    if the function call fails. Provides a single point of control for calling a "unsafe" functions.
        Parameters:
            callable (Callable): The function to execute
            *args: The arguments for the given function
        Returns:
            A tuple of the result or an Exception
    """
    try:
        return callable(*args), None
    except Exception as err:
        return None, err


async def try_call_async(async_callable: Callable[..., Awaitable[T]], *args, timeout: Optional[int] = None) -> Union[Tuple[T, None], Tuple[None, Exception]]:
    """
    Tries calling an async (awaitable) function with the given arguments, returning a tuple of the result or an Exception,
    if the function call fails. Provides a single point of control for calling a "unsafe" async functions.
        Parameters:
            async_callable (Callable): The function to execute
            *args: The arguments for the given function
        Returns:
            A tuple of the result or an Exception
    """
    try:
        result = await wait_for(async_callable(*args), timeout=timeout)
        return result, None
    except Exception as err:
        return None, err


def memoize(func: Callable):
    """Decorate a function with this annotation to memoize (cache) arguments without bound.

    Note: all arguments in a decorated function must be hashable."""
    @lru_cache(maxsize=None)
    def func_wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return func_wrapper


def load_class_from_file(file_path: str) -> type:
    """Loads and returns a single class defined in a file at the given path."""
    new_module_name = ""  # new module name of imported strategy

    # creates a ModuleSpec which contains all the import-related
    # information used to create and load a module
    spec = spec_from_file_location(new_module_name, file_path)
    if spec is None:
        raise ValueError(f"Cannot find file at {file_path}")

    # creates a new module from the ModuleSpec
    module = module_from_spec(spec)

    if spec.loader is None:
        raise ValueError(f"Unable to retrieve loader for {file_path}")

    try:
        assert isinstance(spec.loader, Loader)
        spec.loader.exec_module(module)  # load the module
    except:
        raise ValueError(f"Unable to parse module at {file_path}")

    # discover locally defined classes from the module
    module_classes: List[type] = [member for member in module.__dict__.values(
    ) if _is_locally_defined_class(member, new_module_name)]

    # assert the module only contains 1 class
    if len(module_classes) != 1:
        raise ValueError(f"The loaded file must only contain 1 class.")
    return module_classes[0]


def _is_locally_defined_class(member: Any, module_name: str) -> bool:
    """Determines whether a module member is a class that belongs to the module with the given name."""
    return isinstance(member, type) and getattr(member, "__module__", None) == module_name


def flatten_set(double_set: Iterable[Set[T]]) -> Set[T]:
    """Flattten the given iterable of sets of items to one set of items."""
    return {item for set in double_set for item in set}
