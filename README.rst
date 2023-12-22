=============
Debtcollector
=============

.. image:: https://governance.openstack.org/tc/badges/debtcollector
    :target: https://governance.openstack.org/tc/reference/projects/oslo.html

.. image:: https://img.shields.io/pypi/v/debtcollector
    :target: https://pypi.org/project/debtcollector/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/dm/debtcollector
    :target: https://pypi.org/project/debtcollector/
    :alt: Downloads

.. image:: https://img.shields.io/pypi/types/debtcollector
    :target: https://pypi.org/project/debtcollector/
    :alt: Typing Status

A collection of Python deprecation patterns and strategies that help you
collect your technical debt in a non-destructive manner. The goal of this
library is to provide well documented developer facing deprecation
patterns that start of with a basic set and can expand into a larger
set of patterns as time goes on. The desired output of these patterns
is to apply the ``warnings`` module to emit ``DeprecationWarning``,
``PendingDeprecationWarning`` or similar derivative to developers using
libraries (or potentially applications) about future deprecations.

* Free software: Apache license
* Documentation: https://docs.openstack.org/debtcollector/latest
* Source: https://opendev.org/openstack/debtcollector
* Bugs: https://bugs.launchpad.net/debtcollector
* Release Notes: https://docs.openstack.org/releasenotes/debtcollector
