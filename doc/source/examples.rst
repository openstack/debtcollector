========
Examples
========

Removing a class/method/function
--------------------------------

To signal to a user that a method (staticmethod, classmethod, or regular
instance method) or a class or function is going to be removed at some point
in the future the :py:func:`~debtcollector.removals.remove` function/decorator
can be used to achieve this in a non-destructive manner.

A basic example to do just this (on a method/function):

.. doctest::

    >>> from debtcollector import removals
    >>> import warnings
    >>> warnings.simplefilter('always')
    >>> class Car(object):
    ...   @removals.remove
    ...   def start(self):
    ...     pass
    ...
    >>> c = Car()
    >>> c.start()
    __main__:1: DeprecationWarning: Using function/method Car.start is deprecated

A basic example to do just this (on a class):

.. doctest::

    >>> from debtcollector import removals
    >>> import warnings
    >>> warnings.simplefilter('always')
    >>> @removals.remove
    ... class Pinto(object):
    ...   pass
    ...
    >>> p = Pinto()
    __main__:1: DeprecationWarning: Using class Pinto is deprecated

Moving a method
---------------

To move a *instance* method from an existing one to a new one
the :py:func:`~debtcollector.moves.moved_method` function/decorator can be
used to achieve this in a non-destructive manner.

A basic example to do just this:

.. doctest::

    >>> from debtcollector import moves
    >>> import warnings
    >>> warnings.simplefilter('always')
    >>> class Cat(object):
    ...   @moves.moved_method('meow')
    ...   def mewow(self):
    ...     return self.meow()
    ...   def meow(self):
    ...     return 'kitty'
    ...
    >>> c = Cat()
    >>> c.mewow()
    __main__:1: DeprecationWarning: Method 'Cat.mewow()' has moved to 'Cat.meow()'
    'kitty'
    >>> c.meow()
    'kitty'

Moving a property
-----------------

To move a *instance* property from an existing one to a new one
the :py:func:`~debtcollector.moves.moved_property` function/decorator can be
used to achieve this in a non-destructive manner.

A basic example to do just this:

.. doctest::

    >>> from debtcollector import moves
    >>> import warnings
    >>> warnings.simplefilter('always')
    >>> class Dog(object):
    ...   @property
    ...   @moves.moved_property('bark')
    ...   def burk(self):
    ...     return self.bark
    ...   @property
    ...   def bark(self):
    ...     return 'woof'
    ...
    >>> d = Dog()
    >>> d.burk
    __main__:1: DeprecationWarning: Property 'Dog.burk' has moved to 'Dog.bark'
    'woof'
    >>> d.bark
    'woof'

Moving a class
--------------

To move a *class* from an existing one to a new one
the :py:func:`~debtcollector.moves.moved_class` type generator function can
be used to achieve this in a non-destructive manner.

A basic example to do just this:

.. doctest::

    >>> from debtcollector import moves
    >>> import warnings
    >>> warnings.simplefilter('always')
    >>> class WizBang(object):
    ...   pass
    ...
    >>> OldWizBang = moves.moved_class(WizBang, 'OldWizBang', __name__)
    >>> a = OldWizBang()
    __main__:1: DeprecationWarning: Class '__main__.OldWizBang' has moved to '__main__.WizBang'
    >>> b = WizBang()

Renaming a keyword argument
---------------------------

To notify the user when a keyword argument has been replaced with a new and
improved keyword argument and the user is still using the old keyword argument
the :py:func:`~debtcollector.renames.renamed_kwarg` function/decorator
can be used to achieve this in a non-destructive manner.

A basic example to do just this:

.. doctest::

    >>> from debtcollector import renames
    >>> import warnings
    >>> warnings.simplefilter('always')
    >>> @renames.renamed_kwarg('snizzle', 'nizzle')
    ... def do_the_deed(snizzle=True, nizzle=True):
    ...   print(snizzle)
    ...   print(nizzle)
    ...
    >>> do_the_deed()
    True
    True
    >>> do_the_deed(snizzle=False)
    __main__:1: DeprecationWarning: Using the 'snizzle' argument is deprecated, please use the 'nizzle' argument instead
    False
    True
    >>> do_the_deed(nizzle=False)
    True
    False

Further customizing the emitted messages
----------------------------------------

It is typically useful to tell the user when a deprecation has started and
when the deprecated item will be offically removed (deleted or other). To
enable this all the currently provided functions this library provides
take a ``message``, ``version`` and ``removal_version`` keyword arguments.
These are used in forming the message that is shown to the user when they
trigger the deprecated activity.

A basic example to do just this:

.. doctest::

    >>> from debtcollector import renames
    >>> import warnings
    >>> warnings.simplefilter('always')
    >>> @renames.renamed_kwarg('snizzle', 'nizzle', version="0.5", removal_version="0.7")
    ... def do_the_deed(snizzle=True, nizzle=True):
    ...   pass
    ...
    >>> do_the_deed(snizzle=False)
    __main__:1: DeprecationWarning: Using the 'snizzle' argument is deprecated in version '0.5' and will be removed in version '0.7', please use the 'nizzle' argument instead

If the ``removal_version`` is unknown the special character ``?`` can be used
instead (to denote that the deprecated activity will be removed sometime in
the future).

A basic example to do just this:

.. doctest::

    >>> from debtcollector import renames
    >>> import warnings
    >>> warnings.simplefilter('always')
    >>> @renames.renamed_kwarg('snizzle', 'nizzle', version="0.5", removal_version="?")
    ... def do_the_deed(snizzle=True, nizzle=True):
    ...   pass
    ...
    >>> do_the_deed(snizzle=False)
    __main__:1: DeprecationWarning: Using the 'snizzle' argument is deprecated in version '0.5' and will be removed in a future version, please use the 'nizzle' argument instead

To further customize the message (with a special postfix) the ``message``
keyword argument can be provided.

A basic example to do just this:

.. doctest::

    >>> from debtcollector import renames
    >>> import warnings
    >>> warnings.simplefilter('always')
    >>> @renames.renamed_kwarg('snizzle', 'nizzle', message="Pretty please stop using it")
    ... def do_the_deed(snizzle=True, nizzle=True):
    ...   pass
    ...
    >>> do_the_deed(snizzle=False)
    __main__:1: DeprecationWarning: Using the 'snizzle' argument is deprecated, please use the 'nizzle' argument instead: Pretty please stop using it
