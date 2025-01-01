import re



def transform_mathematical_operation(s):
    # Input
    # THEN( [Successful] +
    #   NVL([Presentation Layer].[Ir_Section].[Grade D],0)+NVL([Presentation
    #   Layer].[Ir_Section].[Grade F],0)+NVL([Presentation
    #   Layer].[Ir_Section].[Grade Np],0)+NVL([Presentation
    #   Layer].[Ir_Section].[Grade Nc],0)+NVL([Presentation
    #   Layer].[Ir_Section].[Grade I],0)) END

    result_list = []
    mathematical_operation = r"\[(.*?)\]\s*\+"
    mathematical_operation_finding = re.findall(mathematical_operation, s)
    if mathematical_operation_finding:
        mathematical_operation_finding_final = str(mathematical_operation_finding[0]).replace("'", "").upper()
        result_list.append(f"try [{mathematical_operation_finding_final}] otherwise 0")
    
    splitted = s.split("+NVL")
    for i in splitted:
        pattern = r"\[.*?\]\.\[.*?\]\.\[(.*?)\],?(\d*)"
        pattern_modification = re.findall(pattern, i)
        if pattern_modification:
            pattern_modification_final = (str(pattern_modification[0][0]).replace("(", "").replace(" ", "_").replace(")", "").replace("'", "").lower())
            result_list.append(f"try [{pattern_modification_final}] otherwise {pattern_modification[0][1]}")
    
    return ",\n".join(result_list)
        # Output
        #    List.Sum({ 
        #         try [SUCCESSFUL] otherwise 0, 
        #         try [grade_d] otherwise 0, 
        #         try [grade_f] otherwise 0, 
        #         try [grade_np] otherwise 0, 
        #         try [grade_nc] otherwise 0, 
        #         try [grade_i] otherwise 0 
        #     }) 
        # else null

def iflogic_modify(s):
    # Input-  WHEN([Presentation Layer].[Ir_Section].[Campus] = 'BA' )THEN

    pattern = r"\[*.*?\]\.\[.*?\]\.(\[.*?\]),?\d*\)*"
    IF_logic = re.findall(pattern,s)
    IF_logic_Final = re.sub(pattern,IF_logic[0],s)
    return IF_logic_Final
    # output Extract [Campus]

def IF_ELSE_modification(s):
    # Input
    # WHEN([Presentation Layer].[Ir_Section].[Campus] IN ( 'BO' ,
    #   'BG' , 'BQ' ))

    pattern = r"\[*.*?\]\.\[.*?\]\.\[(.*?)\],?\d*"
    matching_pattern= re.findall(pattern,s)

    in_values = re.findall(r"IN\s*\((.*?)\)", s)
    if in_values:
        in_values_list = in_values[0].replace("'", "").split(',')
        return " or ".join([f"if{matching_pattern}= \"{value}\" "for value in in_values_list])
    # output
    # if [campus] = "BO" or [campus] = "BG" or [campus] = "BQ" then "BC Delano Campus"
    
def else_if_logic(s):
    # WHEN([Presentation Layer].[Ir_Section].[Campus] = 'BI' )THEN
    #   ('BC Bakersfield Area')
    else_part = iflogic_modify(s)
    else_logic= f"else if {else_part}".replace("'",'"').replace(")","")
    return else_logic

    # else if [Campus] = "BI" 

def transform_substrlogic_IF_condition(when):

            # CASE WHEN (substr ([Presentation
            #   Layer].[Ir_Section].[Academic_Period],5,2) IN
            #   ('50','70'))
            #   THEN
    
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

    # if Text.Middle([academic_period], 4, 2) = "50" or Text.Middle([academic_period], 4, 2) = "70" then

