import ast
import os
import glob
from collections import OrderedDict
import json
from utils_ast import load_code_file

# -----------
"""
Extract ClassDef and FunctionDef in library for mapping args
"""

def extract_arg_node_value(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str) or \
            isinstance(node.value, int) or \
            isinstance(node.value, float) or \
            isinstance(node.value, bool):
            return node.value
        else:
            return str(node.value)
    elif isinstance(node, ast.Tuple) or isinstance(node, ast.List):
        return [extract_arg_node_value(item) for item in node.elts]
    else:
        return str(type(node))

def extract_node_FunctionDef(node):
    """
    def f(a: 'annotation', b=1, c=2, *d, e, f=3, **g) -> 'return annotation':
    FunctionDef(
            name='f',
            args=arguments(
                posonlyargs=[],
                args=[
                    arg(
                        arg='a',
                        annotation=Constant(value='annotation')),
                    arg(arg='b'),
                    arg(arg='c')],
                vararg=arg(arg='d'),
                kwonlyargs=[
                    arg(arg='e'),
                    arg(arg='f')],
                kw_defaults=[
                    None,
                    Constant(value=3)],
                kwarg=arg(arg='g'),
                defaults=[
                    Constant(value=1),
                    Constant(value=2)]),
    """
    func_name = node.name
    if func_name == 'suptitle':
        print()
    # extract args and their default values
    args = [arg.arg for arg in node.args.args]
    if len(args) > 0:
        args_default = [None]*len(args)
        default_values = [extract_arg_node_value(item) for item in node.args.defaults]
        if len(default_values) > 0:
            args_default[-len(default_values):] = default_values
        assert len(args) == len(args_default)
        args = list(zip(args, args_default))

    # extract kargs and their default values
    kargs = [arg.arg for arg in node.args.kwonlyargs]
    kargs_values = [extract_arg_node_value(item) for item in node.args.kw_defaults]
    assert len(kargs) == len(kargs_values)
    kargs = list(zip(kargs, kargs_values))

    # additional args and kargs
    add_args = node.args.vararg.arg if node.args.vararg else None
    add_kargs = node.args.kwarg.arg if node.args.kwarg else None

    return func_name, args, add_args, kargs, add_kargs

def extract_node_Def(node):
    if not isinstance(node, ast.AST) and not isinstance(node, list):
        return []
    elif isinstance(node, list):
        # for body
        result = []
        for subnode in node:
            result+= extract_node_Def(subnode)
        return result
    elif isinstance(node, ast.ClassDef):
        cls_name = node.name
        result = []
        for subnode in node.body:
            if isinstance(subnode, ast.FunctionDef):
                func_name, args, add_args, kargs, add_kargs = extract_node_FunctionDef(subnode)
                result.append((cls_name, func_name, args, add_args, kargs, add_kargs))
        return result
    elif isinstance(node, ast.FunctionDef):
        func_name, args, add_args, kargs, add_kargs = extract_node_FunctionDef(node)
        return [(None, func_name, args, add_args, kargs, add_kargs)]
    else:
        result = []
        for field in node._fields:
            subnode = getattr(node, field)
            result+=extract_node_Def(subnode)
        return result

def extract_library_def_functions(glob_path, output_path):
    fo = open(output_path, mode="w", encoding="utf-8")
    
    pypaths = glob.glob(glob_path, recursive=True)
    print(len(pypaths))
    for pypath in pypaths:
        if "/backends/" in pypath: continue
        if "/tests/" in pypath: continue
        if "/testing/" in pypath: continue
        # print(pypath.replace("/Users/hy/Documents/usyd/projects/matplotlib/matplotlib-3.8.1/lib/matplotlib", ""))

        source = load_code_file(pypath)
        tree = ast.parse(source=source)
        def_funcs = extract_node_Def(tree)
        print(pypath)
        pypath_out = pypath + ".jsonl"
        pypath_out_fo = open(pypath_out, mode="w", encoding="utf-8")
        for def_func in def_funcs:
            # print(def_func)
            class_name, func_name, args, add_args, kargs, add_kargs = def_func
            json_s = json.dumps({
                "class_name": class_name,
                "func_name": func_name,
                "args": args,
                "kargs": kargs,
                "add_args": add_args,
                "add_kargs": add_kargs
            })
            fo.write(json_s + "\n")
            pypath_out_fo.write(json_s + "\n\n")
        pypath_out_fo.close()
    fo.close()


def load_matplotlib_schema(matplotlib_schema_dir, 
                           version_list=["3.8.1", "2.2.5" ,"1.5.3"]):
    matplotlib_schema_dict = OrderedDict()
    """
    matplotlib_schema_dict["version"]["function_name"] = [(class_name, function_name, args, kargs)]
    """
    for version in version_list:
        matplotlib_schema_path = f"{matplotlib_schema_dir}/matplotlib-{version}.jsonl"
        assert os.path.exists(matplotlib_schema_path), f"{matplotlib_schema_path} does not exist"
        if version not in matplotlib_schema_dict:
            matplotlib_schema_dict[version] = dict()
            
        with open(matplotlib_schema_path, mode="r", encoding="utf-8") as fi:
            for i, line in enumerate(fi):
                line = line.strip()
                if line:
                    line_dict = json.loads(line)

                    if line_dict["func_name"] == "__init__":
                        line_dict["func_name"] = line_dict["class_name"]

                    if line_dict["func_name"] not in matplotlib_schema_dict[version]:
                        matplotlib_schema_dict[version][line_dict["func_name"]] = []
                    
                    if len(line_dict["args"]) > 0:
                        if line_dict["args"][0][0] == "self" or line_dict["args"][0][0] == "cls":
                            line_dict["args"] = line_dict["args"][1:]
                    
                    line_dict["args"] = OrderedDict(line_dict["args"])
                    line_dict["kargs"] = OrderedDict(line_dict["kargs"])

                    matplotlib_schema_dict[version][line_dict["func_name"]].append(line_dict)
    return matplotlib_schema_dict


if __name__ == "__main__":
    # Extract library function definitions
    # This will help to retrieve keyword arguments
    # For example, the user call plt.title("TITLE") --> we can retrieve plt.title(label="TITLE")

    # Input: matplotlib_schema/matplotlib-1.5.3 <--- matplotlib source code, downloaded from release page 
    # https://github.com/matplotlib/matplotlib/releases/tag/v1.5.3
    extract_library_def_functions(glob_path=f"matplotlib_schema/matplotlib-1.5.3/lib/matplotlib/**/*.py",
                                  output_path=f"matplotlib_schema/matplotlib-1.5.3.jsonl")
    extract_library_def_functions(glob_path=f"matplotlib_schema/matplotlib-2.2.5/lib/matplotlib/**/*.py",
                                  output_path=f"matplotlib_schema/matplotlib-2.2.5.jsonl")
    extract_library_def_functions(glob_path=f"matplotlib_schema/matplotlib-3.8.1/lib/matplotlib/**/*.py",
                                  output_path=f"matplotlib_schema/matplotlib-3.8.1.jsonl")
