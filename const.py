"""
the Constant Variables.
"""

import sys


class _const(object):
    """
    The class of constant number.
    It doesn't follow the Pascal format since its speciality.
    """
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, key, value):
        if self.__dict__.has_key(key):
            raise self.ConstError("Can't change const.{0}".format(key))
        if not key.isupper():
            raise self.ConstCaseError("Const name {0} is not all uppercase".format(key))


sys.modules[__name__] = _const()
import const

# the category of decision variables
cat_binary = "binary"
cat_continuous = "continuous"
cat_integer = "integer"

# sense for a constrain
sense_leq = -1
sense_eq = 0
sense_geq = 1

# sense for a model
sense_max = 0
sense_min = 1

# the lower and upper bound type of a variable
bound_two_open = 0
bound_left_open = 1
bound_right_open = 2
bound_two_closed = 3