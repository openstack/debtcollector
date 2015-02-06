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
import wrapt

from debtcollector import _utils


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
        try:
            # Prefer the py3.x name (if we can get at it...)
            f_name = f.__qualname__
            qualified = True
            if inspect.isclass(f):
                _prefix_pre = "Using class"
            else:
                _prefix_pre = "Using function/method"
        except AttributeError:
            f_name = f.__name__
            qualified = False

        if not qualified:
            _prefix_pre = "Using function/method"
            if instance is None:
                # Decorator was used on a class
                if inspect.isclass(f):
                    _prefix_pre = "Using class"
                    module_name = inspect.getmodule(f).__name__
                    if module_name == '__main__':
                        f_name = reflection.get_class_name(
                            f, fully_qualified=False)
                    else:
                        f_name = reflection.get_class_name(
                            f, fully_qualified=True)
                    base_name = None
                # Decorator was a used on a function
                else:
                    module_name = inspect.getmodule(f).__name__
                    if module_name != '__main__':
                        f_name = reflection.get_callable_name(f)
                    base_name = None
            # Decorator was used on a classmethod or instancemethod
            else:
                base_name = reflection.get_class_name(instance,
                                                      fully_qualified=False)
            if base_name:
                function_name = ".".join([base_name, f_name])
            else:
                function_name = f_name
        else:
            function_name = f_name
        _prefix = _prefix_pre + " %s is deprecated" % function_name
        out_message = _utils.generate_message(
            _prefix,
            version=version,
            removal_version=removal_version,
            message=message)
        _utils.deprecation(out_message, stacklevel)
        return f(*args, **kwargs)
    return wrapper(f)
