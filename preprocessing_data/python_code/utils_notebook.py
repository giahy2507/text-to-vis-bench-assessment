import ast
from utils_ast import rev_extract_all_command
import re
from main_matplotlib_python import post_process_parsed_nodes, handle_node


def filter_by_lines(code):
    lines = re.split("\n+", code)
    result = []
    for line in lines:
        if re.search("^[#!%]", line):
            continue
        result.append(line)
    return "\n".join(result)


def parse_ast_for_notebook_cells(matplotlib_schema_dict, 
                                 code_cells,
                                 target_lib="matplotlib",
                                 verbose=False):
    content = []
    variable_list = []

    # parse AST tree
    for code in code_cells:
        try:
            # AST parsing
            tree = ast.parse(source=code)
            # Extract all command
            nodes = rev_extract_all_command(tree)
            for node in nodes:
                # Parse function command and convert to universal format
                parsed_nodes, variable_list = handle_node(node, 
                            target_lib=target_lib, 
                            variable_list=variable_list, 
                            verbose=verbose)
                
                if len(parsed_nodes) > 0:
                    content += post_process_parsed_nodes(matplotlib_schema_dict, parsed_nodes, verbose=verbose)
        except KeyboardInterrupt:
            break
        except:
            continue
    return content



    

                      


    
