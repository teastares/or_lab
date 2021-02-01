"""
This file defines the algorithms.
Last edited by Teast Ares, 20190130.
"""

import itertools
import numpy as np
from util import *
from constant import const

def map_variables(model):
    """
    map the variables by the four types of variable bound.

    paras:
        model: the original model.
    
    returns:
        variable_map_dict: a dictionary contains four sub-dictionaries, each
            contains the replaced parameters.
    """
    variable_map_dict = {
        const.BOUND_TWO_OPEN: defaultdict(lambda: None),
        const.BOUND_LEFT_OPEN: defaultdict(lambda: None),
        const.BOUND_RIGHT_OPEN: defaultdict(lambda: None),
        const.BOUND_TWO_CLOSED: defaultdict(lambda: None)
    }
    
    for variable in model.variable_dict.values():
        # if x is two-side unbounded (-infinite, infinite), then x = x1 - x2
        if variable.get_bound_type() == const.BOUND_TWO_OPEN:
            x1 = Variable(name=variable.name + "_plus",cat=variable.cat)
            x2 = Variable(name=variable.name + "_minus", cat=variable.cat)
            variable_map_dict[const.BOUND_TWO_OPEN][variable.name] = (x1, x2)
        # if x is left-side unbounded (-infinite, upper_bound), then x = -x1 + upper_bound
        elif variable.get_bound_type() == const.BOUND_LEFT_OPEN:
            x1 = Variable(name=variable.name + "_opposite_shift", cat=variable.cat)
            variable_map_dict[const.BOUND_LEFT_OPEN][variable.name] = (x1, variable.upper_bound)
        # if x is right-side unbounded (lower_bound, infinite), then x = x1 + lower_bound
        elif variable.get_bound_type() == const.BOUND_RIGHT_OPEN:
            x1 = Variable(name=variable.name + "_shift", cat=variable.cat)
            variable_map_dict[const.BOUND_RIGHT_OPEN][variable.name] = (x1, variable.lower_bound)
        # if x is two-side closed (lower_bound, upper_bound), then x = x1 + lower_bound, 
        # and there should be a constrain x1 <= variable.upper_bound - variable.lower_bound
        else:
            x1 = Variable(name=variable.name + "_shift", cat=variable.cat)
            variable_map_dict[const.BOUND_TWO_CLOSED][variable.name] = (x1, variable.lower_bound, variable.upper_bound - variable.lower_bound)

    return variable_map_dict

def replace_linear_expression(linear_expression, variable_map_dict):
    """
    use the variable map dictionary to get the replaced linear expression.

    paras:
        linear_expression: the original linear expression
        variable_map_dict: a dictionary contains four sub-dictionaries, each
            contains the replaced parameters.
    
    returns:
        the replaced linear expression and the additional right hand side.
    """
    replaced_linear_expression = LinearExpression()
    arhs = 0

    for variable_name, coefficient in linear_expression.coefficient_dict.items():
        variable = linear_expression.variable_dict[variable_name]
        if variable.get_bound_type() == const.BOUND_TWO_OPEN:
            x1, x2 = variable_map_dict[const.BOUND_TWO_OPEN][variable_name]
            replaced_linear_expression.add_item(x1, coefficient)
            replaced_linear_expression.add_item(x2, -coefficient)
        elif variable.get_bound_type() == const.BOUND_LEFT_OPEN:
            x1, shift = variable_map_dict[const.BOUND_LEFT_OPEN][variable_name]
            replaced_linear_expression.add_item(x1, -coefficient)
            arhs -= (shift * coefficient)
        elif variable.get_bound_type() == const.BOUND_RIGHT_OPEN:
            x1, shift = variable_map_dict[const.BOUND_RIGHT_OPEN][variable_name]
            replaced_linear_expression.add_item(x1, coefficient)
            arhs -= (shift * coefficient)
        else:
            x1, shift, _ = variable_map_dict[const.BOUND_TWO_CLOSED][variable_name]
            replaced_linear_expression.add_item(x1, coefficient)
            arhs -= (shift * coefficient)

    return replaced_linear_expression, arhs

