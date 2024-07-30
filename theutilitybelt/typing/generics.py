import types
from collections.abc import Callable
from queue import Queue
from typing import (  # type: ignore
    Generic,
    Protocol,
    TypeVar,
    _GenericAlias,  # type: ignore
    _SpecialGenericAlias,  # type: ignore
)

TypingGenericAlias = (_GenericAlias, _SpecialGenericAlias, types.GenericAlias)
GenericDefinitionClasses = (Generic, Protocol)


class GenericTypeMap:
    """
    A class that represents a mapping between generic types and their implementations.

    This class allows you to define a mapping between generic types and their corresponding
    implementations. It provides methods to access and modify the mapping.

    Example:
        ```python
        class Node(Generic[T]):
            pass

        class IntNode(Node[int]):
            pass

        mapping = GenericTypeMap(Node)

        mapping["T"] # Returns int
        mapping[T] # Returns int
        ```
    """

    def __init__(self, cls: type):
        self._inner_map: dict[str, TypeVar | type] = {}

        mapping = self._build_map(cls)

        for k, v in mapping.items():
            self[k] = v

    @classmethod
    def _get_generic_definitions(cls, type_cls: type):
        queue = Queue()
        queue.put(type_cls)
        aliases = []

        if root_origin := (getattr(type_cls, "__origin__", None)):
            queue.put(root_origin)

        while not queue.empty():
            type_check = queue.get()
            if getattr(type_check, "__origin__", None) in GenericDefinitionClasses:
                aliases.append(type_check)

            for base in getattr(type_check, "__orig_bases__", ()):
                queue.put(base)
                if orig := getattr(base, "__origin__", None):
                    queue.put(orig)

        return aliases

    @classmethod
    def _get_generic_implementations(cls, type_cls: type):
        queue = Queue()
        queue.put(type_cls)
        if orig := getattr(type_cls, "__origin__", None):
            queue.put(orig)

        aliases = []
        while not queue.empty():
            type_check = queue.get()
            if (
                type(type_check) is _GenericAlias
                and getattr(type_check, "__origin__", None)
                not in GenericDefinitionClasses
            ):
                aliases.append(type_check)

            for base in getattr(type_check, "__orig_bases__", ()):
                queue.put(base)
                if base_orig := getattr(base, "__origin__", None):
                    queue.put(base_orig)

        return aliases

    @classmethod
    def _build_map(cls, type_cls: type) -> dict[str, TypeVar | type]:
        generic_definitions = cls._get_generic_definitions(type_cls)

        generic_implementations = cls._get_generic_implementations(type_cls)

        generic_definitions.reverse()
        generic_implementations.reverse()

        generic_definitions = generic_definitions[: len(generic_implementations)]

        mapping = {}

        for idx, definition in enumerate(generic_definitions):
            implementation = generic_implementations[idx]
            additions = dict(zip(definition.__args__, implementation.__args__))
            mapping = {**mapping, **additions}

        return mapping

    @classmethod
    def _lookup_key(cls, key: TypeVar | str) -> str:
        if isinstance(key, TypeVar):
            return key.__name__
        return key

    def is_generic_mapping_open(self) -> bool:
        for k, v in self._inner_map.items():
            if isinstance(v, TypeVar):
                return True
        return False

    def is_generic_mapping_closed(self) -> bool:
        return not self.is_generic_mapping_open()

    def __getitem__(self, key: TypeVar | str):
        return self._inner_map[self._lookup_key(key)]

    def __setitem__(self, key: TypeVar | str, value: type | TypeVar):
        self._inner_map[self._lookup_key(key)] = value

    def values(self):
        return self._inner_map.values()

    def get(self, key: TypeVar | str, default=None):
        return self._inner_map.get(self._lookup_key(key), default)

    def items(self):
        return self._inner_map.items()

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, GenericTypeMap):
            return False
        return self._inner_map == __value._inner_map


def get_generic_bases(cls: type, filter: Callable[[type], bool] = lambda t: True):
    queue = Queue()
    queue.put(cls)
    items = []
    while not queue.empty():
        t = queue.get_nowait()

        for sub in getattr(t, "__orig_bases__", ()):
            queue.put(sub)
            if orig := getattr(sub, "__origin__", None):
                queue.put(orig)

            if filter(sub):
                items.append(sub)

    return items


def is_generic_type_closed(cls: type):
    m = GenericTypeMap(cls)
    return m.is_generic_mapping_closed()


def is_generic_type_open(cls: type):
    m = GenericTypeMap(cls)
    return m.is_generic_mapping_open()


def get_type_args(cls: type):
    return getattr(cls, "__args__", ())


def is_generic_type(tp: type):
    """Test if the given type is a generic type. This includes Generic itself, but
    excludes special typing constructs such as Union, Tuple, Callable, ClassVar.
    Example:

        is_generic_type(int) == False
        is_generic_type(Union[int, str]) == False
        is_generic_type(Union[int, T]) == False
        is_generic_type(ClassVar[List[int]]) == False
        is_generic_type(Callable[..., T]) == False

        is_generic_type(Generic) == True
        is_generic_type(Generic[T]) == True
        is_generic_type(Iterable[int]) == True
        is_generic_type(Mapping) == True
        is_generic_type(MutableMapping[T, List[int]]) == True
        is_generic_type(Sequence[Union[str, bytes]]) == True
    """

    return (
        isinstance(tp, type)
        and issubclass(tp, Generic)
        or isinstance(tp, TypingGenericAlias)
    )


def get_generic_type_args(type: type):
    queue = Queue()
    queue.put(type)

    while not queue.empty():
        type_check = queue.get()
        if getattr(type_check, "__origin__", None) == Generic:
            return type_check.__args__

        for base in getattr(type_check, "__orig_bases__", ()):
            queue.put(base)
            queue.put(base.__origin__)

    return ()


def get_generic_types(cls: type):
    mapping = GenericTypeMap(cls)
    return tuple(mapping.values())


def try_to_complete_generic(open_type: _GenericAlias, closed_type: type) -> type:
    if not getattr(open_type, "__args__", None):
        return open_type
    if is_generic_type_closed(open_type):
        return open_type

    mapping = GenericTypeMap(closed_type)
    new_args = tuple([mapping.get(a, a) for a in open_type.__args__])
    return open_type[new_args]


def get_generic_type(obj):
    """Get the generic type of an object if possible, or runtime class otherwise.
    Examples::
        class Node(Generic[T]):
            ...
        type(Node[int]()) == Node
        get_generic_type(Node[int]()) == Node[int]
        get_generic_type(Node[T]()) == Node[T]
        get_generic_type(1) == int
    """

    gen_type = getattr(obj, "__orig_class__", None)
    return gen_type if gen_type is not None else type(obj)
