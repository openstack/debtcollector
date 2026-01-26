# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import annotations

import builtins
from collections.abc import Callable
import functools
import inspect
import types
from typing import Any
from typing import overload
from typing import ParamSpec
from typing import TypeVar

import wrapt

from debtcollector import _utils

P = ParamSpec('P')
R = TypeVar('R')
T = TypeVar('T')


def _get_qualified_name(
    obj: Callable[..., Any] | types.ModuleType | builtins.function,
) -> str:
    return _utils.get_qualified_name(obj)[1]


def _fetch_first_result(
    fget: Callable[[Any], Any] | None,
    fset: Callable[[Any, Any], None] | None,
    fdel: Callable[[Any], None] | None,
    apply_func: Callable[[Callable[..., Any] | builtins.function], str],
    value_not_found: str | None = None,
) -> str | None:
    """Fetch first non-none/empty result of applying ``apply_func``."""
    for f in filter(None, (fget, fset, fdel)):
        result = apply_func(f)
        if result:
            return result
    return value_not_found


class removed_property(property):
    """Property descriptor that deprecates a property.

    This works like the ``@property`` descriptor but can be used instead to
    provide the same functionality and also interact with the :mod:`warnings`
    module to warn when a property is accessed, set and/or deleted.

    :param message: string used as ending contents of the deprecate message
    :param version: version string (represents the version this deprecation
                    was created in)
    :param removal_version: version string (represents the version this
                            deprecation will be removed in); a string
                            of '?' will denote this will be removed in
                            some future unknown version
    :param stacklevel: stacklevel used in the :func:`warnings.warn` function
                       to locate where the users code is when reporting the
                       deprecation call (the default being 3)
    :param category: the :mod:`warnings` category to use, defaults to
                     :py:class:`DeprecationWarning` if not provided
    """

    # Message templates that will be turned into real messages as needed.
    _PROPERTY_GONE_TPLS = {
        'set': "Setting the '%s' property is deprecated",
        'get': "Reading the '%s' property is deprecated",
        'delete': "Deleting the '%s' property is deprecated",
    }

    stacklevel: int
    category: type[Warning]
    version: str | None
    removal_version: str | None
    message: str | None
    _message_cache: dict[str, str]

    def __init__(
        self,
        fget: Callable[[Any], Any] | None = None,
        fset: Callable[[Any, Any], None] | None = None,
        fdel: Callable[[Any], None] | None = None,
        doc: str | None = None,
        stacklevel: int = 3,
        category: type[Warning] = DeprecationWarning,
        version: str | None = None,
        removal_version: str | None = None,
        message: str | None = None,
    ):
        if doc is None and inspect.isfunction(fget):
            doc = getattr(fget, '__doc__', None)
        super().__init__(fget, fset, fdel, doc)
        self.stacklevel = stacklevel
        self.category = category
        self.version = version
        self.removal_version = removal_version
        self.message = message
        self._message_cache = {}

    def _fetch_message_from_cache(self, kind: str) -> str:
        try:
            out_message = self._message_cache[kind]
        except KeyError:
            prefix_tpl = self._PROPERTY_GONE_TPLS[kind]
            prefix = prefix_tpl % _fetch_first_result(
                self.fget,
                self.fset,
                self.fdel,
                _get_qualified_name,
                value_not_found="???",
            )
            out_message = _utils.generate_message(
                prefix,
                message=self.message,
                version=self.version,
                removal_version=self.removal_version,
            )
            self._message_cache[kind] = out_message
        return out_message

    def __call__(
        self,
        fget: Callable[[Any], Any],
        **kwargs: Any,
    ) -> removed_property:
        return type(self)(
            fget,
            self.fset,
            self.fdel,
            kwargs.get('doc', getattr(fget, '__doc__', self.__doc__)),
            kwargs.get('stacklevel', self.stacklevel),
            kwargs.get('category', self.category),
            kwargs.get('version', self.version),
            kwargs.get('removal_version', self.removal_version),
            kwargs.get('message', self.message),
        )

    def __delete__(self, obj: Any) -> None:
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        out_message = self._fetch_message_from_cache('delete')
        _utils.deprecation(
            out_message, stacklevel=self.stacklevel, category=self.category
        )
        self.fdel(obj)

    def __set__(self, instance: Any, value: Any) -> None:
        if self.fset is None:
            raise AttributeError("can't set attribute")
        out_message = self._fetch_message_from_cache('set')
        _utils.deprecation(
            out_message, stacklevel=self.stacklevel, category=self.category
        )
        self.fset(instance, value)

    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        if instance is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        out_message = self._fetch_message_from_cache('get')
        _utils.deprecation(
            out_message, stacklevel=self.stacklevel, category=self.category
        )
        return self.fget(instance)

    def getter(self, fget: Callable[[Any], Any], /) -> removed_property:
        return type(self)(
            fget,
            self.fset,
            self.fdel,
            self.__doc__,
            self.stacklevel,
            self.category,
            self.version,
            self.removal_version,
            self.message,
        )

    def setter(self, fset: Callable[[Any, Any], None], /) -> removed_property:
        return type(self)(
            self.fget,
            fset,
            self.fdel,
            self.__doc__,
            self.stacklevel,
            self.category,
            self.version,
            self.removal_version,
            self.message,
        )

    def deleter(self, fdel: Callable[[Any], None], /) -> removed_property:
        return type(self)(
            self.fget,
            self.fset,
            fdel,
            self.__doc__,
            self.stacklevel,
            self.category,
            self.version,
            self.removal_version,
            self.message,
        )


