import ast
import re
from ast import AST


def merge_lines(lines, merge_chars=[",", "\\"]):
    merged_lines = []
    new_line = []
    for line in lines:
        strip_line = line.strip()
        if strip_line == "":
            continue

        new_line.append(strip_line)
        if new_line[-1][-1] not in merge_chars:
            if len(new_line) > 0:
                merged_lines.append("\n".join(new_line))
                new_line = []

    if len(new_line) > 0:
        merged_lines.append("\n".join(new_line))
    return merged_lines


def load_code_file(filepath, read_lines=False):
    with open(filepath, mode="r", encoding="utf-8") as fi:
        if read_lines:
            lines = fi.readlines()
            merged_lines = merge_lines(lines)
            return merged_lines
        else:
            return fi.read()
        
def load_code_text_by_lines(text):
    lines = re.split("[\n]+", text)
    merged_lines = merge_lines(lines)
    return merged_lines
    

def check_node_with_variable_list(node, variable_list, verbose=False):
    for variable_name in variable_list:
        if check_node_with_variable_name(node, variable_name):
            return True
    if verbose:
        print("No variables in this node!")
    return False

def rev_extract_all_command(node: ast.AST):
    if "body" not in node._fields:
        return node
    else:
        result = []
        for sub_node in node.body:
            r_sub_node = rev_extract_all_command(sub_node)
            if isinstance(r_sub_node, list):
                result.extend(r_sub_node)
            else:
                result.append(r_sub_node)
        return result
    

def check_node_with_variable_name(node, variable_name):
    """
    Checking this node for whether it involves from "variable_name"
    For example: assume, variable_name = "plt"
        plt.subplots()      - Call a function
        
        abc = plt           - Assign to another variable_name
    """
    def rev_check(node):
        if not isinstance(node, AST) and not isinstance(node, list):
            # not ASR node
            return True if str(node) == variable_name else False
        elif isinstance(node, ast.Call):
            # function
            return True if node.func.value.id == variable_name else False
        elif isinstance(node, list):
            # body of function, if, for, while
            return_bool = False
            for _node in node:
                return_bool = return_bool or rev_check(_node)
            return return_bool
        else:
            # AST node
            return_bool = False
            for name in node._fields:
                if name == "arg":
                    # arg name of a function
                    continue
                try:
                    value = getattr(node, name)
                    return_bool = return_bool or rev_check(value)
                except:
                    continue
            return return_bool
            
    if not isinstance(node, AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    
    return rev_check(node)


def dump(node, annotate_fields=True, include_attributes=False, *, indent=None):
    """
    Return a formatted dump of the tree in node.  This is mainly useful for
    debugging purposes.  If annotate_fields is true (by default),
    the returned string will show the names and the values for fields.
    If annotate_fields is false, the result string will be more compact by
    omitting unambiguous field names.  Attributes such as line
    numbers and column offsets are not dumped by default.  If this is wanted,
    include_attributes can be set to true.  If indent is a non-negative
    integer or string, then the tree will be pretty-printed with that indent
    level. None (the default) selects the single line representation.
    """
    def _format(node, level=0):
        if indent is not None:
            level += 1
            prefix = '\n' + indent * level
            sep = ',\n' + indent * level
        else:
            prefix = ''
            sep = ', '
        if isinstance(node, AST):
            cls = type(node)
            args = []
            allsimple = True
            keywords = annotate_fields
            for name in node._fields:
                try:
                    value = getattr(node, name)
                except AttributeError:
                    keywords = True
                    continue
                if value is None and getattr(cls, name, ...) is None:
                    keywords = True
                    continue
                value, simple = _format(value, level)
                allsimple = allsimple and simple
                if keywords:
                    args.append('%s=%s' % (name, value))
                else:
                    args.append(value)
            
            if allsimple and len(args) <= 3:
                return '%s(%s)' % (node.__class__.__name__, ', '.join(args)), not args
            return '%s(%s%s)' % (node.__class__.__name__, prefix, sep.join(args)), False
        elif isinstance(node, list):
            if not node:
                return '[]', True
            return '[%s%s]' % (prefix, sep.join(_format(x, level)[0] for x in node)), False
        return repr(node), True

    if not isinstance(node, AST):
        raise TypeError('expected AST, got %r' % node.__class__.__name__)
    if indent is not None and not isinstance(indent, str):
        indent = ' ' * indent
    return _format(node)[0]