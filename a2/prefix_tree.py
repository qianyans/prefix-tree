"""CSC148 Assignment 2: Autocompleter classes

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This file contains the design of a public interface (Autocompleter) and two
implementation of this interface, SimplePrefixTree and CompressedPrefixTree.
You'll complete both of these subclasses over the course of this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
from typing import Any, List, Optional, Tuple, Callable


################################################################################
# The Autocompleter ADT
################################################################################
class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """
    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        raise NotImplementedError

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree (Tasks 1-3)
################################################################################
class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    This class follows the implementation described on the assignment handout.
    Note that we've made the attributes public because we will be accessing them
    directly for testing purposes.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.
    weight_type:
        The way that the aggregate weight of non-leaf trees should be
        calculated.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - ("prefixes grow by 1")
      If len(self.subtrees) > 0, and subtree in self.subtrees, and subtree
      is non-empty and not a leaf, then

          subtree.value == self.value + [x], for some element x

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Any
    weight: float
    subtrees: List[SimplePrefixTree]
    weight_type: str
    # === Private Attributes ===
    _cal_weight: Callable
    _leaf_sum: float
    _leaf_count: int

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.value = []
        self.weight = 0.0
        self.subtrees = []
        self.weight_type = weight_type

        if weight_type == 'sum':
            self._cal_weight = self._cal_sum
        else:
            self._cal_weight = self._cal_avg

        self._leaf_sum = 0.0
        self._leaf_count = 0

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __len__(self) -> int:
        """Return the number of values stored in this SimplePrefixTree."""
        return self._leaf_count

    def _cal_sum(self) -> float:
        """Calculate the sum of weight of leaves.
        """
        return self._leaf_sum

    def _cal_avg(self) -> float:
        """Calculate the average of weight of leaves.
        """
        if self._leaf_count != 0:
            return self._leaf_sum / self._leaf_count
        else:
            return 0.0

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this SimplePrefixTree.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        if not self._leaf_has_value(value, prefix):
            self._leaf_count += 1

        if prefix == []:
            new_tree = SimplePrefixTree(self.weight_type)
            new_tree.value = value
            new_tree.weight = float(weight)

            subtree_with_value = self._subtree_with_value(value)
            if subtree_with_value is not None:
                subtree_with_value.weight += weight
            else:
                self.subtrees.append(new_tree)

        else:
            prefix_copy = prefix[:]
            first_prefix = prefix_copy.pop(0)
            subtree_with_value = self._subtree_with_value(self.value
                                                          + [first_prefix])

            if subtree_with_value is not None:
                subtree_with_value.insert(value, weight, prefix_copy)
            else:
                new_tree = SimplePrefixTree(self.weight_type)
                new_tree.value = self.value + [first_prefix]
                self.subtrees.append(new_tree)
                new_tree.insert(value, weight, prefix_copy)

        self._leaf_sum += weight
        self.weight = self._cal_weight()

        self.subtrees.sort(reverse=True)

    def __lt__(self, other: SimplePrefixTree) -> bool:
        """Return a boolean based on the comparison between self and other.
        """
        return self.weight < other.weight

    def _subtree_with_value(self, value: Any) -> Optional[SimplePrefixTree]:
        """Return the subtree in self.subtrees whose value attribute is the
        same with value.
        """
        for subtree in self.subtrees:
            if subtree.value == value:
                return subtree
        return None

    def _leaf_has_value(self, value: Any, prefix: List) -> bool:
        """Return True if the leaves of self has the input value.
        """
        if self.is_empty():
            return False
        else:
            for subtree in self.subtrees:
                if subtree.is_leaf():
                    return subtree.value == value

                length = len(subtree.value)
                if (self.value + prefix)[:length] != subtree.value:
                    continue
                else:
                    prefix_copy = prefix[:]
                    prefix_copy.pop(0)
                    if subtree._leaf_has_value(value, prefix_copy):
                        return True
            return False

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        if self.is_empty():
            return []
        elif self.is_leaf():
            return []
        elif self.value == prefix:
            return self._leaf_value_weight(limit)
        else:
            for subtree in self.subtrees:
                length = len(subtree.value)
                if prefix[:length] != subtree.value:
                    continue
                else:
                    if subtree.autocomplete(prefix, limit):
                        return subtree.autocomplete(prefix, limit)
            return []

    def _leaf_value_weight(self, limit: Optional[int] = None) -> \
            List[Tuple[Any, float]]:
        """Return a list of tuple consisting of each leaf's value and weight.
        """
        if self.is_empty():
            return []
        elif self.is_leaf():
            return [(self.value, self.weight)]
        else:
            leaf_list = []
            for subtree in self.subtrees:
                if limit is None:
                    leaf_list.extend(subtree._leaf_value_weight())
                elif len(leaf_list) < limit:
                    leaf_list.extend(subtree._leaf_value_weight(limit -
                                                                len(leaf_list)))
                else:
                    break
            return sorted(leaf_list, key=lambda x: x[1], reverse=True)

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        if self.is_empty():
            pass
        elif self.is_leaf():
            pass
        elif self._recursive_subtree_with_value(prefix) is None:
            pass
        elif self._subtree_with_value(prefix):
            subtree_with_value = self._subtree_with_value(prefix)
            self._leaf_sum -= subtree_with_value._leaf_sum
            self._leaf_count -= subtree_with_value._leaf_count
            self.weight = self._cal_weight()
            self.subtrees.remove(self._subtree_with_value(prefix))
        else:
            recursive_subtree = self._recursive_subtree_with_value(prefix)
            self._leaf_sum -= recursive_subtree._leaf_sum
            self._leaf_count -= recursive_subtree._leaf_count
            self.weight = self._cal_weight()
            for subtree in self.subtrees:
                length = len(subtree.value)
                if prefix[:length] != subtree.value:
                    continue
                else:
                    subtree.remove(prefix)

        self._remove_empty_subtree(prefix)
        self.subtrees.sort(reverse=True)

    def _recursive_subtree_with_value(self, value: list) -> \
            Optional[SimplePrefixTree]:
        """Return a SimplePrefixTree if the subtrees of self is that value.
        """
        if self.is_empty():
            return None
        elif self.is_leaf():
            return None
        elif self.value == value:
            return self
        else:
            for subtree in self.subtrees:
                length = len(subtree.value)
                if value[:length] != subtree.value:
                    continue
                else:
                    recursive_subtree = subtree.\
                        _recursive_subtree_with_value(value)
                    if recursive_subtree is not None:
                        return recursive_subtree
            return None

    def _remove_empty_subtree(self, prefix: list) -> None:
        """Remove all empty subtree in this tree.
        """
        if self.is_empty():
            pass
        elif self.is_leaf():
            pass
        elif self._zero_weight_subtree() is not None:
            self.subtrees.remove(self._zero_weight_subtree())
        else:
            for subtree in self.subtrees:
                length = len(subtree.value)
                if prefix[:length] != subtree.value:
                    continue
                else:
                    subtree._remove_empty_subtree(prefix)

    def _zero_weight_subtree(self) -> Optional[SimplePrefixTree]:
        """Return the subtree of this tree whose weight is zero.
        If there is none, return None instead.
        """
        for subtree in self.subtrees:
            if subtree.weight == 0:
                return subtree
        return None


