"""
This file defines the utilities.
Last edited by Teast Ares, 20190130.
"""

from collections import defaultdict
from constant import const
import string
import random


def random_string(size=16, chars=string.ascii_lowercase + string.digits):
    """
    generate a random string.

    paras:
        size: the length of the string
        chars: the candidate character set.
    """
    return ''.join(random.choice(chars) for _ in range(size))


class Variable:
    """
    the decision variable for a mathematical model.

    paras:
        name: the name of the variable, this is the identical flag for a variable
        cat: the category of the variable
        upper_bound: the upper bound of the variable, if None, the upper bound is infinite
        lower_bound: the lower bound of the variable, if None, the lower bound is negative infinite.
    """

    def __init__(self, name, cat=const.CAT_CONTINUOUS, upper_bound=None, lower_bound=0, value=0):
        self.name = name

        self.cat = cat
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
        self.value = value

        if cat == const.CAT_BINARY:
            self.cat = const.CAT_INTEGER
            self.upper_bound = 1
            self.lower_bound = 0

        if (self.lower_bound is not None) and (self.upper_bound is not None) and (self.lower_bound > self.upper_bound):
            raise ValueError("Lower bound cannot be greater than the upper bound")

    def get_bound_type(self):
        """
        get the variable's lower and upper bound type.

        returns:
            the bound type.
        """
        if self.lower_bound is None and self.upper_bound is None:
            return const.BOUND_TWO_OPEN
        elif self.lower_bound is not None and self.upper_bound is None:
            return const.BOUND_RIGHT_OPEN
        elif self.lower_bound is None and self.upper_bound is not None:
            return const.BOUND_LEFT_OPEN
        elif self.lower_bound is not None and self.upper_bound is not None:
            return const.BOUND_TWO_CLOSED
        else:
            raise ValueError("Variable has infeasible lower or upper bound.")

    def __str__(self):
        result = self.cat + ": " + self.name + ", "
        if self.lower_bound is None:
            result += "(-infinite, "
        else:
            result += "[{0}, ".format(self.lower_bound)

        if self.upper_bound is None:
            result += "infinite)"
        else:
            result += "{0}]".format(self.upper_bound)

        return result


class LinearExpression:
    """
    the linear (affine) combination of variables.
    
    paras:
        name: the name of the linear expression.
    """

    def __init__(self):
        self.coefficient_dict = defaultdict(float)
        self.variable_dict = dict()

    def add_item(self, variable, coefficient):
        """
        add an item to the expression.

        paras:
            variable: the decision variable to add
            coefficient: the coefficient of the variable in this adding item.
        """
        self.coefficient_dict[variable.name] += coefficient
        self.variable_dict[variable.name] = variable

    def add_items(self, variables, coefficients):
        """
        add some items to the expression

        paras:
            variables: iteration of variables
            coefficients: iteration of coefficients
        """
        for variable, coefficient in zip(variables, coefficients):
            self.add_item(variable, coefficient)

    def get_coefficient(self, variable):
        """
        get a coefficient for a variable.

        paras:
            variable_name: the variable.

        returns:
            coefficient: the coefficient of this variable.
        """
        return self.variable_dict[variable.name]

    def value(self):
        """
        return the value of the linear expression.
        """
        return sum(self.coefficient_dict[x] * self.variable_dict[x].value for x in self.coefficient_dict)

    def oppose(self):
        """
        make the coefficient of each item become the opposite number.
        """
        for k, v in self.coefficient_dict.items():
            self.coefficient_dict[k] = -v

    def copy(self):
        """
        copy the linear expression.

        returns:
            a linear expression: the same variables and cofficients.
        """
        result = LinearExpression()
        result.coefficient_dict = self.coefficient_dict.copy()
        result.variable_dict = self.variable_dict.copy()
        return result

    def __str__(self):
        return " + ".join(str(self.coefficient_dict[x]) + x for x in self.coefficient_dict)


