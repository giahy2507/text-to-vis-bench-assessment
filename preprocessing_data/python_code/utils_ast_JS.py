import re
import glob
import json


def json_to_namespaces(json_data: dict):
    if isinstance(json_data, dict):
        result = []
        for key, value in json_data.items():
            if isinstance(value, list) or isinstance(value, dict):
                value_result = json_to_namespaces(value)
                for item in value_result:
                    result.append(f"{key}.{item}")
            else:
                result.append(key)
        return result
    elif isinstance(json_data, list):
        result = []
        for item in json_data:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, list) or isinstance(value, dict):
                        value_result = json_to_namespaces(value)
                        for item in value_result:
                            result.append(f"{key}.{item}")
                    else:
                        result.append(key)
        return result
    else:
        return []
    
def check_chartjs_basic_items(json_data):
    if "type" in json_data and "options" in json_data and "data" in json_data:
        return True
    else:
        return False
    
def check_chartjs_in_code(lines):
    for line in lines:
        json_data = json.loads(line)
        if check_chartjs_basic_items(json_data):
            return json_data
    return None

def check_attribute_in_schema_tables(all_tables, attribute):
    for table in all_tables:
        if attribute in table["table"]:
            return True
    return False

def check_namespace_in_schema_tables(schema_tables, namespace_attribute, verbose=False):
    namespace, attribute = namespace_attribute.rsplit(".", maxsplit=1)
    for schema_table in schema_tables:
        namespace_p = namespace.split(".")
        for schema_namespace_p in schema_table["namespaces_p"]:
            intersection =  set(namespace_p) & set(schema_namespace_p)
            if len(intersection) > 0 and attribute in schema_table["table"]:
                if verbose:
                    print(namespace_attribute)
                    print(schema_namespace_p)
                    print(attribute)
                return schema_table
    return None


def check_json_line_in_schema_table(schema_tables, line, threshold=3, verbose=False):
    json_data = json.loads(line)
    namespaces = json_to_namespaces(json_data)
    collected_attrs = []
    for namespace in namespaces:
        if "." not in namespace:
            attribute = namespace
            check_result = check_attribute_in_schema_tables(schema_tables, attribute)
        else:
            check_result = check_namespace_in_schema_tables(schema_tables, namespace, verbose=verbose)

        if check_result:
            collected_attrs.append(namespace)

    if len(collected_attrs) >= threshold:
        if verbose:
            print(collected_attrs)
        return True
    else:
        return False


def recursive_extract_obj_expression(node):
    if isinstance(node, dict):
        if node.get("type", None) == "ObjectExpression":
            return [node]
        else:
            result = []
            for _, value in node.items():
                if not (isinstance(value, bool) or \
                        isinstance(value, int) or \
                        isinstance(value, float) or \
                        isinstance(value, str)) and value:
                    result += recursive_extract_obj_expression(value)
            return result
    elif isinstance(node, list):
        result = []
        for value in node:
            result += recursive_extract_obj_expression(value)
        return result
    elif not node:
        return []
    else:
        print("x"*50)
        print(node)
        return []


def transform_node_to_json(node):
    if  node["type"] == "Identifier":
        return node["name"]
    elif node["type"] == "Literal":
        return node["value"]
    elif node["type"] == "ArrayExpression":
        result = []
        for element in node["elements"]:
            result.append(transform_node_to_json(element))
        return result
    elif node["type"] == "ObjectExpression":
        result = {}
        for property in node["properties"]:
            if "key" not in property:
                continue

            key_obj = property["key"]
            if key_obj["type"] == "Literal":
                key = key_obj["value"]
            elif key_obj["type"] == "Identifier":
                key = key_obj["name"]
            else:
                print("Exception key!")
                print(key_obj)
                continue

            value_obj = property["value"]
            if value_obj["type"] == "Literal":
                value = value_obj["value"]
            elif value_obj["type"] == "Identifier":
                value = value_obj["name"]
            else:
                value = transform_node_to_json(value_obj)
            
            result[key] = value
        return result
    elif node["type"].endswith("Expression"):
        return f"<{node['type']}>"
    elif node["type"] == "TemplateLiteral":
        return f"<{node['type']}>"
    elif node["type"] == "SpreadElement":
        return f"<{node['type']}>"
    else:
        print("x"*50)
        print(node)