def standardize_model(model):
    """
    get a standard model.
    ----------
    Max cx
    s.t.
    Ax = b
    x >= 0
    ----------

    paras:
        model: the original model.

    returns:
        the standardized model.
    """
    variable_map_dict = map_variables(model)
    standard_model = Model(name="standard " + model.name,sense=const.SENSE_MAX)

    # add the standard variables to the standard model.
    for x1, x2 in variable_map_dict[const.BOUND_TWO_OPEN].values():
        standard_model.add_variable(x1)
        standard_model.add_variable(x2)

    for x1, _ in variable_map_dict[const.BOUND_LEFT_OPEN].values():
        standard_model.add_variable(x1)

    for x1, _ in variable_map_dict[const.BOUND_RIGHT_OPEN].values():
        standard_model.add_variable(x1)

    for x1, _, upper_bound in variable_map_dict[const.BOUND_TWO_CLOSED].values():
        standard_model.add_variable(x1)
        
        upper_bound_constrain = Constrain(name=x1.name + "_upper_bound", sense=const.SENSE_EQ)
        slack_variable = Variable(name="slack_"+x1.name)
        standard_model.add_variable(slack_variable)

        upper_bound_constrain.add_lhs_item(x1, 1)
        upper_bound_constrain.add_lhs_item(slack_variable, 1)
        upper_bound_constrain.set_rhs(upper_bound)
        standard_model.add_constrain(upper_bound_constrain)

    # objective function
    if model.sense == const.SENSE_MAX:
        standard_model.set_objective(replace_linear_expression(model.objective, variable_map_dict)[0])
    else:
        model.objective.oppose()
        standard_model.set_objective(replace_linear_expression(model.objective, variable_map_dict)[0])
        model.objective.oppose()

    # constrains
    for original_constrain in model.constrain_dict.values():
        lhs, arhs = replace_linear_expression(original_constrain.lhs, variable_map_dict)
        constrain = Constrain(name=original_constrain.name + "_replaced", lhs=lhs, sense=const.SENSE_EQ, rhs=original_constrain.rhs + arhs)

        if original_constrain.sense == const.SENSE_LEQ:
            slack_variable = Variable(name="slack_"+original_constrain.name)
            standard_model.add_variable(slack_variable)
            constrain.add_lhs_item(slack_variable, 1)
        elif original_constrain.sense == const.SENSE_GEQ:
            slack_variable = Variable(name="slack_"+original_constrain.name)
            standard_model.add_variable(slack_variable)
            constrain.add_lhs_item(slack_variable, -1)

        standard_model.add_constrain(constrain)

    return standard_model

def matrix_generation(standard_model, variable_index_dict, constrain_index_dict):
    """
    For a standard model, we have following sturcture:
    ------------------
    Max cx
    s.t.
    Ax = b
    ------------------
    This function will generate the Numpy Ndarray format data.


    paras:
        standard_model: a model with standard formation,
        variable_index_dict: the dict for variable's index,
        constrain_index_dict: the dict for constrain's index.

    returns:
        c: the cost function vector,
        A: the left hand side matrix,
        b: the right hand side vector.
    """
    # the column number, or the number of variables.
    n = len(variable_index_dict)
    # the row number, or the number of constrains.
    m = len(constrain_index_dict)

    c = np.zeros(n)
    for variable_name, value in standard_model.objective.coefficient_dict.items():
        index = variable_index_dict[variable_name]
        c[index] = value

    A = np.zeros((m, n))
    b = np.zeros(m)
    for constrain_name, constrain in standard_model.constrain_dict.items():
        row_index = constrain_index_dict[constrain_name]
        for variable_name, value in constrain.lhs.coefficient_dict.items():
            column_index = variable_index_dict[variable_name]
            A[row_index, column_index] = value
        b[row_index] = constrain.rhs

    return c, A, b

def is_solvable(A, b):
    """
    To valid if the linear equations Ax=b is solvable.

    paras:
        A: the left hand side matrix,
        b: the right hand side vector.

    returns:
        True\False
    """
    m = b.shape[0]
    _A = np.concatenate((A, b.reshape(m, 1)), axis=1)
    if np.linalg.matrix_rank(A) == np.linalg.matrix_rank(_A):
        return True
    else:
        return False

def search_init_solution(A, b):
    """
    For a linear equations Ax=b, search a extreme point as a initial solution.

    paras:
        A: the left hand side matrix,
        b: the right hand side vector.    
    """
    m, n = A.shape

    for item in itertools.permutations(range(n)[::-1], m):
        _A = A[:, item]
        basic_solution = np.linalg.solve(_A, b)
        
        for value in basic_solution:
            if value < 0:
                break
        else:
            init_solution = np.zeros(n)
            init_basic_position = np.zeros(n)

            for index, value in enumerate(basic_solution):
                position = item[index]
                init_solution[position] = value
                init_basic_position[position] = 1
            
            return init_solution, init_basic_position

def simplex_method(model, simplex_type):
    """
    Use the simplex method to solve the linear programming.

    
    paras:
        model: the original linear programing model.

    returns:
        TBD
    """
    standard_model = standardize_model(model)

    variable_list = list(standard_model.variable_dict)
    constrain_list = list(standard_model.constrain_dict)

    variable_index_dict = dict()
    constrain_index_dict = dict()

    for index, variable in enumerate(variable_list):
        variable_index_dict[variable] = index
    for index, constrain in enumerate(constrain_list):
        constrain_index_dict[constrain] = index

    c, A, b = matrix_generation(standard_model, variable_index_dict, constrain_index_dict)

    # check if there has a solution
    if is_solvable(A, b) == False:
        standard_model.status == const.STATUS_NO_SOLUTION
        return

    init_solution, init_basic_position = search_init_solution(A, b)
    return init_solution, init_basic_position