class Constraint:
    """
    the linear constrain for a mathematical model.

    paras:
        name: the name of the constrain, since name is the identical flag for the constraint, we strongly recommend the
            users to fill it
        lhs: left hand side, a linear expression of variables
        sense: equal, less || equal or great || equal
        rhs: right hand side, a valid number.
    """

    def __init__(self, name=None, lhs=None, sense=const.SENSE_LEQ, rhs=0):
        if name is not None:
            self.name = name
        else:
            self.name = random_string() + str(id(self))

        if lhs is None:
            self.lhs = LinearExpression()
        else:
            self.lhs = lhs

        self.sense = sense
        self.rhs = rhs

    def set_lhs(self, lhs):
        """
        set the left hand side.

        paras:
            lhs: the linear expression for the left hand side.
        """
        self.lhs = lhs

    def add_lhs_item(self, variable, coefficient):
        """
        add a item to the left hand side.

        paras:
            variable: the decision variable to add
            coefficient: the coefficient of the variable in this adding item.        
        """
        self.lhs.add_item(variable, coefficient)

    def add_lhs_items(self, variables, coefficients):
        """
        add a sequence of items to the left hand side.

        paras:
            variables: iteration of variables
            coefficients: iteration of coefficients
        """
        self.lhs.add_items(variables, coefficients)

    def set_sense(self, sense):
        """
        set the sense of the constrain.

        paras:
            sense: equal, less || equal or great || equal.     
        """
        self.sense = sense

    def set_rhs(self, rhs):
        """
        set the right hand side.
        
        paras:
            rhs: right hand side, a valid number.
        """
        self.rhs = rhs

    def get_coefficient(self, variable):
        return self.lhs.get_coefficient(variable.name)

    def is_valid(self):
        """
        check if this constriant is valid or not.

        returns:
            bool: if this constrain is valid.
        """
        if self.sense == const.SENSE_LEQ:
            if self.lhs.value() <= self.rhs:
                return True
            else:
                return False

        elif self.sense == const.SENSE_EQ:
            if self.lhs.value() == self.rhs:
                return True
            else:
                return False

        elif self.sense == const.SENSE_GEQ:
            if self.lhs.value() >= self.rhs:
                return True
            else:
                return False

        else:
            raise ValueError("Sense not valid")

    def __str__(self):
        return "{name}: {lhs} {sense} {rhs}".format(name=self.name, lhs=self.lhs, sense=self.sense, rhs=self.rhs)


class Model:
    """
    the mathematical model (or formulation),
    including the decision variables, objective function and constrains,
    the objective function and the constrains must be LINEAR.

    paras:
        name: the name of the model
        sense: maximize or minimize.

    """

    def __init__(self, name, sense=const.SENSE_MIN):
        self.name = name
        self.sense = sense
        self.variable_dict = dict()
        self.objective = LinearExpression()
        self.constraint_dict = dict()

        # the constraint from the lower and upper bound of the variables.
        self.sign_constraint_dict = dict()
        self.status = const.STATUS_UNSOLVED

    def copy(self, name):
        """
        copy the model.

        paras:
            name: the name of the target (backup) model.

        returns:
            model: the model with same variables, objective function and constrains.
        """
        result = Model(name=name, sense=self.sense)
        result.variable_dict = self.variable_dict.copy()
        result.objective = self.objective.copy()
        result.constrain_dict = self.constraint_dict.copy()
        result.sign_constraint_dict = self.sign_constraint_dict.copy()
        result.status = self.status
        return result

    def add_variable(self, variable):
        """
        add a variable to the model.

        paras:
            variable: the decision variable to add.
        """
        if not self.variable_dict.get(variable):
            self.variable_dict[variable.name] = variable
            if variable.lower_bound is not None:
                lb_constraint = Constraint(sense=const.SENSE_GEQ, rhs=variable.lower_bound)
                lb_constraint.add_lhs_item(variable, 1)
                self.add_sign_constrain(lb_constraint)
            if variable.upper_bound is not None:
                ub_constraint = Constraint(sense=const.SENSE_LEQ, rhs=variable.upper_bound)
                ub_constraint.add_lhs_item(variable, 1)
                self.add_sign_constrain(ub_constraint)
        else:
            raise ValueError("Two or more variables have the same name, or one variable has been added more than once.")

    def get_variable(self, variable):
        """
        get a variable by the name, if no variable in this model, return None.

        paras:
            variable: the variable.

        returns:
            variable.
        """
        return self.variable_dict[variable.name]

    def set_objective(self, linear_expression):
        """
        set the objective function using a linear expression.

        paras:
            linear_expression: the linear expression to be the objective function.
        """
        self.objective = linear_expression

    def add_objective_item(self, variable, coefficient):
        """
        add an item to the objective function.

        paras:
            variable: the decision variable to add
            coefficient: the coefficient of the variable in this adding item.        
        """
        self.objective.add_item(variable, coefficient)

    def add_constrain(self, constrain):
        """
        add a constrain to the model.

        paras:
            constrain: the constrain to add        
        """
        self.constrain_dict[constrain.name] = constrain

    def get_constrain(self, constrain_name):
        """
        return a constrain by the contrain name, if no constrain in this model, return None.

        paras:
            constrain_name: the name of the constrain.

        returns:
            constrain.
        """
        return self.constrain_dict[constrain_name]

    def add_sign_constrain(self, constrain):
        """
        add a sign constrain to the model.

        paras:
            constrain: the constrain to add.      
        """
        self.sign_contrain_dict[constrain.name] = constrain

    def __str__(self):
        result = "Obj:\n"
        if self.sense == const.SENSE_MAX:
            result += "Max "
        elif self.sense == const.SENSE_MIN:
            result += "Min "
        else:
            raise ValueError("Invalid model sense: max or min")

        result += (str(self.objective) + "\n")

        result += "\n"

        result += "Variables:\n"
        for variable in self.variable_dict.values():
            result += (str(variable) + "\n")

        result += "\n"

        result += "Constrains:\n"
        for constrain in self.constrain_dict.values():
            result += (str(constrain) + "\n")

        return result