def transform_substrlogic_then_condition(then_clause):
    # THEN
    #   substr([Presentation
    #   Layer].[Ir_Section].[Academic_Period],1,4)||'-'||TO_CHAR(TO_NUMBER(substr([Presentation
    #   Layer].[Ir_Section].[Academic_Period],1,4))+1) ELSE

    # or

    # ELSE
    #   TO_CHAR(TO_NUMBER(substr([Presentation
    #   Layer].[Ir_Section].[Academic_Period],1,4))-1)||'-'||substr([Presentation
    #   Layer].[Ir_Section].[Academic_Period],1,4) END

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

    # Text.Start([academic_period], 4) & "-" & Text.From(Number.FromText(Text.Start([academic_period], 4)) + 1)



#main query

def transform_sql_to_mquery(sql_query):
    sql_query = " ".join(sql_query.split())  
    
    #Identify when pattern - WHEN ([Presentation Layer].[Ir_Section].[Credit_Status] NOT IN('N'))THEN
    when_pattern = re.findall(r"WHEN\s*(.*?)\s*THEN", sql_query)
    #Identify then pattern -THEN( [Successful] +NVL([Presentation Layer].[Ir_Section].[Grade D],0)+NVL([Presentation Layer].[Ir_Section].[Grade F],0)+NVL([PresentationLayer].[Ir_Section].[Grade Np],0)+NVL([Presentation Layer].[Ir_Section].[Grade Nc],0)+NVL([Presentation Layer].[Ir_Section].[Grade I],0)) END
    then_pattern = re.findall(r'THEN\s*(.*?)\s*(?:WHEN|ELSE|END)', sql_query)
    #Identify else pattern -ELSE ([Presentation Layer].[Ir_Section].[Campus_Desc])END
    else_pattern = re.findall(r'ELSE\s*(.*?)\s*END', sql_query)

    result = []

    for i, when in enumerate(when_pattern):
        
        if i == 0:  #Handle first WHEN 

            if 'substr' in when:  #Handle substr with when logic 
                transformed_when = transform_substrlogic_IF_condition(when)
                result.append(f"if {transformed_when} then")

            else:  # Handle subsequent WHEN with ELSE IF

                IF_ELSE_pattern =  r"IN\s*\((.*?)\)"  # CASE WHEN([Presentation Layer].[Ir_Section].[Campus] IN ( 'BO' ,'BG' , 'BQ' ))THEN ('BC Delano Campus')
                IF_ELSE_logic = re.findall(IF_ELSE_pattern,when)

                in_values_list = IF_ELSE_logic[0].replace("'", "").split(',')
                if len(in_values_list)>1:  #in values more than 1
                    IF_ELSE__result = IF_ELSE_modification(when)
                    result.append(IF_ELSE__result)

                else:  #  WHEN ([Presentation Layer].[Ir_Section].[Credit_Status] NOT IN ('N'))
                    when = when.replace("'",'"').replace('NOT IN','<>')#.replace('(',"").replace(')',"")
                    when_matches = iflogic_modify(when)
                    result.append(f"if {when_matches} then")
        else:
            
            else_if = else_if_logic(when)
            result.append(else_if)

        if "+NVL" in then_pattern[i] or "+COALESCE" in then_pattern[i]:    # Handle THEN with +NVL or +COALESCE
            NVL_ = transform_mathematical_operation(then_pattern[i])
            transformed_then = f"List.Sum({{{NVL_}}})else null"
            result.append(transformed_then)

        elif 'substr' in then_pattern[i]:  # Handle THEN with substr logic
            transformed_then = transform_substrlogic_then_condition(then_pattern[i])
            result.append(f"{transformed_then}")

        else:  # Handle other THEN clauses  Input - THEN ('PC Online')
            then_modification = f"then {then_pattern[i]}".replace("(","").replace(")","").replace("'",'"')
            result.append(then_modification)

    if else_pattern:
        if 'substr' in else_pattern[0]:  # Handle ELSE with substr logic
            transformed_else = transform_substrlogic_then_condition(else_pattern[0])
            result.append(f"else {transformed_else}")

        else:  # Handle simple ELSE clauses
            else_result = iflogic_modify(else_pattern[0])
            result.append(f"else {else_result}")

    final="\n".join(result)
