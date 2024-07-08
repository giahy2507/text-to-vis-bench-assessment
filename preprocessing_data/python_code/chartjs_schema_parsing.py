import glob
import re
import glob
import json


def check_table_in_segment(segment):
    for line in segment:
        seqs = line.strip().split(" | ")
        if len(seqs) >= 2:
            seqs = [seq.strip("| ") for seq in seqs]
            if "Name" in seqs and "Default" in seqs:
                return True
    return False

            
def extract_sections(markdown_file):
    doc_file_path = markdown_file
    with open(doc_file_path, mode="r", encoding="utf-8") as fi:
        lines = fi.readlines()
        segments = []
        segment = []
        for line in lines:
            if line.strip().startswith("#"):
                if len(segment) > 0:
                    segments.append(segment)
                segment = [line]
            else:
                segment.append(line) 

        if len(segment) > 0:
            segments.append(segment)
    return segments


def get_namespaces(lines):
    namespaces = []
    flag = False
    for line in lines:
        if line.strip() == "":
            continue
        if line.startswith("Namespaces"):
            flag = True
        else:
            m1 = re.search("^\*.`[a-zA-Z0-9.\[\]]+`.+options for", line)
            if m1:
                m2 = re.search("`[a-zA-Z0-9.\[\]]+`", line)
                m2_text = line[m2.regs[0][0]:m2.regs[0][1]]
                if flag == True:
                    namespaces.append(m2_text.strip("`"))
        
        m3 = re.search("Namespace.{1,20}`[a-zA-Z0-9.\[\]]+`", line)
        if m3:
            m2 = re.search("`[a-zA-Z0-9.\[\]]+`", line)
            m2_text = line[m2.regs[0][0]:m2.regs[0][1]]
            namespaces.append(m2_text.strip("`"))

    return namespaces

        
def parse_table(table):
    index_name = list(table[0][1]).index("Name")
    index_default = list(table[0][1]).index("Default")
    result_table = {}
    for id_row in table[2:]:
        _, row = id_row
        name_value = row[index_name]
        match_re = re.search("`[a-zA-Z0-9]+`", name_value)
        if match_re:
            name_value = name_value[match_re.regs[0][0]:match_re.regs[0][1]]
        if index_default >= len(row):
            default_value = ""
        else:
            default_value = row[index_default]
        result_table[name_value.strip(" `")] = default_value.strip(" `")
        
    return result_table


def extract_table(segment):
    tables = []
    table = []
    for i, line in enumerate(segment):
        if line.strip() == "":
            if len(table) > 0:
                tables.append(table)
                table = []
                continue
        else:
            line = line.replace("|",  " | ")
            seqs = line.strip().split(" | ")
            if len(seqs) >= 2:
                seqs = [seq.strip("| ") for seq in seqs]
                if "Name" in seqs and "Default" in seqs:
                    table.append((i, seqs)) 
                else:
                    if len(table) > 0:
                        table.append((i, seqs))
    if len(table) > 0:
        tables.append(table)
    return tables
        

def extract_md_table(segment):
    parsed_tables = extract_table(segment)
    result = []
    for table in parsed_tables:
        # extract namespace in list
        # get the first line index of table
        # get document above
        row_0 = table[0][0]
        lines = segment[:row_0]
        namespaces = get_namespaces(lines)
        # preprocessing namespace for later comparing
        namespaces_p = []
        for namespace in namespaces:
            namespace_p = re.sub("\[.+\]", "", namespace)
            namespace_p_list = namespace_p.split(".")
            namespaces_p.append(namespace_p_list)

        # get attribute name and default value
        extracted_table = parse_table(table)
        result.append({
            "namespaces": namespaces,
            "namespaces_p": namespaces_p,
            "table": extracted_table
        })
    return result


def get_all_schemas(chartjs_source_dir="/Users/hy/Documents/usyd/data/chartjs"):
    versions = ["4.4.0", "3.9.1", "2.9.4"]
    all_tables = []
    for version in versions:
        paths = glob.glob(f"{chartjs_source_dir}/Chart.js-{version}/docs/**/*.md")
        for path in paths:
            # path = "/Users/hy/Documents/usyd/data/chartjs/Chart.js-4.4.0/docs/axes/_common.md"
            # print(path)
            segments = extract_sections(path)
            # print("length of segments: ", len(segments))
            for segment in segments:
                if check_table_in_segment(segment):
                    tables = extract_md_table(segment)
                    for table in tables:
                        table["file"] = path.replace(f"{chartjs_source_dir}/Chart.js-{version}/docs/", "")
                        table["chartjs-version"] = version
                    all_tables.extend(tables)
        # print(version, len(paths) , len(all_tables))
    return all_tables


if __name__ == "__main__":
    


    # Extract library function definitions
    # This will help to identify ChartJS code and retrieve keyword arguments

    # Input: chartjs source code, downloaded from release page. https://github.com/chartjs/Chart.js/releases/tag/v4.4.0
    # - data/raw-data/graphics_schema/Chart.js-4.4.0
    # - data/raw-data/graphics_schema/Chart.js-3.9.1
    # - data/raw-data/graphics_schema/Chart.js-2.9.4
    # Output:
    # - data/universal/ChartJS_JavaScript.universal2.jsonl

    ChartJS_source_dir = "data/raw-data/schema/graphics_schema"
    output_schema_path = "data/raw-data/schema/graphics_schema/schema_tables.json"

    schema_tables = get_all_schemas(chartjs_source_dir=ChartJS_source_dir)
    with open(output_schema_path, mode="w", encoding="utf-8") as f:
        json.dump(schema_tables, f, indent=4)