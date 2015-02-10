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

import functools
import inspect

from oslo_utils import reflection
import six
import wrapt

from debtcollector import _utils


def _get_qualified_name(obj):
    # Prefer the py3.x name (if we can get at it...)
    try:
        return (True, obj.__qualname__)
    except AttributeError:
        return (False, obj.__name__)


def _get_module_name(mod):
    return _get_qualified_name(mod)[1]


def remove(f=None, message=None, version=None, removal_version=None,
           stacklevel=3):
    """Decorates a function, method, or class to emit a deprecation warning

    :param str message: A message to include in the deprecation warning
    :param str version: Specify what version the removed function is present in
    :param str removal_version: What version the function will be removed. If
                                '?' is used this implies an undefined future
                                version
    :param int stacklevel: How many entries deep in the call stack before
                           ignoring
    """
    if f is None:
        return functools.partial(remove, message=message,
                                 version=version,
                                 removal_version=removal_version,
                                 stacklevel=stacklevel)

    @wrapt.decorator
    def wrapper(f, instance, args, kwargs):
        qualified, f_name = _get_qualified_name(f)
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
                    module_name = _get_module_name(inspect.getmodule(f))
                    if module_name == '__main__':
                        f_name = reflection.get_class_name(
                            f, fully_qualified=False)
                    else:
                        f_name = reflection.get_class_name(
                            f, fully_qualified=True)
                # Decorator was a used on a function
                else:
                    thing_post = '()'
                    module_name = _get_module_name(inspect.getmodule(f))
                    if module_name != '__main__':
                        f_name = reflection.get_callable_name(f)
            # Decorator was used on a classmethod or instancemethod
            else:
                thing_post = '()'
                base_name = reflection.get_class_name(instance,
                                                      fully_qualified=False)
            if base_name:
                thing_name = ".".join([base_name, f_name])
            else:
                thing_name = f_name
        else:
            thing_name = f_name
        if thing_post:
            thing_name += thing_post
        prefix = prefix_pre + " '%s' is deprecated" % (thing_name)
        out_message = _utils.generate_message(
            prefix,
            version=version,
            removal_version=removal_version,
            message=message)
        _utils.deprecation(out_message, stacklevel)
        return f(*args, **kwargs)
    return wrapper(f)


def removed_kwarg(old_name, message=None,
                  version=None, removal_version=None, stacklevel=3):
    """Decorates a kwarg accepting function to deprecate a removed kwarg."""

    prefix = "Using the '%s' argument is deprecated" % old_name
    out_message = _utils.generate_message(
        prefix, postfix=None, message=message, version=version,
        removal_version=removal_version)

    def decorator(f):

        @six.wraps(f)
        def wrapper(*args, **kwargs):
            if old_name in kwargs:
                _utils.deprecation(out_message, stacklevel=stacklevel)
            return f(*args, **kwargs)

        return wrapper

    return decorator


def removed_module(module, replacement=None, message=None,
                   version=None, removal_version=None, stacklevel=3):
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
    """
    if inspect.ismodule(module):
        module_name = _get_module_name(module)
    elif isinstance(module, six.string_types):
        module_name = module
    else:
        _qual, type_name = _get_qualified_name(type(module))
        raise TypeError("Unexpected module type '%s' (expected string or"
                        " module type only)" % type_name)
    prefix = "The '%s' module usage is deprecated" % module_name
    if replacement:
        postfix = ", please use %s instead" % replacement
    else:
        postfix = None
    out_message = _utils.generate_message(prefix,
                                          postfix=postfix, message=message,
                                          version=version,
                                          removal_version=removal_version)
    _utils.deprecation(out_message, stacklevel)
