# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
An immutable dictionary view.
"""

from __future__ import print_function, absolute_import

import sys
import os
try:
    from collections.abc import Mapping
except ImportError:
    # Python 2
    from collections import Mapping  # pylint: disable=deprecated-class

__all__ = ['DictView']

# This env var is set when building the docs. It causes the methods that are
# supposed to exist only under certain circumstances, not to be removed, so
# that they appear in the docs.
_BUILDING_DOCS = os.environ.get('BUILDING_DOCS', False)

# Indicates Python dict supports the iter..() and view..() methods
_DICT_SUPPORTS_ITER_VIEW = sys.version_info[0:2] == (2, 7)

# Indicates Python dict supports the has_key() method
_DICT_SUPPORTS_HAS_KEY = sys.version_info[0:2] == (2, 7)

# Indicates Python dict supports the __reversed__() method
_DICT_SUPPORTS_REVERSED = sys.version_info[0:2] >= (3, 8)

# Indicates Python dict supports the __or__/__ror__() methods
_DICT_SUPPORTS_OR = sys.version_info[0:2] >= (3, 9)


class DictView(Mapping):
    # pylint: disable=line-too-long
    """
    An immutable dictionary view.

    Derived from :class:`~py3:collections.abc.Mapping`.

    This class provides an immutable view on a possibly mutable mapping
    object. The mapping object must be an instance of
    :class:`~py3:collections.abc.Mapping`, e.g. :class:`dict`, or a
    user-defined class.

    This can be used for example when a class maintains a dictionary that should
    be made available to users of the class without allowing them to modify the
    dictionary.

    In the description of this class, the term 'view' always refers to the
    :class:`DictView` object, and the term 'dictionary' or
    'underlying dictionary' refers to the mapping object the view is based on.

    The :class:`DictView` class supports the complete behavior of Python class
    :class:`dict`, except for any methods that would modify the dictionary.
    Note that the non-modifying methods of class :class:`dict` are a superset of
    the methods defined for the abstract class
    :class:`~py3:collections.abc.Mapping` (the methods are listed in the table
    at the top of the linked page).

    The view is "live": Since the view class delegates all operations to the
    underlying dictionary, any modification of the underlying dictionary object
    will be visible in the view object.

    Note that only the view object is immutable, not its items. So if the values
    in the underlying dictionary are mutable objects, they can be modified
    through the view.

    Note that in Python, augmented assignment (e.g. ``x += y``) is not
    guaranteed to modify the left hand object in place, but can result in the
    left hand name being bound to a new object (like in ``x = x + y``).
    For details, see
    `object.__iadd__() <https://docs.python.org/3/reference/datamodel.html#object.__iadd__>`_.

    For the DictView class, augmented assignment is supported and results in
    binding the left hand name to a new DictView object.
    """  # noqa: E501
    # pylint: enable=line-too-long

    __slots__ = ['_dict']

    def __init__(self, a_dict):
        """
        Parameters:

          a_dict (:class:`~py3:collections.abc.Mapping`):
            The underlying dictionary.
            If this object is a DictView, its underlying dictionary is used.
        """
        if not isinstance(a_dict, Mapping):
            raise TypeError(
                "The a_dict parameter must be a Mapping, but is: {}".
                format(type(a_dict)))
        if isinstance(a_dict, DictView):
            a_dict = a_dict._dict
        self._dict = a_dict

    @property
    def dict(self):
        """
        The underlying dictionary.

        Access to the underlying dictionary is provided for purposes such as
        conversion to JSON or other cases where the view classes do not work.
        This access should not be used to modify the underlying dictionary.
        """
        return self._dict

    def __repr__(self):
        """
        ``repr(self)``:
        Return a string representation of the view suitable for debugging.

        The underlying dictionary is represented using its ``repr()``
        representation.
        """
        return "{0.__class__.__name__}({1!r})".format(self, self._dict)

    def __getstate__(self):
        """Support for pickling."""
        # Needed on Python 2 due to the use of slots
        a_dict = dict()
        for attr in self.__slots__:
            a_dict[attr] = getattr(self, attr)

        # Support for objects that also have __dict__, e.g. user defined
        # derived classes that did not define __slots__:
        if hasattr(self, '__dict__'):
            for attr in self.__dict__:
                a_dict[attr] = getattr(self, attr)

        return a_dict

    def __setstate__(self, a_dict):
        """Support for unpickling."""
        # Needed on Python 2 due to the use of slots
        for attr in a_dict:
            setattr(self, attr, a_dict[attr])

    def __getitem__(self, key):
        """
        ``self[key]``:
        Return the value of the dictionary item with a key.

        Raises:
          KeyError: An item with the key does not exist.
        """
        return self._dict[key]

    def __len__(self):
        """
        ``len(self)``:
        Return the number of items in the dictionary.

        The return value is the number of items in the underlying dictionary.
        """
        return len(self._dict)

    def __contains__(self, key):
        """
        ``value in self``:
        Return a boolean indicating whether the dictionary contains an item with
        a key.

        The return value indicates whether the underlying dictionary contains an
        item that has the specified key.
        """
        return key in self._dict

    def __reversed__(self):
        """
        ``reversed(self) ...``:
        Return an iterator through the dictionary keys in reversed iteration
        order.

        Added in Python 3.8.

        The returned iterator yields the keys in the underlying dictionary in
        reversed iteration order.
        """
        return reversed(self._dict)

    def get(self, key, default=None):
        """
        Return the value of the dictionary item with a key or a default value.
        """
        return self._dict.get(key, default)

    def has_key(self, key):
        """
        Python 2 only: Return a boolean indicating whether the dictionary
        contains an item with a key.

        Raises:
          AttributeError: The method does not exist on Python 3.
        """
        return self._dict.has_key(key)  # noqa: W601

    # Iteration methods

    def keys(self):
        # pylint: disable=line-too-long
        """
        Return the dictionary keys in iteration order.

        The keys of the underlying dictionary are returned as a view in
        Python 3 and as a list in Python 2.

        See
        `Dictionary View Objects on Python 3 <https://docs.python.org/3/library/stdtypes.html#dictionary-view-objects>`_ for details about view objects.
        """  # noqa: E501
        # pylint: enable=line-too-long
        return self._dict.keys()

    def values(self):
        # pylint: disable=line-too-long
        """
        Return the dictionary values in iteration order.

        The values of the underlying dictionary are returned as a view in
        Python 3 and as a list in Python 2.

        See
        `Dictionary View Objects on Python 3 <https://docs.python.org/3/library/stdtypes.html#dictionary-view-objects>`_ for details about view objects.
        """  # noqa: E501
        # pylint: enable=line-too-long
        return self._dict.values()

    def items(self):
        # pylint: disable=line-too-long
        """
        Return the dictionary items in iteration order.

        Each returned item is a tuple of key and value.
        The items of the underlying dictionary are returned as a view in
        Python 3 and as a list in Python 2.

        See
        `Dictionary View Objects on Python 3 <https://docs.python.org/3/library/stdtypes.html#dictionary-view-objects>`_ for details about view objects.
        """  # noqa: E501
        # pylint: enable=line-too-long
        return self._dict.items()

    def iterkeys(self):
        """
        Python 2 only: Return an iterator through the dictionary keys in
        iteration order.

        Raises:
          AttributeError: The method does not exist on Python 3.
        """
        return self._dict.iterkeys()

    def itervalues(self):
        """
        Python 2 only: Return an iterator through the dictionary values in
        iteration order.

        Raises:
          AttributeError: The method does not exist on Python 3.
        """
        return self._dict.itervalues()

    def iteritems(self):
        """
        Python 2 only: Return an iterator through the dictionary items in
        iteration order.

        Each item is a tuple of key and value.

        Raises:
          AttributeError: The method does not exist on Python 3.
        """
        return self._dict.iteritems()

    def viewkeys(self):
        # pylint: disable=line-too-long
        """
        Python 2 only: Return a view on the dictionary keys in iteration order.

        The keys of the underlying dictionary are returned as a view.

        See
        `Dictionary View Objects on Python 2 <https://docs.python.org/2/library/stdtypes.html#dictionary-view-objects>`_ for details about view objects.

        Raises:
          AttributeError: The method does not exist on Python 3.
        """  # noqa: E501
        # pylint: enable=line-too-long
        return self._dict.viewkeys()

    def viewvalues(self):
        # pylint: disable=line-too-long
        """
        Python 2 only: Return a view on the dictionary values in iteration
        order.

        The values of the underlying dictionary are returned as a view.

        See
        `Dictionary View Objects on Python 2 <https://docs.python.org/2/library/stdtypes.html#dictionary-view-objects>`_ for details about view objects.

        Raises:
          AttributeError: The method does not exist on Python 3.
        """  # noqa: E501
        # pylint: enable=line-too-long
        return self._dict.viewvalues()

    def viewitems(self):
        # pylint: disable=line-too-long
        """
        Python 2 only: Return a view on the dictionary items in iteration order.

        Each returned item is a tuple of key and value.
        The items of the underlying dictionary are returned as a view.

        See
        `Dictionary View Objects on Python 2 <https://docs.python.org/2/library/stdtypes.html#dictionary-view-objects>`_ for details about view objects.

        Raises:
          AttributeError: The method does not exist on Python 3.
        """  # noqa: E501
        # pylint: enable=line-too-long
        return self._dict.viewitems()

    def __iter__(self):
        """
        Return an iterator through the dictionary keys in iteration order.
        """
        return iter(self._dict)

    def copy(self):
        """
        Return a new view on a shallow copy of the dictionary.

        The returned :class:`DictView` object is a new view object on a
        dictionary object of the type of the underlying dictionary.

        If the dictionary type is immutable, the returned dictionary object may
        be the underlying dictionary object. If the dictionary type is mutable,
        the returned dictionary is a new dictionary object that is a shallow
        copy of the underlying dictionary object.
        """
        org_class = self._dict.__class__
        new_dict = org_class(self._dict)  # May be same object if immutable
        return DictView(new_dict)

    def __eq__(self, other):
        """
        ``self == other``:
        Return a boolean indicating whether the dictionary is equal to the
        other object.

        Compared are the underlying dictionary of the left hand view object
        and the right hand object (or in case of a DictView, its underlying
        dictionary).
        """
        # pylint: disable=protected-access
        other_dict = other._dict if isinstance(other, DictView) else other
        return self._dict == other_dict

    def __ne__(self, other):
        """
        ``self != other``:
        Return a boolean indicating whether the dictionary is not equal to the
        other dictionary.

        Compared are the underlying dictionary of the left hand view object
        and the right hand object (or in case of a DictView, its underlying
        dictionary).
        """
        # pylint: disable=protected-access
        other_dict = other._dict if isinstance(other, DictView) else other
        return self._dict != other_dict

    def __gt__(self, other):
        """
        ``self > other``:
        Return a boolean indicating whether the dictionary is greater than
        the other dictionary.

        Whether ordering comparison is supported and how ordering is defined
        depends on the underlying dictionary and the other dictionary. For
        example, the standard Python :class:`dict` class does not support
        ordering comparisons on Python 3.

        The other object must be a :class:`dict` or :class:`DictView`.

        Raises:
          TypeError: The other object is not a dict or DictView.
          TypeError: The underlying dictionary does not support ordering
            comparisons.
        """
        # pylint: disable=protected-access
        other_dict = other._dict if isinstance(other, DictView) else other
        return self._dict > other_dict

    def __lt__(self, other):
        """
        ``self < other``:
        Return a boolean indicating whether the dictionary is less than
        the other dictionary.

        Whether ordering comparison is supported and how ordering is defined
        depends on the underlying dictionary and the other dictionary. For
        example, the standard Python :class:`dict` class does not support
        ordering comparisons on Python 3.

        The other object must be a :class:`dict` or :class:`DictView`.

        Raises:
          TypeError: The other object is dict a set or DictView.
          TypeError: The underlying dictionary does not support ordering
            comparisons.
        """
        # pylint: disable=protected-access
        other_dict = other._dict if isinstance(other, DictView) else other
        return self._dict < other_dict

    def __ge__(self, other):
        """
        ``self >= other``:
        Return a boolean indicating whether the dictionary is greater than or
        equal to the other dictionary.

        Whether ordering comparison is supported and how ordering is defined
        depends on the underlying dictionary and the other dictionary. For
        example, the standard Python :class:`dict` class does not support
        ordering comparisons on Python 3.

        The other object must be a :class:`dict` or :class:`DictView`.

        Raises:
          TypeError: The other object is not a dict or DictView.
          TypeError: The underlying dictionary does not support ordering
            comparisons.
        """
        # pylint: disable=protected-access
        other_dict = other._dict if isinstance(other, DictView) else other
        return self._dict >= other_dict

    def __le__(self, other):
        """
        ``self <= other``:
        Return a boolean indicating whether the dictionary is less than or
        equal to the other dictionary.

        Whether ordering comparison is supported and how ordering is defined
        depends on the underlying dictionary and the other dictionary. For
        example, the standard Python :class:`dict` class does not support
        ordering comparisons on Python 3.

        The other object must be a :class:`dict` or :class:`DictView`.

        Raises:
          TypeError: The other object is not a dict or DictView.
          TypeError: The underlying dictionary does not support ordering
            comparisons.
        """
        # pylint: disable=protected-access
        other_dict = other._dict if isinstance(other, DictView) else other
        return self._dict <= other_dict

    def __hash__(self):
        """
        ``hash(self)``:
        Return a hash value for the dictionary.

        Whether hashing is supported depends on the underlying dictionary. For
        example, the standard Python :class:`dict` class does not support
        hashing.

        Raises:
          TypeError: The underlying dictionary does not support hashing.
        """
        return hash(self._dict)

    def __or__(self, other):
        """
        ``self | other``:
        Return a new view on the merged dictionary and other dictionary.

        Added in Python 3.9.

        The returned :class:`DictView` object is a view on a new dictionary
        object of the type of the left hand operand that contains all the items
        from the underlying dictionary of the left hand operand, updated by the
        items from the other dictionary (or in case of a DictView, its
        underlying dictionary).

        The other object must be a :class:`dict` or :class:`DictView`.

        The dictionary and the other dictionary are not changed.

        Raises:
          TypeError: The other object is not a dict or DictView.
        """
        # pylint: disable=protected-access
        other_dict = other._dict if isinstance(other, DictView) else other
        new_dict = self._dict | other_dict
        return DictView(new_dict)

    def __ror__(self, other):
        """
        ``other | self``:
        Return a new view on the merged dictionary and other dictionary.

        Added in Python 3.9.

        This method is a fallback and is called only if the left operand does
        not support the operation.

        The returned :class:`DictView` object is a view on a new dictionary
        object of the type of the right hand operand that contains all the items
        from the underlying dictionary of the right hand operand, updated by the
        items from the other dictionary (or in case of a DictView, its
        underlying dictionary).

        The other object must be a :class:`dict` or :class:`DictView`.

        The dictionary and the other dictionary are not changed.

        Raises:
          TypeError: The other object is not a dict or DictView.
        """
        return self.__or__(other)


# Remove methods that should be present only under certain conditions, and when
# building the documentation.

if not _DICT_SUPPORTS_ITER_VIEW and not _BUILDING_DOCS:
    del DictView.iterkeys
    del DictView.itervalues
    del DictView.iteritems
    del DictView.viewkeys
    del DictView.viewvalues
    del DictView.viewitems

if not _DICT_SUPPORTS_HAS_KEY and not _BUILDING_DOCS:
    del DictView.has_key

if not _DICT_SUPPORTS_REVERSED and not _BUILDING_DOCS:
    del DictView.__reversed__

if not _DICT_SUPPORTS_OR and not _BUILDING_DOCS:
    del DictView.__or__
    del DictView.__ror__
