"""
the Constant Variables.
"""


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
const.SENSE_LEQ = "<="
const.SENSE_EQ = "="
const.SENSE_GEQ = ">="

# sense for a model
const.SENSE_MAX = "Max"
const.SENSE_MIN = "Min"

# the lower and upper bound type of a variable
const.BOUND_TWO_OPEN = 0
const.BOUND_LEFT_OPEN = 1
const.BOUND_RIGHT_OPEN = 2
const.BOUND_TWO_CLOSED = 3

# the status of the model
const.STATUS_UNSOLVED = "Unsolved"
const.STATUS_OPTIMAL = "Optimal"
const.STATUS_NO_SOLUTION = "No feasible solution"
const.STATUS_UNBOUNDED = "Unbounded"
