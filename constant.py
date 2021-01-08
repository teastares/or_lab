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
const.CAT_BINARY = "Binary"
const.CAT_CONTINUOUS = "Continuous"
const.CAT_INTEGER = "Integer"

# sense for a constrain
const.SENSE_LEQ = -1
const.SENSE_EQ = 0
const.SENSE_GEQ = 1

# sense for a model
const.SENSE_MAX = 0
const.SENSE_MIN = 1

# the lower and upper bound type of a variable
const.BOUND_TWO_OPEN = 0
const.BOUND_LEFT_OPEN = 1
const.BOUND_RIGHT_OPEN = 2
const.BOUND_TWO_CLOSED = 3

# the status of the model
const.STATUS_UNSOLVED = 0
const.STATUS_OPTIMAL = 1
const.STATUS_NO_SOLUTION = 2
const.STATUS_UNBOUNDED = 3