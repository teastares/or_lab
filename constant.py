"""
the Constant Variables.
"""

import sys


class ConstantSet(object):
    """
    The class of constant number.
    It doesn't follow the Pascal format since its speciality.
    """
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, key, value):
        if key in self.__dict__:
            raise self.ConstError("Can't change const.{0}".format(key))
        if not key.isupper():
            raise self.ConstCaseError("Const name {0} is not all uppercase".format(key))
        self.__dict__[key] = value

const = ConstantSet()

# the category of decision variables
const.CAT_BINARY = "binary"
const.CAT_CONTINUOUS = "continuous"
const.CAT_INTEGER = "integer"

# sense for a constrain
const.SENSE_LEQ = -1
const.SENSE_EQ = 0
const.SENSE_GEQ = 1

# sense for a model
const.SENSE_MAX = 0
const.SENSE_MIN = 1

# the lower and upper bound type of a variable
bound_two_open = 0
bound_left_open = 1
bound_right_open = 2
bound_two_closed = 3

const.BOUND_TWO_OPEN = 0
const.BOUND_LEFT_OPEN = 1
const.BOUND_RIGHT_OPEN = 2
const.BOUND_TWO_CLOSED = 3