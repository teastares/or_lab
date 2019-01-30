"""
This file defines the algorithms.
Last edited by Teast Ares, 20190130.
"""

from or_lab.util import *
from or_lab.const import *

def map_variables(model):
    """
    map the variables by the four types of variable bound.

    paras:
        model: the original model.
    
    returns:
        variable_map_dict: a dictionary contains four sub-dictionaries, each
            contains the inversion parameters.
    """
    variable_map_dict = {
        bound_two_open: defaultdict(lambda: None),
        bound_left_open: defaultdict(lambda: None),
        bound_right_open: defaultdict(lambda: None),
        bound_two_closed: defaultdict(lambda: None)
    }
    
    for variable in model.variable_dict.values():
        # if x is two-side unbounded (-infinite, infinite), then x = x1 - x2
        if variable.get_bound_type() == bound_two_open:
            x1 = Variable(name=variable.name + "_plus",cat=variable.cat)
            x2 = Variable(name=variable.name + "_minus", cat=variable.cat)
            variable_map_dict[bound_two_open][variable.name] = (x1, x2)
        # if x is left-side unbounded (-infinite, upper_bound), then x = -x1 + upper_bound
        elif variable.get_bound_type() == bound_left_open:
            x1 = Variable(name=variable.name + "_opposite_shift", cat=variable.cat)
            variable_map_dict[bound_left_open][variable.name] = (x1, variable.upper_bound)
        # if x is right-side unbounded (lower_bound, infinite), then x = x1 + lower_bound
        elif variable.get_bound_type() == bound_right_open:
            x1 = Variable(name=variable.name + "_shift", cat=variable.cat)
            variable_map_dict[bound_right_open][variable.name] = (x1, variable.lower_bound)
        # if x is two-side closed (lower_bound, upper_bound), then x = x1 + lower_bound, 
        # and there should be a constrain x1 <= variable.upper_bound - variable.lower_bound
        elif variable.get_bound_type() == bound_two_closed:
            x1 = Variable(name=variable.name + "_shift", cat=variable.cat)
            variable_map_dict[bound_two_closed][variable.name] = (x1, variable.lower_bound, variable.upper_bound - variable.lower_bound)

    return variable_map_dict

def standardize_model(model):
    """
    get a standard model.
    """
    variable_map_dict = map_variables(model)
    standard_model = Model(name="standard " + model.name,sense=sense_max)


    # add the standard variables to the standard model.
    for x1, x2 in variable_map_dict[bound_two_open].values():
        standard_model.add_variable(x1)
        standard_model.add_variable(x2)

    for x1, _ in variable_map_dict[bound_left_open].values():
        standard_model.add_variable(x1)

    for x1, _ in variable_map_dict[bound_right_open].values():
        standard_model.add_variable(x1)

    for x1, _, upper_bound in variable_map_dict[bound_two_closed].values():
        standard_model.add_variable(x1)
        
        upper_bound_constrain = Constrain(sense=sense_leq)
        upper_bound_constrain.add_lhs_item(x1, 1)
        upper_bound_constrain.set_rhs(upper_bound)
        standard_model.add_constrain(upper_bound_constrain)

    return standard_model