# -*- coding: utf-8 -*-

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

import warnings


def deprecation(message, stacklevel=None):
    """Warns about some type of deprecation that has been (or will be) made.

    This helper function makes it easier to interact with the warnings module
    by standardizing the arguments that the warning function recieves so that
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
    if stacklevel is None:
        warnings.warn(message, category=DeprecationWarning)
    else:
        warnings.warn(message,
                      category=DeprecationWarning, stacklevel=stacklevel)


def generate_message(prefix, postfix=None, message=None,
                     version=None, removal_version=None):
    """Helper to generate a common message 'style' for deprecation helpers."""
    message_components = [prefix]
    if version:
        message_components.append(" in version '%s'" % version)
    if removal_version:
        if removal_version == "?":
            message_components.append(" and will be removed in a future"
                                      " version")
        else:
            message_components.append(" and will be removed in version '%s'"
                                      % removal_version)
    if postfix:
        message_components.append(postfix)
    if message:
        message_components.append(": %s" % message)
    return ''.join(message_components)
