#    Copyright (C) 2014 Yahoo! Inc. All Rights Reserved.
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

import debtcollector
from debtcollector import moves
from debtcollector import removals
from debtcollector import renames
from debtcollector.tests import base as test_base


@renames.renamed_kwarg('blip', 'blop')
def blip_blop(blip=1, blop=1):
    return (blip, blop)


@renames.renamed_kwarg('blip', 'blop', category=PendingDeprecationWarning)
def blip_blop_2(blip=1, blop=1):
    return (blip, blop)


class WoofWoof(object):
    @property
    def bark(self):
        return 'woof'

    @property
    @moves.moved_property('bark')
    def burk(self):
        return self.bark

    @property
    @moves.moved_property('bark', category=PendingDeprecationWarning)
    def berk(self):
        return self.bark

    @removals.removed_kwarg('resp', message="Please use 'response' instead")
    @classmethod
    def factory(cls, resp=None, response=None):
        return 'super-duper'


class KittyKat(object):

    @moves.moved_method('supermeow')
    def meow(self):
        return self.supermeow()

    @moves.moved_method('supermeow', category=PendingDeprecationWarning)
    def maow(self):
        return self.supermeow()

    def supermeow(self):
        return 'supermeow'


class NewHotness(object):
    def hot(self):
        return 'cold'


@removals.remove()
def crimson_lightning(fake_input=None):
    return fake_input


@removals.remove(category=PendingDeprecationWarning)
def crimson_lightning_to_remove(fake_input=None):
    return fake_input


@removals.remove()
def red_comet():
    return True


@removals.remove(category=PendingDeprecationWarning)
def blue_comet():
    return True


def yellow_sun():
    """Yellow."""
    return True


yellowish_sun = moves.moved_function(yellow_sun, 'yellowish_sun', __name__)


@removals.remove()
class EFSF(object):
    pass


@removals.remove(category=PendingDeprecationWarning)
class EFSF_2(object):
    pass


class ThingB(object):
    @removals.remove()
    def black_tristars(self):
        pass

    @removals.remove(category=PendingDeprecationWarning)
    def blue_tristars(self):
        pass

    @removals.remove()
    @classmethod
    def white_wolf(cls):
        pass

    @removals.remove(category=PendingDeprecationWarning)
    @classmethod
    def yellow_wolf(cls):
        pass

    @removals.remove()
    @staticmethod
    def blue_giant():
        pass

    @removals.remove(category=PendingDeprecationWarning)
    @staticmethod
    def green_giant():
        pass


OldHotness = moves.moved_class(NewHotness, 'OldHotness', __name__)

OldHotness2 = moves.moved_class(NewHotness, 'OldHotness', __name__,
                                category=PendingDeprecationWarning)


