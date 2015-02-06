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

from debtcollector import moves
from debtcollector import removals
from debtcollector import renames
from debtcollector.tests import base as test_base


@renames.renamed_kwarg('blip', 'blop')
def blip_blop(blip=1, blop=1):
    return (blip, blop)


class WoofWoof(object):
    @property
    def bark(self):
        return 'woof'

    @property
    @moves.moved_property('bark')
    def burk(self):
        return self.bark


class KittyKat(object):

    @moves.moved_method('supermeow')
    def meow(self):
        return self.supermeow()

    def supermeow(self):
        return 'supermeow'


class NewHotness(object):
    def hot(self):
        return 'cold'


@removals.remove()
def crimson_lightning(fake_input=None):
    return fake_input


@removals.remove()
def red_comet():
    return True


@removals.remove()
class EFSF(object):
    pass


class ThingB(object):
    @removals.remove()
    def black_tristars(self):
        pass

    @removals.remove()
    @classmethod
    def white_wolf(cls):
        pass

    @removals.remove()
    @staticmethod
    def blue_giant():
        pass


OldHotness = moves.moved_class(NewHotness, 'OldHotness', __name__)


class MovedInheritableClassTest(test_base.TestCase):
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

    def test_warnings_not_emitted(self):
        dog = WoofWoof()
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual('woof', dog.bark)
        self.assertEqual(0, len(capture))


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

    def test_warnings_emitted_function_args(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertEqual(666, crimson_lightning(666))
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

    def test_warnings_emitted_function_noargs(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            self.assertTrue(red_comet())
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

    def test_warnings_emitted_class(self):
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            EFSF()
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

    def test_warnings_emitted_instancemethod(self):
        zeon = ThingB()
        with warnings.catch_warnings(record=True) as capture:
            warnings.simplefilter("always")
            zeon.black_tristars()
        self.assertEqual(1, len(capture))
        w = capture[0]
        self.assertEqual(DeprecationWarning, w.category)

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
