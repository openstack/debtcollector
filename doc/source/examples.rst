========
Examples
========

Removing a class/classmethod/method/function
--------------------------------------------

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

**Expected output:**

.. testoutput::

    __main__:1: DeprecationWarning: Using function/method 'Car.start()' is deprecated

A basic example to do just this (on a class):

.. doctest::

    >>> from debtcollector import removals
    >>> import warnings
    >>> warnings.simplefilter('always')
    >>> @removals.removed_class("Pinto")
    ... class Pinto(object):
    ...   pass
    ...
    >>> p = Pinto()

**Expected output:**

.. testoutput::

    __main__:1: DeprecationWarning: Using class 'Pinto' (either directly or via inheritance) is deprecated

A basic example to do just this (on a classmethod):

.. doctest::

    >>> from debtcollector import removals
    >>> import warnings
    >>> warnings.simplefilter("once")
    >>> class OldAndBusted(object):
    ...     @removals.remove
    ...     @classmethod
    ...     def fix_things(cls):
    ...         pass
    ...
    >>> OldAndBusted.fix_things()

**Expected output:**

.. testoutput::

    __main__:1: DeprecationWarning: Using function/method 'OldAndBusted.fix_things()' is deprecated

Removing a instance property
----------------------------

Use the :py:func:`~debtcollector.removals.removed_property` decorator
to signal that an attribute of a class is deprecated.

A basic example to do just this:

.. doctest::

    >>> import warnings
    >>> warnings.simplefilter("once")
    >>> from debtcollector import removals
    >>> class OldAndBusted(object):
    ...   @removals.removed_property
    ...   def thing(self):
    ...     return 'old-and-busted'
    ...   @thing.setter
    ...   def thing(self, value):
    ...     pass
    ...   @thing.deleter
    ...   def thing(self):
    ...     pass
    ...
    >>> o = OldAndBusted()
    >>> o.thing
    'old-and-busted'
    >>> o.thing = '2'
    >>> del o.thing

.. testoutput::

    __main__:1: DeprecationWarning: Reading the 'thing' property is deprecated
    __main__:1: DeprecationWarning: Setting the 'thing' property is deprecated
    __main__:1: DeprecationWarning: Deleting the 'thing' property is deprecated

Removing a keyword argument
---------------------------

A basic example to do just this (on a classmethod):

.. doctest::

    >>> import warnings
    >>> warnings.simplefilter("once")
    >>> from debtcollector import removals
    >>> class OldAndBusted(object):
    ...     @removals.removed_kwarg('resp', message="Please use 'response' instead")
    ...     @classmethod
    ...     def factory(cls, resp=None, response=None):
    ...         response = resp or response
    ...         return response
    ...
    >>> OldAndBusted.factory(resp='super-duper')
    'super-duper'

.. testoutput::

    __main__:1: DeprecationWarning: Using the 'resp' argument is deprecated: Please use 'response' instead

A basic example to do just this (on a ``__init__`` method):

.. doctest::

    >>> import warnings
    >>> warnings.simplefilter("once")
    >>> from debtcollector import removals
    >>> class OldAndBusted(object):
    ...     @removals.removed_kwarg('bleep')
    ...     def __init__(self, bleep=None):
    ...         self.bloop = bleep
    ...
    >>> o = OldAndBusted(bleep=2)

.. testoutput::

    __main__:1: DeprecationWarning: Using the 'bleep' argument is deprecated

Changing the default value of a keyword argument
------------------------------------------------

A basic example to do just this:

.. doctest::

    >>> import warnings
    >>> warnings.simplefilter("once")
    >>> from debtcollector import updating
    >>> class OldAndBusted(object):
    ...     ip = '127.0.0.1'
    ...     @updating.updated_kwarg_default_value('type', 'http', 'https')
    ...     def url(self, type='http'):
    ...         response = '%s://%s' % (type, self.ip)
    ...         return response
    ...
    >>> OldAndBusted().url()
    'http://127.0.0.1'

.. testoutput::

    __main__:1: FutureWarning: The http argument is changing its default value to https, please update the code to explicitly set http as the value


A basic classmethod example.

.. note:: the @classmethod decorator is before the debtcollector one

.. doctest::

    >>> import warnings
    >>> warnings.simplefilter("once")
    >>> from debtcollector import updating
    >>> class OldAndBusted(object):
    ...     ip = '127.0.0.1'
    ...     @classmethod
    ...     @updating.updated_kwarg_default_value('type', 'http', 'https')
    ...     def url(cls, type='http'):
    ...         response = '%s://%s' % (type, cls.ip)
    ...         return response
    ...
    >>> OldAndBusted.url()
    'http://127.0.0.1'

.. testoutput::

    __main__:1: FutureWarning: The http argument is changing its default value to https, please update the code to explicitly set http as the value

Moving a function
-----------------

To change the name or location of a regular function use the
:py:func:`~debtcollector.moves.moved_function` function:

.. doctest::

    >>> from debtcollector import moves
    >>> import warnings
    >>> warnings.simplefilter('always')
    >>> def new_thing():
    ...   return "new thing"
    ...
    >>> old_thing = moves.moved_function(new_thing, 'old_thing', __name__)
    >>> new_thing()
    'new thing'
    >>> old_thing()
    'new thing'

**Expected output:**

.. testoutput::

    __main__:1: DeprecationWarning: Function '__main__.old_thing()' has moved to '__main__.new_thing()'

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
    'kitty'
    >>> c.meow()
    'kitty'

**Expected output:**

.. testoutput::

    __main__:1: DeprecationWarning: Method 'Cat.mewow()' has moved to 'Cat.meow()'

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
    'woof'
    >>> d.bark
    'woof'

**Expected output:**

.. testoutput::

    __main__:1: DeprecationWarning: Property 'Dog.burk' has moved to 'Dog.bark'

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
    >>> b = WizBang()

**Expected output:**

.. testoutput::

    __main__:1: DeprecationWarning: Class '__main__.OldWizBang' has moved to '__main__.WizBang'

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
    ...   return (snizzle, nizzle)
    ...
    >>> do_the_deed()
    (True, True)
    >>> do_the_deed(snizzle=False)
    (False, True)
    >>> do_the_deed(nizzle=False)
    (True, False)

**Expected output:**

.. testoutput::

    __main__:1: DeprecationWarning: Using the 'snizzle' argument is deprecated, please use the 'nizzle' argument instead

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

**Expected output:**

.. testoutput::

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

**Expected output:**

.. testoutput::

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

**Expected output:**

.. testoutput::

    __main__:1: DeprecationWarning: Using the 'snizzle' argument is deprecated, please use the 'nizzle' argument instead: Pretty please stop using it

Deprecating anything else
-------------------------

For use-cases which do not fit the above decorators, properties other
provided functionality the final option is to use debtcollectors
the :py:func:`~debtcollector.deprecate` function to make your own
messages (using the message building logic that debtcollector uses itself).

A basic example to do just this:

.. doctest::

    >>> import warnings
    >>> warnings.simplefilter("always")
    >>> import debtcollector
    >>> debtcollector.deprecate("This is no longer supported", version="1.0")

.. testoutput::

    __main__:1: DeprecationWarning: This is no longer supported in version '1.0'
