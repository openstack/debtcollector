#    Copyright (C) 2015 Yahoo! Inc. All Rights Reserved.
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
import warnings

# See https://docs.python.org/3/library/builtins.html
_BUILTIN_MODULES = ('builtins', 'exceptions')
_enabled = True


def deprecation(
    message: str,
    stacklevel: int | None = None,
    category: type[Warning] | None = None,
) -> None:
    """Warns about some type of deprecation that has been (or will be) made.

    This helper function makes it easier to interact with the warnings module
    by standardizing the arguments that the warning function receives so that
    it is easier to use.

    This should be used to emit warnings to users (users can easily turn these
    warnings off/on, see https://docs.python.org/2/library/warnings.html
    as they see fit so that the messages do not fill up the users logs with
    warnings that they do not wish to see in production) about functions,
    methods, attributes or other code that is deprecated and will be removed
    in a future release (this is done using these warnings to avoid breaking
    existing users of those functions, methods, code; which a library should
    avoid doing by always giving at *least* N + 1 release for users to address
    the deprecation warnings).
    """
    if not _enabled:
        return None
    if category is None:
        category = DeprecationWarning
    if stacklevel is None:
        warnings.warn(message, category=category)
    else:
        warnings.warn(message, category=category, stacklevel=stacklevel)

    return None


def get_qualified_name(
    obj: Callable[..., Any] | types.ModuleType | builtins.function,
) -> tuple[bool, str]:
    # Prefer the py3.x name (if we can get at it...)
    try:
        return (True, obj.__qualname__)
    except AttributeError:
        return (False, obj.__name__)


def generate_message(
    prefix: str,
    postfix: str | None = None,
    message: str | None = None,
    version: str | None = None,
    removal_version: str | None = None,
) -> str:
    """Helper to generate a common message 'style' for deprecation helpers."""
    message_components = [prefix]
    if version:
        message_components.append(f" in version '{version}'")
    if removal_version:
        if removal_version == "?":
            message_components.append(
                " and will be removed in a future version"
            )
        else:
            message_components.append(
                f" and will be removed in version '{removal_version}'"
            )
    if postfix:
        message_components.append(postfix)
    if message:
        message_components.append(f": {message}")
    return ''.join(message_components)


def get_assigned(decorator: Any) -> tuple[str, ...]:
    """Helper to fix/workaround https://bugs.python.org/issue3445"""
    return functools.WRAPPER_ASSIGNMENTS


def get_class_name(
    obj: type[Any] | Callable[..., Any],
    fully_qualified: bool = True,
) -> str:
    """Get class name for object.

    If object is a type, fully qualified name of the type is returned.
    Else, fully qualified name of the type of the object is returned.
    For builtin types, just name is returned.
    """
    if not isinstance(obj, type):
        obj = type(obj)
    try:
        built_in = obj.__module__ in _BUILTIN_MODULES
    except AttributeError:
        pass
    else:
        if built_in:
            return obj.__name__

    if fully_qualified and hasattr(obj, '__module__'):
        return f'{obj.__module__}.{obj.__name__}'
    else:
        return obj.__name__


def get_method_self(method: Any) -> Any:
    """Gets the ``self`` object attached to this method (or none)."""
    if not inspect.ismethod(method):
        return None
    try:
        return getattr(method, '__self__')
    except AttributeError:
        return None


def get_callable_name(function: Callable[..., Any]) -> str:
    """Generate a name from callable.

    Tries to do the best to guess fully qualified callable name.
    """
    parts: tuple[str, str] | tuple[str, str, str]
    method_self = get_method_self(function)
    if method_self is not None:
        # This is a bound method.
        if isinstance(method_self, type):
            # This is a bound class method.
            im_class = method_self
        else:
            im_class = type(method_self)
        try:
            parts = (im_class.__module__, function.__qualname__)
        except AttributeError:
            parts = (im_class.__module__, im_class.__name__, function.__name__)
    elif inspect.ismethod(function) or inspect.isfunction(function):
        # This could be a function, a static method, a unbound method...
        try:
            parts = (function.__module__, function.__qualname__)
        except AttributeError:
            if hasattr(function, 'im_class'):
                # This is a unbound method, which exists only in python 2.x
                im_class = function.im_class
                parts = (
                    im_class.__module__,
                    im_class.__name__,
                    function.__name__,
                )
            else:
                parts = (function.__module__, function.__name__)
    else:
        if type(function) is type:
            im_class = function
        else:
            im_class = type(function)
        try:
            parts = (im_class.__module__, im_class.__qualname__)
        except AttributeError:
            parts = (im_class.__module__, im_class.__name__)
    # When running under sphinx it appears this can be none? if so just
    # don't include it...
    mod, rest = (parts[0], parts[1:])
    if not mod:
        return '.'.join(rest)
    else:
        return '.'.join(parts)
