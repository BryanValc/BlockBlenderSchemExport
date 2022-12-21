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
An immutable list view.
"""

from __future__ import print_function, absolute_import

try:
    from collections.abc import Sequence
except ImportError:
    # Python 2
    from collections import Sequence  # pylint: disable=deprecated-class

__all__ = ['ListView']


class ListView(Sequence):
    # pylint: disable=line-too-long
    """
    An immutable list view.

    Derived from :class:`~py3:collections.abc.Sequence`.

    This class provides an immutable view on a possibly mutable sequence
    object. The sequence object must be an instance of
    :class:`~py3:collections.abc.Sequence`, e.g. :class:`list`, :class:`tuple`,
    :class:`range`, or a user-defined class.

    This can be used for example when a class maintains a list that should
    be made available to users of the class without allowing them to modify the
    list.

    In the description of this class, the term 'view' always refers to the
    :class:`ListView` object, and the term 'list' or 'underlying list' refers
    to the sequence object the view is based on.

    The :class:`ListView` class supports the complete behavior of Python class
    :class:`list`, except for any methods that would modify the list.
    Note that the non-modifying methods of class :class:`list` are a superset of
    the methods defined for the abstract class
    :class:`~py3:collections.abc.Sequence` (the methods are listed in the table
    at the top of the linked page).

    The view is "live": Since the view class delegates all operations to the
    underlying list, any modification of the underlying list object
    will be visible in the view object.

    Note that only the view object is immutable, not its items. So if the values
    in the underlying list are mutable objects, they can be modified through the
    view.

    Note that in Python, augmented assignment (e.g. ``x += y``) is not
    guaranteed to modify the left hand object in place, but can result in the
    left hand name being bound to a new object (like in ``x = x + y``).
    For details, see
    `object.__iadd__() <https://docs.python.org/3/reference/datamodel.html#object.__iadd__>`_.

    For the ListView class, augmented assignment is supported and results in
    binding the left hand name to a new ListView object.
    """  # noqa: E501
    # pylint: enable=line-too-long

    __slots__ = ['_list']

    def __init__(self, a_list):
        """
        Parameters:

          a_list (:class:`~py3:collections.abc.Sequence`):
            The underlying list.
            If this object is a ListView, its underlying list is used.
        """
        if not isinstance(a_list, Sequence):
            raise TypeError(
                "The a_list parameter must be a Sequence, but is: {}".
                format(type(a_list)))
        if isinstance(a_list, ListView):
            a_list = a_list._list
        self._list = a_list

    @property
    def list(self):
        """
        The underlying list.

        Access to the underlying list is provided for purposes such as
        conversion to JSON or other cases where the view classes do not work.
        This access should not be used to modify the underlying list.
        """
        return self._list

    def __repr__(self):
        """
        ``repr(self)``:
        Return a string representation of the view suitable for debugging.

        The underlying list is represented using its ``repr()``
        representation.
        """
        return "{0.__class__.__name__}({1!r})".format(self, self._list)

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

    def __getitem__(self, index):
        """
        ``self[index]``:
         Return the list value at the index position.

        Raises:
          IndexError: Index out of range.
        """
        return self._list[index]

    def __len__(self):
        """
        ``len(self)``:
        Return the number of items in the list.

        The return value is the number of items in the underlying list.
        """
        return len(self._list)

    def __contains__(self, value):
        """
        ``value in self``:
        Return a boolean indicating whether the list contains a value.

        The return value indicates whether the underlying list contains an
        item that is equal to the value.
        """
        return value in self._list

    def __iter__(self):
        """
        Return an iterator through the list items.
        """
        return iter(self._list)

    def __add__(self, other):
        """
        ``self + other``:
        Return a new view on the concatenation of the list and the other list.

        The returned :class:`ListView` object is a view on a new list object of
        the type of the left hand operand that contains the items that are in
        the underlying list of the left hand operand, concatenated with the
        items in the other list (or in case of a ListView, its underlying list).

        The other object must be an :term:`py3:iterable` or :class:`ListView`.

        The list and the other list are not changed.

        Raises:
          TypeError: The other object is not an iterable.
        """
        # pylint: disable=protected-access
        other_list = other._list if isinstance(other, ListView) else other
        new_list = self._list + other_list
        return ListView(new_list)

    def __mul__(self, number):
        """
        ``self * number``:
        Return a new view on the multiplication of the list with a number.

        The returned :class:`ListView` object is a view on a new list object of
        the type of the left hand operand that contains the items that are in
        the underlying list of the left hand operand as many times as specified
        by the right hand operand.

        A number <= 0 causes the returned list to be empty.

        The left hand operand is not changed.
        """
        new_list = self._list * number
        return ListView(new_list)

    def __rmul__(self, number):
        """
        ``number * self``:
        Return a new view on the multiplication of the list with a number.

        This method is a fallback and is called only if the left operand does
        not support the operation.

        The returned :class:`ListView` object is a view on a new list object of
        the type of the right hand operand that contains the items that are in
        the underlying list of the right hand operand as many times as specified
        by the left hand operand.

        A number <= 0 causes the returned list to be empty.

        The right hand operand is not changed.
        """
        return self * number  # Delegates to __mul__()

    def __reversed__(self):
        """
        ``reversed(self) ...``:
        Return an iterator through the list in reversed iteration order.

        The returned iterator yields the items in the underlying list in the
        reversed iteration order.
        """
        return reversed(self._list)

    def __eq__(self, other):
        """
        ``self == other``:
        Return a boolean indicating whether the list is equal to the other list.

        The return value indicates whether the items in the underlying list are
        equal to the items in the other list (or in case of a ListView, its
        underlying list).

        The other object must be a :class:`list` or :class:`ListView`.

        Raises:
          TypeError: The other object is not a list or ListView.
        """
        # pylint: disable=protected-access
        other_list = other._list if isinstance(other, ListView) else other
        return self._list == other_list

    def __ne__(self, other):
        """
        ``self != other``:
        Return a boolean indicating whether the list is not equal to the other
        list.

        The return value indicates whether the items in the underlying list are
        not equal to the items in the other list (or in case of a ListView, its
        underlying list).

        The other object must be a :class:`list` or :class:`ListView`.

        Raises:
          TypeError: The other object is not a list or ListView.
        """
        # pylint: disable=protected-access
        other_list = other._list if isinstance(other, ListView) else other
        return self._list != other_list

    def __gt__(self, other):
        # pylint: disable=line-too-long
        """
        ``self > other``:
        Return a boolean indicating whether the list is greater than the other
        list.

        The return value indicates whether the underlying list is greater than
        the other list (or in case of a ListView, its underlying list), based on
        the lexicographical ordering Python defines for sequence types
        (see https://docs.python.org/3/tutorial/datastructures.html#comparing-sequences-and-other-types)

        The other object must be a :class:`list` or :class:`ListView`.

        Raises:
          TypeError: The other object is not a list or ListView.
        """  # noqa: E501
        # pylint: enable=line-too-long
        # pylint: disable=protected-access
        other_list = other._list if isinstance(other, ListView) else other
        return self._list > other_list

    def __lt__(self, other):
        # pylint: disable=line-too-long
        """
        ``self < other``:
        Return a boolean indicating whether the list is less than the other
        list.

        The return value indicates whether the underlying list is less than
        the other list (or in case of a ListView, its underlying list), based on
        the lexicographical ordering Python defines for sequence types
        (see https://docs.python.org/3/tutorial/datastructures.html#comparing-sequences-and-other-types)

        The other object must be a :class:`list` or :class:`ListView`.

        Raises:
          TypeError: The other object is not a list or ListView.
        """  # noqa: E501
        # pylint: enable=line-too-long
        # pylint: disable=protected-access
        other_list = other._list if isinstance(other, ListView) else other
        return self._list < other_list

    def __ge__(self, other):
        # pylint: disable=line-too-long
        """
        ``self < other``:
        Return a boolean indicating whether the list is greater than or equal to
        the other list.

        The return value indicates whether the underlying list is greater than
        or equal to the other list (or in case of a ListView, its underlying
        list), based on the lexicographical ordering Python defines for sequence
        types
        (see https://docs.python.org/3/tutorial/datastructures.html#comparing-sequences-and-other-types)

        The other object must be a :class:`list` or :class:`ListView`.

        Raises:
          TypeError: The other object is not a list or ListView.
        """  # noqa: E501
        # pylint: enable=line-too-long
        # pylint: disable=protected-access
        other_list = other._list if isinstance(other, ListView) else other
        return self._list >= other_list

    def __le__(self, other):
        # pylint: disable=line-too-long
        """
        ``self < other``:
        Return a boolean indicating whether the list is less than or equal to
        the other list.

        The return value indicates whether the underlying list is less than or
        equal to the other list (or in case of a ListView, its underlying list),
        based on the lexicographical ordering Python defines for sequence types
        (see https://docs.python.org/3/tutorial/datastructures.html#comparing-sequences-and-other-types)

        The other object must be a :class:`list` or :class:`ListView`.

        Raises:
          TypeError: The other object is not a list or ListView.
        """  # noqa: E501
        # pylint: enable=line-too-long
        # pylint: disable=protected-access
        other_list = other._list if isinstance(other, ListView) else other
        return self._list <= other_list

    def count(self, value):
        """
        Return the number of times the specified value occurs in the list.
        """
        return self._list.count(value)

    def copy(self):
        """
        Return a new view on a shallow copy of the list.

        The returned :class:`ListView` object is a new view object on a list
        object of the type of the underlying list.

        If the list type is immutable, the returned list object may be the
        underlying list object. If the list type is mutable, the returned list
        is a new list object that is a shallow copy of the underlying list
        object.
        """
        org_class = self._list.__class__
        new_list = org_class(self._list)  # May be same object if immutable
        return ListView(new_list)

    def index(self, value, start=0, stop=9223372036854775807):
        """
        Return the index of the first item in the list with the specified value.

        The search is limited to the index range defined by the specified
        ``start`` and ``stop`` parameters, whereby ``stop`` is the index
        of the first item after the search range.

        Raises:
          ValueError: No such item is found.
        """
        return self._list.index(value, start, stop)

    def __hash__(self):
        """
        ``hash(self)``:
        Return a hash value for the list.

        Whether hashing is supported depends on the underlying list. For
        example, the standard Python :class:`list` class does not support
        hashing, but the standard Python :class:`tuple` class does.

        Raises:
          TypeError: The underlying list does not support hashing.
        """
        return hash(self._list)
