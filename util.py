"""
This file defines the utilities.
Last edited by Teast Ares, 20190126.
"""
from collections import defaultdict
from or_lab.const import *
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
        name: the name of the variable
        cat: the category of the variable
        upper_bound: the upper bound of the variable, if None, the upper bound is infinite
        lower_bound: the lower bound of the variable, if None, the lower bound is negative infinite.
    """
    def __init__(self, name=None, cat=cat_continuous, upper_bound=None, lower_bound=0, value=0):
        if name != None:
            self.name = name
        else:
            self.name = random_string()

        self.cat = cat
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
        self.value = value

        if cat == cat_binary:
            self.cat = cat_integer
            self.upper_bound = 1
            self.lower_bound = 0

    def __str__(self):
        return self.name

class LinearExpression:
    """
    the linear (affine) combination of variables.
    
    paras:
        name: the name of the linear expression.
    """
    def __init__(self, name=None):
        self.__body__ = defaultdict(lambda: 0)
        self.variable_dict = defaultdict(lambda: None)

        if name != None:
            self.name = name
        else:
            self.name = random_string()

    def add_item(self, variable, coefficient):
        """
        add an item to the expression.

        paras:
            variable: the decision variable to add
            coefficient: the coefficient of the variable in this adding item.
        """
        self.__body__[variable.name] += coefficient
        self.variable_dict[variable.name] = variable

    def value(self):
        """
        return the value of the linear expression.
        """
        return sum(self.__body__[x] * self.variable_dict[x].value for x in self.__body__)

    def copy(self):
        result = LinearExpression()
        result.__body__ = self.__body__.copy()
        result.variable_dict = self.variable_dict.copy()
        return result

    def __str__(self):
        return " + ".join(str(self.__body__[x]) + x for x in self.__body__)

class Constrain:
    """
    the linear constrain for a mathematical model.

    paras:
        name: the name of the constrain
        lhs: left hand side, a linear expression of variables
        sense: equal, less || equal or great || equal
        rhs: right hand side, a valid number.
    """
    def __init__(self, name=None, lhs=None, sense=sense_leq, rhs = 0):
        if name != None:
            self.name = name
        else:
            self.name = random_string()
        
        if lhs == None:
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

    def is_valid(self):
        """
        check if this constrian is valid or not.
        """
        if self.sense == sense_leq:
            if self.lhs.value() <= self.rhs:
                return True
            else:
                return False

        elif self.sense == sense_eq:
            if self.lhs.value() == self.rhs:
                return True
            else:
                return False

        elif self.sense == sense_geq:
            if self.lhs.value() >= self.rhs:
                return True
            else:
                return False

        else:
            raise ValueError("sense not valid")

    def __str__(self):
        result = str(self.lhs)

        if self.sense == sense_leq:
            result += " <= "

        elif self.sense == sense_eq:
            result += " = "

        elif self.sense == sense_geq:
            result += " > "

        else:
            raise ValueError("sense not valid")

        result += str(self.rhs)
        return result

class Model:
    """
    the mathematical model (or formulation), 
    including the decision variables, objective function and constrains,
    the objective function and the constrains must be LINEAR.

    paras:
        name: the name of the model
        sense: maximize or minimize.
    """
    def __init__(self, name, sense=sense_max):
        self.name = name
        self.sense = sense_max
        self.variable_dict = defaultdict(lambda: None)
        self.objective = LinearExpression()
        self.constrain_dict = defaultdict(lambda: None)

    def copy(self, name):
        """
        copy the model.

        paras:
            name: the name of the target (backup) model.
        """
        result = Model(name=name, sense=self.sense)
        result.variable_dict = self.variable_dict.copy()
        result.objective = self.objective.copy()
        result.constrain_dict = self.constrain_dict.copy()
        return result

    def add_variable(self, variable):
        """
        add a variable to the model.

        paras:
            variable: the decision variable to add
        """
        if self.variable_dict[variable.name] is None:
            self.variable_dict[variable.name] = variable
            if variable.lower_bound != None:
                lower_bound_constrain = Constrain(sense=sense_geq, rhs=variable.lower_bound)
                lower_bound_constrain.add_lhs_item(variable, 1)
                self.add_constrain(lower_bound_constrain)
            if variable.upper_bound != None:
                upper_bound_constrain = Constrain(sense=sense_leq, rhs=variable.upper_bound)
                upper_bound_constrain.add_lhs_item(variable, 1)
                self.add_constrain(upper_bound_constrain)
        else:
            raise ValueError("Two or more variables have the same name, or one variable has been added more than once.")

    def get_variable(self, variable_name):
        """
        get a variable by the name, if no variable in this model, return None.

        paras:
            variable_name: the name of the variable.
        """
        return self.variable_dict[variable_name]
        
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
        """
        return self.constrain_dict[constrain_name]

    def __str__(self):
        result = "Obj:\n"
        result += (str(self.objective) + "\n")

        result += "\n"

        result += "Variables:\n"
        for variable in self.variable_dict.values():
            result += (str(variable.cat) + ": " + str(variable) + "\n")

        result += "\n"

        result += "Constrains:\n"
        for constrain in self.constrain_dict.values():
            result += (str(constrain) + "\n")

        return result