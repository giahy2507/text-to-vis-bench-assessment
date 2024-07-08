import ast
import re
import glob
import copy
from collections import OrderedDict
from tqdm import tqdm
from pprint import pprint
from utils_ast import check_node_with_variable_list, dump as ast_dump


def handle_node_import(node,
                  target_lib="matplotlib", 
                  verbose=False):
    """
    Handle import statement
    if 'target_lib' in line, get the lib name or alias
    For example:
        import matplotlib.pyplot as plt --> ["plt"]
        import matplotlib --> ["matplotlib"]
        from os import path, makedirs --> ["path", "makedirs"]
    
    Return:
        list of all lib_name or their alias
    """
    if verbose:
        print(ast_dump(node))
        print()
    variable_list = []
    for name in node.names:
        if target_lib in name.name or target_lib in str(name.asname):
            variable_name = name.asname if name.asname != None else name.name
            if variable_name == "_": 
                continue
            variable_list.append(variable_name)
    if verbose:
        print("New variable_list: ", variable_list)
        print("-"*50)
    return variable_list

def rev_get_variable_func_call(node: ast.AST):
    if not isinstance(node, ast.AST):
        return None
    elif isinstance(node, ast.Name):
        return node.id
    else:
        if len(node._fields) > 0:
            next_node = getattr(node, node._fields[0])
            return rev_get_variable_func_call(next_node)
        else:
            return None

def check_parsable_line(line):
    try:
        return ast.parse(line.strip()).body[0]
    except:
        return None

def handle_node_call_args(args):
    args_value = []
    for arg in args:
        if isinstance(arg, ast.Constant):
            args_value.append(arg.value)
        else:
            args_value.append(str(type(arg)))
    return args_value

def handle_node_call_kargs(kargs):
    kargs_dict = {}
    for karg in kargs:
        karg_name = karg.arg
        if isinstance(karg.value, ast.Constant):
            karg_value = karg.value.value
        else:
            karg_value = str(type(karg.value))
        kargs_dict[karg_name] = karg_value
    return kargs_dict

def handle_node_Call(node):
    assert isinstance(node, ast.Call)
    args_value = handle_node_call_args(node.args)
    kargs_dict = handle_node_call_kargs(node.keywords)
    if isinstance(node.func, ast.Name):
        func_name = node.func.id
        variable_name_call = None
    elif isinstance(node.func, ast.Attribute):
        func_name = node.func.attr
        variable_name_call = rev_get_variable_func_call(node.func.value)
    else:
        # print("handle_node_Call - Unknown function type!")
        # print(ast_dump(node, indent=4))
        return {}
        # raise ValueError("handle_node_Call - Unknown function type!")

    return OrderedDict({
        "var_call": variable_name_call,
        "func_name": func_name,
        "args": args_value,
        "kargs": kargs_dict
    })

def handle_node_Expr(node, verbose=False):
    """
    When an expression, such as a function call.
    """
    if verbose:
        print(ast_dump(node))
        print()
        
    assert isinstance(node, ast.Expr)
    result = {}
    if isinstance(node.value, ast.Call):
        result = handle_node_Call(node.value)
    else:
        if verbose:
            print("Not a call Expr")
    if verbose:
        pprint(result)
        print("-"*50)
    return result

def rev_extract_target_names(node):
    if isinstance(node, list):
        result = []
        for item in node:
            result += rev_extract_target_names(item)
        return result
    elif not isinstance(node, ast.AST):
        return []
    else:
        if isinstance(node, ast.Name):
            if node.id != "_":
                return [node.id]
            else:
                return []
        else:
            result = []
            for field in node._fields:
                next_node = getattr(node, field)
                result += rev_extract_target_names(next_node)
            return result
                
def handle_node_Assign(node, variable_list:list, verbose=False):
    # Check whether this node involves in variable list.
    # Exmaple --> see "check_node_with_variable_list"
    # if not check_node_with_variable_list(node, variable_list):
    #     return None
    
    if verbose:
        print(ast_dump(node))
        print()

    
    assert isinstance(node, ast.Assign) or isinstance(node, ast.AnnAssign)
    #  ----- Parsing targets -----
    node_targets = node.targets if "targets" in node._fields else [node.target]
    targets_str = rev_extract_target_names(node_targets)

    # ----- Parsing values -----
    # gathering values
    values_str = []
    if isinstance(node.value, ast.Name):
        # Assign variable
        values_str.append({"var_call": node.value.id})
    elif isinstance(node.value, ast.Call):
        # Call a function
        values_str.append(handle_node_Call(node.value))
    elif isinstance(node.value, ast.Tuple):
        # Assign a tuple
        for elt in node.value.elts:
            if isinstance(elt, ast.Name):
                values_str.append({"var_call": elt.id})
            elif isinstance(elt, ast.Call):
                values_str.append(handle_node_Call(elt))

    result = []
    # Updating variable list
    new_variable_list = copy.deepcopy(variable_list)
    for value_str in values_str:
        # prepare result dict
        value_str["target"] = targets_str
        result.append(value_str)

        # update new_variable_list
        var_call = value_str.get("var_call", None)
        if var_call and var_call in new_variable_list:
            new_variable_list.extend(targets_str)
    
    if verbose:
        pprint(result)
        print("-"*50 + "\n")

    return result, new_variable_list

def handle_node(node, target_lib, variable_list, verbose=False):

    if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
        variable_list += handle_node_import(node, target_lib=target_lib, verbose=verbose)
        return [], list(set(variable_list))
    else:
        if not check_node_with_variable_list(node, variable_list, verbose=verbose):
            return [], variable_list

        result = []
        if isinstance(node, ast.Expr):
            result_expr = handle_node_Expr(node, verbose=verbose)
            result.append(result_expr)
        elif isinstance(node, ast.Assign) or isinstance(node, ast.AnnAssign):
            result_asign, new_variable_list = handle_node_Assign(node, variable_list, verbose=verbose)
            variable_list += new_variable_list
            result.extend(result_asign)
        for item in result:
            if item:
                item["target_lib"] = target_lib
        return result, list(set(variable_list))