class DeprecateAnythingTest(test_base.TestCase):
    def test_generation(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            debtcollector.deprecate("Its broken")
            debtcollector.deprecate("Its really broken")
        self.assertEqual(2, len(capture))


class MovedInheritableClassTest(test_base.TestCase):
    def test_broken_type_class(self):
        self.assertRaises(TypeError, moves.moved_class, 'b', __name__)

    def test_basics(self):
        old = OldHotness()
        self.assertIsInstance(old, NewHotness)
        self.assertEqual('cold', old.hot())

    def test_warnings_emitted_creation(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            OldHotness()
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

    def test_warnings_emitted_creation_pending(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            OldHotness2()
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(PendingDeprecationWarning, w.category)

    def test_existing_refer_subclass(self):

        class MyOldThing(OldHotness):
            pass

        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            MyOldThing()

        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)


class MovedPropertyTest(test_base.TestCase):
    def test_basics(self):
        dog = WoofWoof()
        self.assertEqual('woof', dog.burk)
        self.assertEqual('woof', dog.bark)

    def test_warnings_emitted(self):
        dog = WoofWoof()
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual('woof', dog.burk)
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

    def test_warnings_emitted_pending(self):
        dog = WoofWoof()
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual('woof', dog.berk)
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(PendingDeprecationWarning, w.category)

    def test_warnings_not_emitted(self):
        dog = WoofWoof()
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual('woof', dog.bark)
        self.assertEqual(0, len(capture))


class MovedFunctionTest(test_base.TestCase):
    def test_basics(self):
        self.assertTrue(yellowish_sun())
        self.assertTrue(yellow_sun())
        self.assertEqual("Yellow.", yellowish_sun.__doc__)

    def test_warnings_emitted(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertTrue(yellowish_sun())
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)


class MovedMethodTest(test_base.TestCase):
    def test_basics(self):
        c = KittyKat()
        self.assertEqual('supermeow', c.meow())
        self.assertEqual('supermeow', c.supermeow())

    def test_warnings_emitted(self):
        c = KittyKat()
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual('supermeow', c.meow())
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

    def test_warnings_emitted_pending(self):
        c = KittyKat()
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual('supermeow', c.maow())
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(PendingDeprecationWarning, w.category)

    def test_warnings_not_emitted(self):
        c = KittyKat()
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual('supermeow', c.supermeow())
        self.assertEqual(0, len(capture))


class RenamedKwargTest(test_base.TestCase):
    def test_basics(self):
        self.assertEqual((1, 1), blip_blop())
        self.assertEqual((2, 1), blip_blop(blip=2))
        self.assertEqual((1, 2), blip_blop(blop=2))
        self.assertEqual((2, 2), blip_blop(blip=2, blop=2))

    def test_warnings_emitted(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual((2, 1), blip_blop(blip=2))
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

    def test_warnings_emitted_classmethod(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            WoofWoof.factory(resp="hi")
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            WoofWoof.factory(response="hi")
        self.assertEqual(0, len(capture))

    def test_warnings_emitted_pending(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual((2, 1), blip_blop_2(blip=2))
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(PendingDeprecationWarning, w.category)

    def test_warnings_not_emitted(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual((1, 2), blip_blop(blop=2))
        self.assertEqual(0, len(capture))


class RemovalTests(test_base.TestCase):
    def test_function_args(self):
        self.assertEqual(666, crimson_lightning(666))

    def test_function_noargs(self):
        self.assertTrue(red_comet())

    def test_deprecated_kwarg(self):

        @removals.removed_kwarg('b')
        def f(b=2):
            return b

        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual(3, f(b=3))
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual(2, f())
        self.assertEqual(0, len(capture))

    def test_pending_deprecated_kwarg(self):

        @removals.removed_kwarg('b', category=PendingDeprecationWarning)
        def f(b=2):
            return b

        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual(3, f(b=3))
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(PendingDeprecationWarning, w.category)

        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual(2, f())
        self.assertEqual(0, len(capture))

    def test_warnings_emitted_function_args(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual(666, crimson_lightning(666))
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

    def test_pending_warnings_emitted_function_args(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual(666, crimson_lightning_to_remove(666))
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(PendingDeprecationWarning, w.category)

    def test_warnings_emitted_function_noargs(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertTrue(red_comet())
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

    def test_pending_warnings_emitted_function_noargs(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertTrue(blue_comet())
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(PendingDeprecationWarning, w.category)

    def test_warnings_emitted_class(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            EFSF()
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

    def test_pending_warnings_emitted_class(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            EFSF_2()
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(PendingDeprecationWarning, w.category)

    def test_warnings_emitted_instancemethod(self):
        zeon = ThingB()
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            zeon.black_tristars()
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

    def test_pending_warnings_emitted_instancemethod(self):
        zeon = ThingB()
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            zeon.blue_tristars()
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(PendingDeprecationWarning, w.category)

    def test_pending_warnings_emitted_classmethod(self):
        zeon = ThingB()
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            zeon.yellow_wolf()
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(PendingDeprecationWarning, w.category)

    def test_warnings_emitted_classmethod(self):
        zeon = ThingB()
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            zeon.white_wolf()
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

    def test_warnings_emitted_staticmethod(self):
        zeon = ThingB()
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            zeon.blue_giant()
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

    def test_pending_warnings_emitted_staticmethod(self):
        zeon = ThingB()
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            zeon.green_giant()
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(PendingDeprecationWarning, w.category)

    def test_removed_module(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            removals.removed_module(__name__)
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

    def test_pending_removed_module(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            removals.removed_module(__name__,
                                    category=PendingDeprecationWarning)
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(PendingDeprecationWarning, w.category)

    def test_removed_module_bad_type(self):
        self.assertRaises(TypeError, removals.removed_module, 2)
