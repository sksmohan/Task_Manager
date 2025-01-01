
# 1 to 3
import re

def firstT3(sql_query):
    
    sql_query = " ".join(sql_query.split())

    
    match = re.search(r"\[(.*?)\]\s*NOT\s*IN\s*\(\s*'(.*?)'\s*\)", sql_query, re.IGNORECASE)
    if not match:
        raise ValueError("Condition not found in SQL query.")
    
    field = match.group(1).split('.')[-1].lower()
    value = match.group(2)
    condition = f"{field}] <> \"{value}\""

    
    explicit_match = re.search(r"THEN\s*\(\s*\[([^\]]+)\]", sql_query, re.IGNORECASE)
    explicit_field = explicit_match.group(1).split('.')[-1].lower() if explicit_match else None

    
    nvl_fields = re.findall(r"NVL\(\[.*?\]\.\[.*?\]\.\[([^]]+)\]", sql_query, re.IGNORECASE)
    fields = [explicit_field] if explicit_field else []
    fields += [field.lower().replace(" ", "_") for field in nvl_fields]

    if not fields:
        raise ValueError("No valid fields found in SQL query.")

    
    fields_sum = ",\n".join([f"try [{field}] otherwise 0" for field in fields])
    m_query = f"if {condition} then \nList.Sum({{\n{fields_sum}\n}}) \nelse null"
    return m_query



# fourth one

def fourth(case_logic):
    case_logic = " ".join(case_logic.split())
    column_pattern = r"\[([^\]]+)\]\.\[([^\]]+)\]\.\[([^\]]+)\]"
    column_match = re.search(column_pattern, case_logic, re.DOTALL)

    

    column_name = column_match.group(3)
    

    when_then_pattern = r"WHEN\s*\((.*?)\)\s*THEN\s*\(?([^\)]+)\)?"
    conditions = re.findall(when_then_pattern, case_logic)

    else_pattern = r"ELSE\s+\((.*?)\)"
    else_match = re.search(else_pattern, case_logic)
    else_logic = else_match.group(1).strip() if else_match else None
    
    
    grouped_conditions = {}
    for condition, result in conditions:
        result = result.strip().replace("'", "")  
        
        
        condition = condition.strip()
        if "IN" in condition:
            
            condition = re.sub(r"\[([^\]]+)\]\.\[([^\]]+)\]\.\[([^\]]+)\]", f"[{column_name}]", condition)
            condition = condition.replace("IN", "=").replace("(", "").replace(")", "").replace(",", " or " + f"[{column_name}] =")
        else:
            
            condition = re.sub(r"\[([^\]]+)\]\.\[([^\]]+)\]\.\[([^\]]+)\]", f"[{column_name}]", condition)

        
        if result not in grouped_conditions:
            grouped_conditions[result] = []
        grouped_conditions[result].append(condition)

    
    m_query = ""
    for result, cond_list in grouped_conditions.items():
        combined_condition = " or ".join(cond_list)  
        if not m_query:
            m_query = f'if {combined_condition} then "{result}"'
        else:
            m_query += f'\nelse if {combined_condition} then "{result}"'

    
    column_name_elselogic=r"\[([^\]]+)\]\.\[([^\]]+)\]\.\[([^\]]+)\]"
    column_match_elselogic= re.search(column_name_elselogic, else_logic, re.DOTALL)
    column_name = column_match_elselogic.group(3)
    

    else_logic = re.sub(r"\[([^\]]+)\]\.\[([^\]]+)\]\.\[([^\]]+)\]", f"[{column_name}]", else_logic.strip())
    m_query += f'\nelse {else_logic}'

    return m_query




def sql_2_M(query):
    pattern = r"\[([^\]]+)\],(\d+),(\d+)\)\s*IN\s*\('([0-9]+)','([0-9]+)'\)"
    column_name = re.findall(pattern,query)

    pattern2 = r"\[([^\]]+)\],(\d+),(\d+)\)\|"
    column_name2 = re.findall(pattern2,query)

    pattern3 = r"\[([^\]]+\],\d+,\d+\)\)[-+*/0-9]+)"
    column_name3 = re.findall(pattern3,query)

    new_query = f'if Text.Middle([{column_name[0][0]}],{int(column_name[0][1])-1},{column_name[0][2]}) = "{column_name[0][3]}" or Text.Middle([{column_name[0][0]}],{int(column_name[0][1])-1},{column_name[0][2]}) = "{column_name[0][4]}" then \n Text.Start([{column_name2[0][0]}], {column_name2[0][-1]}) & "-" & Text.From(Number.FromText(Text.Start({column_name3[0]})\nelse\nText.From(Number.FromText(Text.Start({column_name3[0]}) & "-" & Text.Start([{column_name2[0][0]}], {column_name2[0][-1]})'

    return new_query

def process_sql_to_m_query(sql_query):
    
    if 'TO_CHAR' in sql_query:
        return sql_2_M(sql_query)
    
    if "WHEN" in sql_query and "ELSE" in sql_query:
        return fourth(sql_query)

    if "NOT IN" in sql_query or "NVL" in sql_query:
        return firstT3(sql_query)
    
    print('hiii')

    raise ValueError("Unrecognized SQL pattern. Could not route to the correct function.")




sql_query1 = """CASE WHEN (substr ([Presentation
      Layer].[Ir_Section].[Academic_Period],5,2) IN
      ('50','70'))
      THEN
      substr([Presentation
      Layer].[Ir_Section].[Academic_Period],1,4)||'-'||TO_CHAR(TO_NUMBER(substr([Presentation
      Layer].[Ir_Section].[Academic_Period],1,4))+1) ELSE
      TO_CHAR(TO_NUMBER(substr([Presentation
      Layer].[Ir_Section].[Academic_Period],1,4))-1)||'-'||substr([Presentation
      Layer].[Ir_Section].[Academic_Period],1,4) END
"""

print(process_sql_to_m_query(sql_query1))