import re
sql_query ="""CASE WHEN ([Presentation Layer].[Ir_Section].[Credit_Status] NOT IN
      ('N'))
      THEN( [Retained] +
      NVL([Presentation Layer].[Ir_Section].[Grade W],0)+NVL([Presentation
      Layer].[Ir_Section].[Grade Dr],0)) END"""

sql_query = " ".join(sql_query.split())

when_then_pattern = r"WHEN\s*(.*?)\s*THEN"
when_then_matches = re.findall(when_then_pattern, sql_query)



then_clauses = re.findall(r'THEN\s*(.*?)\s*(?:WHEN|ELSE|END)', sql_query)


else_clauses = re.findall(r'ELSE\s*(.*?)\s*END', sql_query)


end_clauses = re.findall(r'ELSE\s*(.*?)\s*END', sql_query)



result = []

def transform_(s):
    lis = []
    success = r"\[(.*?)\]\s*\+"
    success_1 = re.findall(success,s)
    if success_1:
        success_final = str(success_1[0]).replace("'","").upper()
        lis.append(f"try [{success_final}] otherwise 0,")
    splitted = s.split("+NVL")
    for i in splitted:
        pattern1 = r"\[*.*?\]\.\[.*?\]\.\[(.*?)\],?(\d*)"
        pattern_modi = re.findall(pattern1,i)
        pattern_modi1 = str(pattern_modi[0][0]).replace("(","").replace(" ","_").replace(")","").replace("'","").lower()

        lis.append(f"try [{pattern_modi1}] otherwise {pattern_modi[0][1]},")
    return "\n".join(lis)

# CASE WHEN ([Presentation Layer].[Ir_Section].[Credit_Status] NOT IN
#       ('N'))
def if_modify(s):
    pattern1 = r"\[*.*?\]\.\[.*?\]\.(\[.*?\]),?\d*"
    first = re.findall(pattern1,s)
    second = re.sub(pattern1,first[0],s)
    return second



def fourt_modi(s):
    pattern1 = r"\[*.*?\]\.\[.*?\]\.\[(.*?)\],?\d*"
    single_value = re.findall(pattern1,s)

    fourth_function = r"IN\s*\(\s*'([a-zA-Z0-9]+)'\s*,\s*'([a-zA-Z0-9]+)'\s*,\s*'([a-zA-Z0-9]+)'\s*\)"
    fourth_fun = re.findall(fourth_function,s)

    return f'if{single_value} = "{fourth_fun[0][0]}" or {single_value} = "{fourth_fun[0][1]}" or {single_value} = "{fourth_fun[0][2]}"'

def else_if_func(s):
    first_part = if_modify(s)
    final_ = f"else if {first_part}".replace("'",'"').replace(")","")
    return final_

def transform_substr_condition(when):
    
    substr_pattern = r"substr\s*\(\s*\[.*?\]\.\[.*?\]\.\[(.*?)\],(\d+),(\d+)\)"
    matches = re.findall(substr_pattern, when)

    
    for match in matches:
        column = match[0]
        start_pos = int(match[1]) - 1 
        length = match[2]

        
        new_condition = f'Text.Middle([{column}], {start_pos}, {length})'

        
        if "IN" in when:
            
            in_values = re.findall(r"IN\s*\((.*?)\)", when)
            if in_values:
                
                in_values_list = in_values[0].replace("'", "").split(',')
                
                transformed_when = " or ".join([f"{new_condition} = \"{value.strip()}\"" for value in in_values_list])
                
                when = re.sub(r"\(substr\s*\(\s*\[.*?\]\.\[.*?\]\.\[(.*?)\],(\d+),(\d+)\)\s*IN\s*\((.*?)\)\)", transformed_when, when)

    
    return when


def transform_then_condition(then_clause):
    
    substr_pattern = r"substr\s*\(\s*\[.*?\]\.\[.*?\]\.\[(.*?)\],(\d+),(\d+)\)"
    matches = re.findall(substr_pattern, then_clause)

    for match in matches:
        column = match[0]
        start_pos = int(match[1])
        
        length = int(match[2])
        

        
        if start_pos == 1:
            new_condition = f'Text.Start([{column}], {length})'
        else:
            new_condition = f'Text.Middle([{column}], {length})'

        
        then_clause = then_clause.replace("||", "&")
        then_clause = then_clause.replace("'",'"')

        
        then_clause = then_clause.replace("TO_NUMBER", "Number.FromText")
        then_clause = then_clause.replace("TO_CHAR", "Text.From")

        
        then_clause = re.sub(r"substr\s*\(\s*\[.*?\]\.\[.*?\]\.\[(.*?)\],(\d+),(\d+)\)", new_condition, then_clause)

    
    return then_clause




for i, when in enumerate(when_then_matches):
    if i == 0:
        if 'substr' in when:
            transformed_when = transform_substr_condition(when)
            
            result.append(f"if {transformed_when} then")
        
        elif 'substr' not in when:
            fourth_function = r"IN\s*\(\s*'([a-zA-Z0-9]+)'\s*,\s*'([a-zA-Z0-9]+)'\s*,\s*'([a-zA-Z0-9]+)'\s*\)"
            fourth_fun = re.findall(fourth_function,when)
            if fourth_fun:
                four_result = fourt_modi(when)
                result.append(four_result)
            
        else:
            when = when.replace("'",'"').replace('NOT IN','<>').replace('(',"").replace(')',"")
            single_value = if_modify(when)
            result.append(f"if {single_value} then")
    else:
        else_if = else_if_func(when)
        result.append(else_if)

    if "+NVL" in then_clauses[i] or "+COALESCE" in then_clauses[i]:
        NVL_ = transform_(then_clauses[i])
        transformed_then = f"List.Sum({{{NVL_}}})else null"
        result.append(transformed_then)

    elif 'substr' in then_clauses[i]:
        transformed_then = transform_then_condition(then_clauses[i])
        result.append(f"{transformed_then}")

    else: 
        then_modification = f"then {then_clauses[i]}".replace("(","").replace(")","").replace("'",'"')
        result.append(then_modification)

if else_clauses:
    if 'substr' in else_clauses[0]:
        transformed_else = transform_then_condition(else_clauses[0])
        result.append(f"else {transformed_else}")
    else:
        else_result = if_modify(else_clauses[0])
        result.append(f"else {else_result}")


final="\n".join(result)
print(final)


