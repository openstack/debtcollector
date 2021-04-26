# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

try:
    # For Python 3.8 and later
    import importlib.metadata as importlib_metadata
except ImportError:
    # For everyone else
    import importlib_metadata

from debtcollector import _utils

__version__ = importlib_metadata.version('debtcollector')


def deprecate(prefix, postfix=None, message=None,
              version=None, removal_version=None,
              stacklevel=3, category=DeprecationWarning):
    """Helper to deprecate some thing using generated message format.

    :param prefix: prefix string used as the prefix of the output message
    :param postfix: postfix string used as the postfix of the output message
    :param message: message string used as ending contents of the deprecate
                    message
    :param version: version string (represents the version this
                    deprecation was created in)
    :param removal_version: version string (represents the version this
                            deprecation will be removed in); a string of '?'
                            will denote this will be removed in some future
                            unknown version
    :param stacklevel: stacklevel used in the :func:`warnings.warn` function
                       to locate where the users code is in the
                       :func:`warnings.warn` call
    :param category: the :mod:`warnings` category to use, defaults to
                     :py:class:`DeprecationWarning` if not provided
    """
    out_message = _utils.generate_message(prefix, postfix=postfix,
                                          version=version, message=message,
                                          removal_version=removal_version)
    _utils.deprecation(out_message, stacklevel=stacklevel,
                       category=category)
