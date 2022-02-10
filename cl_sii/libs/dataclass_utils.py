"""
Dataclass utils
===============

Utils for std lib's :class:`dataclasses.Dataclass` classes and instances.

"""
import dataclasses
import enum


@enum.unique
class DcDeepComparison(enum.IntEnum):

    """
    The possible results of a "deep comparison" between 2 dataclass instances.

    .. warning:: The type of both instances must be the same.

    For dataclass instances ``instance_1`` and ``instance_2``, the
    enum member name should be interpreted as:
    ``instance_1`` is ``enum_member_name`` of|to|with ``instance_2``
    e.g. ``instance_1`` is subset of ``instance_2``.

    .. note:: The enum members values are arbitrary.

    """

    EQUAL = 0
    """
    For each dataclass attribute A and B have the same value.
    """

    SUBSET = 11
    """
    A and B are not equal, and A's value for each dataclass attribute whose
    value is not None is equal to B's value for the same attribute.
    """

    SUPERSET = 12
    """
    A and B are not equal, and B's value for each dataclass attribute whose
    value is not None is equal to A's value for the same attribute.
    """

    CONFLICTED = -1
    """
    For one or more dataclass attributes A and B have a different value.
    """


class DcDeepCompareMixin:

    """
    Mixin for dataclass instances "deep comparison".
    """

    def deep_compare_to(self, value: object) -> DcDeepComparison:
        """
        Return result of a "deep comparison" against another dataclass instance.
        """
        # note: 'is_dataclass' returns True if obj is a dataclass or an instance of a dataclass.
        if not dataclasses.is_dataclass(self):
            # TODO: would it be possible to run this check when the **class** is created?
            raise Exception(
                "Programming error. Only dataclasses may subclass 'DcDeepCompareMixin'."
            )
        # note: 'is_dataclass' returns True if obj is a dataclass or an instance of a dataclass.
        if not dataclasses.is_dataclass(value):
            raise TypeError("Value must be a dataclass instance.")

        return _dc_deep_compare_to(self, value)


def dc_deep_compare(value_a: object, value_b: object) -> DcDeepComparison:
    """
    Return result of a "deep comparison" between dataclass instances.
    """
    # note: 'is_dataclass' returns True if obj is a dataclass or an instance of a dataclass.
    if not dataclasses.is_dataclass(value_a) or not dataclasses.is_dataclass(value_b):
        raise TypeError("Values must be dataclass instances.")

    return _dc_deep_compare_to(value_a, value_b)


def _dc_deep_compare_to(value_a: object, value_b: object) -> DcDeepComparison:

    if type(value_a) != type(value_b):
        raise TypeError("Values to be compared must be of the same type.")

    if value_a == value_b:
        return DcDeepComparison.EQUAL

    # Remove dataclass attributes whose value is None.
    self_dict_clean = {k: v for k, v in dataclasses.asdict(value_a).items() if v is not None}
    value_dict_clean = {k: v for k, v in dataclasses.asdict(value_b).items() if v is not None}

    if len(self_dict_clean) < len(value_dict_clean):
        for k, v in self_dict_clean.items():
            if v != value_dict_clean[k]:
                return DcDeepComparison.CONFLICTED
        return DcDeepComparison.SUBSET
    else:
        for k, v in value_dict_clean.items():
            if v != self_dict_clean[k]:
                return DcDeepComparison.CONFLICTED
        return DcDeepComparison.SUPERSET