@overload
def remove(
    f: Callable[P, R],
    message: str | None = None,
    version: str | None = None,
    removal_version: str | None = None,
    stacklevel: int = 3,
    category: type[Warning] | None = None,
) -> Callable[P, R]: ...


@overload
def remove(
    f: None = None,
    message: str | None = None,
    version: str | None = None,
    removal_version: str | None = None,
    stacklevel: int = 3,
    category: type[Warning] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


def remove(
    f: Callable[P, R] | None = None,
    message: str | None = None,
    version: str | None = None,
    removal_version: str | None = None,
    stacklevel: int = 3,
    category: type[Warning] | None = None,
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorates a function, method, or class to emit a deprecation warning

    Due to limitations of the wrapt library (and python) itself, if this
    is applied to subclasses of metaclasses then it likely will not work
    as expected. More information can be found at bug #1520397 to see if
    this situation affects your usage of this *universal* decorator, for
    this specific scenario please use :py:func:`.removed_class` instead.

    :param str message: A message to include in the deprecation warning
    :param str version: Specify what version the removed function is present in
    :param str removal_version: What version the function will be removed. If
                                '?' is used this implies an undefined future
                                version
    :param int stacklevel: How many entries deep in the call stack before
                           ignoring
    :param type category: warnings message category (this defaults to
                          ``DeprecationWarning`` when none is provided)
    """
    if f is None:
        return functools.partial(
            remove,
            message=message,
            version=version,
            removal_version=removal_version,
            stacklevel=stacklevel,
            category=category,
        )

    @wrapt.decorator
    def wrapper(
        wrapped: Callable[P, R],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> R:
        qualified, f_name = _utils.get_qualified_name(f)
        if qualified:
            if inspect.isclass(f):
                prefix_pre = "Using class"
                thing_post = ''
            else:
                prefix_pre = "Using function/method"
                thing_post = '()'
        if not qualified:
            prefix_pre = "Using function/method"
            base_name = None
            if instance is None:
                # Decorator was used on a class
                if inspect.isclass(f):
                    prefix_pre = "Using class"
                    thing_post = ''
                    module = inspect.getmodule(f)
                    if module is None:
                        raise TypeError('Could not retrieve module for {f}')
                    module_name = _get_qualified_name(module)
                    if module_name == '__main__':
                        f_name = _utils.get_class_name(
                            f, fully_qualified=False
                        )
                    else:
                        f_name = _utils.get_class_name(f, fully_qualified=True)
                # Decorator was a used on a function
                else:
                    thing_post = '()'
                    module = inspect.getmodule(f)
                    if module is None:
                        raise TypeError('Could not retrieve module for {f}')
                    module_name = _get_qualified_name(module)
                    if module_name != '__main__':
                        f_name = _utils.get_callable_name(f)
            # Decorator was used on a classmethod or instancemethod
            else:
                thing_post = '()'
                base_name = _utils.get_class_name(
                    instance, fully_qualified=False
                )
            if base_name:
                thing_name = ".".join([base_name, f_name])
            else:
                thing_name = f_name
        else:
            thing_name = f_name
        if thing_post:
            thing_name += thing_post
        prefix = prefix_pre + f" '{thing_name}' is deprecated"
        out_message = _utils.generate_message(
            prefix,
            version=version,
            removal_version=removal_version,
            message=message,
        )
        _utils.deprecation(
            out_message, stacklevel=stacklevel, category=category
        )
        return wrapped(*args, **kwargs)

    return wrapper(f)


def removed_kwarg(
    old_name: str,
    message: str | None = None,
    version: str | None = None,
    removal_version: str | None = None,
    stacklevel: int = 3,
    category: type[Warning] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorates a kwarg accepting function to deprecate a removed kwarg."""
    prefix = f"Using the '{old_name}' argument is deprecated"
    out_message = _utils.generate_message(
        prefix,
        postfix=None,
        message=message,
        version=version,
        removal_version=removal_version,
    )

    @wrapt.decorator
    def wrapper(
        wrapped: Callable[P, R],
        instance: Any,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> R:
        if old_name in kwargs:
            _utils.deprecation(
                out_message, stacklevel=stacklevel, category=category
            )
        return wrapped(*args, **kwargs)

    return wrapper


def removed_class(
    cls_name: str,
    replacement: None = None,
    message: str | None = None,
    version: str | None = None,
    removal_version: str | None = None,
    stacklevel: int = 3,
    category: type[Warning] | None = None,
) -> Callable[[T], T]:
    """Decorates a class to denote that it will be removed at some point."""

    def _wrap_it(old_init: Any, out_message: str) -> Any:
        @functools.wraps(old_init, assigned=_utils.get_assigned(old_init))
        def new_init(self: Any, *args: Any, **kwargs: Any) -> Any:
            _utils.deprecation(
                out_message, stacklevel=stacklevel, category=category
            )
            return old_init(self, *args, **kwargs)

        return new_init

    def _cls_decorator(cls: T) -> T:
        if not inspect.isclass(cls):
            _qual, type_name = _utils.get_qualified_name(type(cls))
            raise TypeError(
                f"Unexpected class type '{type_name}' (expected "
                f"class type only)"
            )

        out_message = _utils.generate_message(
            f"Using class '{cls_name}' (either directly or via inheritance) "
            f"is deprecated",
            postfix=None,
            message=message,
            version=version,
            removal_version=removal_version,
        )
        cls.__init__ = _wrap_it(cls.__init__, out_message)
        return cls

    return _cls_decorator


def removed_module(
    module: types.ModuleType | str,
    replacement: str | None = None,
    message: str | None = None,
    version: str | None = None,
    removal_version: str | None = None,
    stacklevel: int = 3,
    category: type[Warning] | None = None,
) -> None:
    """Helper to be called inside a module to emit a deprecation warning

    :param str replacment: A location (or information about) of any potential
                           replacement for the removed module (if applicable)
    :param str message: A message to include in the deprecation warning
    :param str version: Specify what version the removed module is present in
    :param str removal_version: What version the module will be removed. If
                                '?' is used this implies an undefined future
                                version
    :param int stacklevel: How many entries deep in the call stack before
                           ignoring
    :param type category: warnings message category (this defaults to
                          ``DeprecationWarning`` when none is provided)
    """
    if inspect.ismodule(module):
        module_name = _get_qualified_name(module)
    elif isinstance(module, str):
        module_name = module
    else:
        _qual, type_name = _utils.get_qualified_name(type(module))
        raise TypeError(
            f"Unexpected module type '{type_name}' (expected string or "
            f"module type only)"
        )
    prefix = f"The '{module_name}' module usage is deprecated"
    if replacement:
        postfix = f", please use {replacement} instead"
    else:
        postfix = None
    out_message = _utils.generate_message(
        prefix,
        postfix=postfix,
        message=message,
        version=version,
        removal_version=removal_version,
    )
    _utils.deprecation(out_message, stacklevel=stacklevel, category=category)