################################################################################
# CompressedPrefixTree (Task 6)
################################################################################
class CompressedPrefixTree(Autocompleter):
    """A compressed prefix tree implementation.

    While this class has the same public interface as SimplePrefixTree,
    (including the initializer!) this version follows the implementation
    described on Task 6 of the assignment handout, which reduces the number of
    tree objects used to store values in the tree.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.
    weight_type:
        The way that the aggregate weight of non-leaf trees should be
        calculated.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - **NEW**
      This tree does not contain any compressible internal values.
      (See the assignment handout for a definition of "compressible".)

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Optional[Any]
    weight: float
    subtrees: List[CompressedPrefixTree]
    weight_type: str
    # === Private Attributes ===
    _cal_weight: Callable
    _leaf_sum: float
    _leaf_count: int

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty compressed prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.value = []
        self.weight = 0.0
        self.subtrees = []
        self.weight_type = weight_type

        if weight_type == 'sum':
            self._cal_weight = self._cal_sum
        else:
            self._cal_weight = self._cal_avg

        self._leaf_sum = 0.0
        self._leaf_count = 0

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __len__(self) -> int:
        """Return the number of values stored in this SimplePrefixTree."""
        return self._leaf_count

    def _cal_sum(self) -> float:
        """Calculate the sum of weight of leaves.
        """
        return self._leaf_sum

    def _cal_avg(self) -> float:
        """Calculate the average of weight of leaves.
        """
        if self._leaf_count != 0:
            return self._leaf_sum / self._leaf_count
        else:
            return 0.0

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this CompressedPrefixTree.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        if self.value != []:
            self._add_head()
        self._insert(value, weight, prefix)
        self._remove_head()

        # value: Optional[Any]
        # weight: float
        # subtrees: List[CompressedPrefixTree]
        # weight_type: str
        # # === Private Attributes ===
        # _cal_weight: Callable
        # _leaf_sum: float
        # _leaf_count: int

    def _add_head(self) -> None:
        """Add an empty list head for self."""
        new_tree = CompressedPrefixTree(self.weight_type)
        new_tree.value = self.value
        new_tree._leaf_sum = self._leaf_sum
        new_tree._leaf_count = self._leaf_count
        new_tree.weight = self.weight
        new_tree.subtrees = self.subtrees
        self.value = []
        self.subtrees = []
        self.subtrees.insert(0, new_tree)

    def _insert(self, value: Any, weight: float, prefix: List) -> None:
        """Helper function for self.insert."""
        if not self._leaf_has_value(value, prefix):
            self._leaf_count += 1

        if prefix == self.value:
            subtree_with_value = self._subtree_with_value(value)
            if subtree_with_value is not None:
                subtree_with_value.weight += weight
            else:
                new_tree = CompressedPrefixTree(self.weight_type)
                new_tree.value = value
                new_tree.weight = float(weight)
                self.subtrees.append(new_tree)

        elif not self._common_prefix(prefix):
            new_tree = CompressedPrefixTree(self.weight_type)
            new_tree.value = prefix
            new_tree.weight = float(weight)
            self.subtrees.append(new_tree)
            new_tree._insert(value, weight, prefix)

        elif (len(self._common_prefix(prefix)[0]) <
              len(self._common_prefix(prefix)[1].value)):
            new_tuple = self._common_prefix(prefix)
            common_prefix = new_tuple[0]
            common_prefix_subtree = new_tuple[1]

            self.subtrees.remove(common_prefix_subtree)

            new_tree = CompressedPrefixTree(self.weight_type)
            new_tree.value = common_prefix
            new_tree.subtrees.append(common_prefix_subtree)
            new_tree._leaf_count += common_prefix_subtree._leaf_count
            new_tree._leaf_sum += common_prefix_subtree._leaf_sum

            self.subtrees.append(new_tree)

            new_tree._insert(value, weight, prefix)

        else:
            common_prefix_subtree = self._common_prefix(prefix)[1]
            common_prefix_subtree._insert(value, weight, prefix)

        self._leaf_sum += weight
        self.weight = self._cal_weight()

        self.subtrees.sort(reverse=True)

    def _common_prefix(self, prefix: List) -> \
            Optional[Tuple[list, CompressedPrefixTree]]:
        """Return a tuple consisting of a list of common prefix and the subtree
        that has the common prefix.
        """
        common_prefix = []
        for subtree in self.subtrees:
            if not subtree.is_leaf():
                i = len(self.value)
                while ((i < len(prefix) and i < len(subtree.value))
                       and prefix[i] == subtree.value[i]):
                    common_prefix.append(prefix[i])
                    i += 1

            if common_prefix:
                return self.value + common_prefix, subtree

        return None

    def __lt__(self, other: SimplePrefixTree) -> bool:
        """Return a boolean based on the comparison between self and other.
        """
        return self.weight < other.weight

    def _subtree_with_value(self, value: Any) -> Optional[CompressedPrefixTree]:
        """Return the subtree in self.subtrees whose value attribute is the
        same with value.
        """
        for subtree in self.subtrees:
            if subtree.value == value:
                return subtree
        return None

    def _leaf_has_value(self, value: Any, prefix: List) -> bool:
        """Return True if the leaves of self has the input value.
        """
        if self.is_empty():
            return False
        else:
            for subtree in self.subtrees:
                if subtree.is_leaf():
                    return subtree.value == value

                length = min(len(prefix), len(subtree.value))
                if prefix[:length] != subtree.value[:length]:
                    continue
                else:
                    if subtree._leaf_has_value(value, prefix):
                        return True
            return False

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        if self.value != []:
            self._add_head()
        return_list = self._autocomplete(prefix, limit)
        self._remove_head()
        return return_list

    def _autocomplete(self, prefix: List,
                      limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Helper function for self.autocomplete."""
        if self.is_empty():
            return []
        elif self.is_leaf():
            return []
        elif self._has_common_prefix(prefix):
            return self._leaf_value_weight(limit)
        else:
            for subtree in self.subtrees:
                length = min(len(prefix), len(subtree.value))
                if prefix[:length] != subtree.value[:length]:
                    continue
                else:
                    if subtree._autocomplete(prefix, limit):
                        return subtree._autocomplete(prefix, limit)
            return []

    def _has_common_prefix(self, prefix: list) -> bool:
        """Return whether self.value has common prefix with prefix.
        """
        common_prefix = []
        i = 0
        while i < len(self.value) and i < len(prefix):
            if self.value[i] != prefix[i]:
                break
            else:
                common_prefix.append(prefix[i])
                i += 1

        return len(common_prefix) == len(prefix)

    def _leaf_value_weight(self, limit: Optional[int] = None) -> \
            List[Tuple[Any, float]]:
        """Return a list of tuple consisting of each leaf's value and weight.
        """
        if self.is_empty():
            return []
        elif self.is_leaf():
            return [(self.value, self.weight)]
        else:
            leaf_list = []
            for subtree in self.subtrees:
                if limit is None:
                    leaf_list.extend(subtree._leaf_value_weight())
                elif len(leaf_list) < limit:
                    leaf_list.extend(subtree._leaf_value_weight(limit -
                                                                len(leaf_list)))
                else:
                    break
            return sorted(leaf_list, key=lambda x: x[1], reverse=True)

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        if self.value != []:
            self._add_head()
        self._remove(prefix)
        self._remove_head()

    def _remove(self, prefix: List) -> None:
        """Helper function of remove.
        """
        if self.is_empty():
            pass
        elif self.is_leaf():
            pass

        elif prefix == []:
            self.subtrees = []
            self.weight = 0.0
            self._leaf_count = 0
            self._leaf_sum = 0.0

        elif self._recursive_subtree_with_prefix(prefix) is None:
            pass

        elif (len(prefix) == len(self._common_prefix(prefix)[0]) or
              prefix == self._common_prefix(prefix)[1].value):
            common_subtree = self._common_prefix(prefix)[1]
            self.subtrees.remove(common_subtree)
            self._leaf_sum -= common_subtree._leaf_sum
            self._leaf_count -= common_subtree._leaf_count
            self.weight = self._cal_weight()

        else:
            subtree_with_prefix = self._recursive_subtree_with_prefix(prefix)
            self._leaf_sum -= subtree_with_prefix._leaf_sum
            self._leaf_count -= subtree_with_prefix._leaf_count
            self.weight = self._cal_weight()
            common_subtree = self._common_prefix(prefix)[1]
            common_subtree._remove(prefix)

        self._compress(prefix)

        self._remove_empty_subtree(prefix)
        self.subtrees.sort(reverse=True)

    def _remove_head(self) -> None:
        """Remove the head of the head list which is empty if it only has one
        subtree.
        """
        if self.value == [] and len(self.subtrees) == 1:
            self.value = self.subtrees[0].value
            self.subtrees = self.subtrees[0].subtrees

    def _compress(self, prefix: list) -> None:
        """Compress the tree so that all trees has more than one child or it is
        the parent of a leaf (or both).
        """
        if self.is_empty():
            pass
        elif self.is_leaf():
            pass
        elif self._subtree_compressible(prefix) is not None:
            compressible = self._subtree_compressible(prefix)
            self.subtrees.remove(compressible)
            self.subtrees.append(compressible.subtrees[0])
        else:
            for subtree in self.subtrees:
                length = min(len(prefix), len(subtree.value))
                if prefix[:length] != subtree.value[:length]:
                    continue
                else:
                    subtree._compress(prefix)

    def _subtree_compressible(self, prefix: list) \
            -> Optional[CompressedPrefixTree]:
        """Return the subtree which is compressible.
        If there is none, return None.
        """
        for subtree in self.subtrees:
            length = min(len(prefix), len(subtree.value))
            if prefix[:length] != subtree.value[:length]:
                continue
            else:
                num_subtree = len(subtree.subtrees)
                if num_subtree == 1:
                    if not subtree.subtrees[0].is_leaf():
                        return subtree
        return None

    def _remove_empty_subtree(self, prefix: list) -> None:
        """Remove all empty subtrees in this tree.
        """
        if self.is_empty():
            pass
        elif self.is_leaf():
            pass
        elif self._zero_weight_subtree() is not None:
            self.subtrees.remove(self._zero_weight_subtree())
        else:
            for subtree in self.subtrees:
                length = min(len(prefix), len(subtree.value))
                if prefix[:length] != subtree.value[:length]:
                    continue
                else:
                    subtree._remove_empty_subtree(prefix)

    def _zero_weight_subtree(self) -> Optional[CompressedPrefixTree]:
        """Return the subtree of this tree whose weight is zero.
        If there is none, return None instead.
        """
        for subtree in self.subtrees:
            if subtree.weight == 0.0:
                return subtree
        return None

    def _recursive_subtree_with_prefix(self, prefix: list) -> \
            Optional[CompressedPrefixTree]:
        """Return a SimplePrefixTree if the subtrees of self's value is the same
        with prefix.
        """
        if self.is_empty():
            return None
        elif self.is_leaf():
            return None
        elif not self._common_prefix(prefix):
            return None

        elif (len(self._common_prefix(prefix)[0]) <
              len(self._common_prefix(prefix)[1].value) or
              prefix == self._common_prefix(prefix)[1].value):
            return self._common_prefix(prefix)[1]
        else:
            for subtree in self.subtrees:
                length = min(len(prefix), len(subtree.value))
                if prefix[:length] != subtree.value[:length]:
                    continue
                else:
                    recursive_subtree = subtree.\
                        _recursive_subtree_with_prefix(prefix)
                    if recursive_subtree is not None:
                        return recursive_subtree
            return None


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'max-nested-blocks': 4
    })
