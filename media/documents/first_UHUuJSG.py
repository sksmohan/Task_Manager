'''
let
    Source = Sql.Database("YourServerName", "YourDatabaseName"),
    Enrollment = Source{[Schema="ODSMGR",Item="ENROLLMENT"]}[Data],
    Finaid_SAP_GPA = Source{[Schema="ODSMGR_CUST",Item="FINAID_SAP_GPA"]}[Data],
    
    // Filter Finaid_SAP_GPA table based on parameters
    FilteredFinaid = Table.SelectRows(Finaid_SAP_GPA, each 
        [FINAID_CAMPUS] = "#prompt('p_FAcollege')#" and 
        [ACADEMIC_PERIOD] = "#prompt('p_term')#" and 
        [IS_ENROLLED] = "Y"
    ),
    
    // Join with Enrollment table on PERSON_UID
    JoinedTables = Table.Join(FilteredFinaid, "PERSON_UID", Enrollment, "PERSON_UID", JoinKind.Inner),
    
    // Add calculated columns
    AddedColumn = Table.AddColumn(JoinedTables, "OVERALL_GPA_TERM_STATS", each
        let
            GPA = try [FW_GET_OVERALL_GPA_TERM_STATS] otherwise null,
            SplitFields = try [F_SPLIT_FIELDS] otherwise null,
            GPA_1 = if SplitFields{1} = "0" or SplitFields{1} = null then 0 else 
                    Number.FromText(SplitFields{2}) / Number.FromText(SplitFields{1})
        in
            GPA_1
    ),
    AddedPercentCompleted = Table.AddColumn(AddedColumn, "PERCENT_COMPLETED", each
        if [CREDITS_ATTEMPTED] > 0 then 
            [CREDITS_EARNED] / [CREDITS_ATTEMPTED]
        else
            0
    ),
    
    // Apply additional filters based on prompts
    FilteredData = Table.SelectRows(AddedPercentCompleted, each
        [CALENDAR_YEAR] = "#prompt('p_Calendar_Year')#" and
        List.Contains(#promptmany('p_Put_In_Deduction_Numbers')#, [DEDUCTION])
    ),
    
    // Sort by Student Name
    SortedData = Table.Sort(FilteredData, {{"StuNAME", Order.Ascending}})
in
    SortedData
'''

sql_query = """
SELECT ODSMGR_CUST.dddd (o100942.PERSON_UID,
                            #prompt('p_term')# ),
                            ODSMGR_CUST.FW_GET_PREV_SAP_CODE (o100942.PERSON_UID,ewewewe,#prompt('p_term')#,wqwwhhehej )
                            AS GET_PREV_SAP_CODE,
                            ODSMGR_CUST.FW_GET_PREV_SAP_CODE (o100942.PERSON_UID,ewewewe,wqwwhhehej )
                            AS FIRST,
                            CASE
                            WHEN ( (ODSMGR_CUST.F_SPLIT_FIELDS (
                            ODSMGR_CUST.FW_GET_OVERALL_GPA_TERM_STATS (
                            o100942.PERSON_UID,
                            o100942.PREVIOUSLY_ENROLLED_TERM),
                            1)) = '0'
                            OR (ODSMGR_CUST.F_SPLIT_FIELDS (
                            ODSMGR_CUST.FW_GET_OVERALL_GPA_TERM_STATS (
                            o100942.PERSON_UID,
                            o100942.PREVIOUSLY_ENROLLED_TERM),
                            1))
                            IS NULL)
                            THEN
                            0
                            ELSE
                            TO_NUMBER (
                            (ODSMGR_CUST.F_SPLIT_FIELDS (
                            ODSMGR_CUST.FW_GET_OVERALL_GPA_TERM_STATS (
                            o100942.PERSON_UID,
                            o100942.PREVIOUSLY_ENROLLED_TERM),
                            2)))
                            / TO_NUMBER (
                            (ODSMGR_CUST.F_SPLIT_FIELDS (
                            ODSMGR_CUST.FW_GET_OVERALL_GPA_TERM_STATS (
                            o100942.PERSON_UID,
                            o100942.PREVIOUSLY_ENROLLED_TERM),
                            1)))
                            END
                            AS OVERALL_GPA_TERM_STATS,
                            CASE
                            WHEN TO_NUMBER (o100942.CREDITS_ATTEMPTED) > 0
                            THEN
                            TO_NUMBER (o100942.CREDITS_EARNED)
                            / TO_NUMBER (o100942.CREDITS_ATTEMPTED)
                            ELSE
                            0
                            END
                            AS PERCENT_COMPLETED,
                            o100942.ACADEMIC_PERIOD
                            AS Term,
                            o100942.AID_YEAR
                            AS AIDYEAR,
                            o100942.CREDITS_ATTEMPTED
                            AS CREDITS_ATTEMPT,
                            o100942.CREDITS_EARNED
                            AS CREDITS_EARN,
                            o100861.ENROLLMENT_STATUS
                            AS ENROLL_STATUS,
                            o100942.FINAID_CAMPUS
                            AS FINAID_CAMPUS,
                            to_number(o100942.GPA_SCORE)
                            AS GPA_SCORE,
                            o100861.ID
                            AS ID,
                            o100942.IS_ENROLLED
                            AS IS_ENROLLED,
                            o100861.NAME
                            AS StuNAME,
                            o100942.SATISFACTORY_ACAD_PROG_CODE
                            AS SAP_CODE,
                            o100861.TOTAL_CREDITS
                            AS TOTAL_CREDIT
                            FROM ODSMGR.ENROLLMENT o100861, ODSMGR_CUST.FINAID_SAP_GPA o100942
                            WHERE ( (o100942.FINAID_CAMPUS = #prompt('p_FAcollege')#)
                            AND ( o100942.ACADEMIC_PERIOD = o100861.ACADEMIC_PERIOD
                            AND o100942.PERSON_UID = o100861.PERSON_UID))
                            AND (o100942.IS_ENROLLED = 'Y')
                            -- AND (o100942.SATISFACTORY_ACAD_PROG_CODE = :SAPCODES)
                            AND (o100942.ACADEMIC_PERIOD = #prompt('p_term')#)
                            AND ( PD.CALENDAR_YEAR = #prompt('p_Calendar_Year')# )
                            AND ( PD.CALENDAR_YEAR(#) = (#prompt('p_Calendar_Year')# ))
                            AND ( PD.DEDUCTION in (#promptmany('p_Put_In_Deduction_Numbers')#))
                            OR (o100942.AID_YEAR = #prompt('p_Aid_Year')#)
                            ORDER BY o100861.NAME ASC  
"""
import re

def convert_sql_to_mquery(sql_query):
    m_query = ""

    # Step 1: Extract SELECT statement columns
    select_columns = re.findall(r"SELECT(.*?)FROM", sql_query, re.DOTALL)
    if select_columns:
        select_columns = select_columns[0].strip()
        # Remove AS aliases and extra spaces
        select_columns = re.sub(r" AS \w+", "", select_columns)
        columns = select_columns.split(',')
        m_query += "let\n"
        m_query += "    Source = Sql.Database(\"YourServerName\", \"YourDatabaseName\"),\n"
        m_query += "    RawData = Source{[Schema=\"ODSMGR\",Item=\"ENROLLMENT\"]}[Data],\n"

        # Step 2: Handle WHERE conditions (simple equality and logical operators)
        where_conditions = re.findall(r"WHERE(.*?)ORDER BY", sql_query, re.DOTALL)
        if where_conditions:
            where_conditions = where_conditions[0].strip()
            where_clauses = where_conditions.split("AND")
            m_query += "    FilteredRows = Table.SelectRows(RawData, each\n"
            for clause in where_clauses:
                clause = clause.strip()
                clause = re.sub(r"=", " = ", clause)
                clause = re.sub(r"AND", "and", clause)
                clause = re.sub(r"OR", "or", clause)
                m_query += f"        {clause} and "
            m_query = m_query.rstrip(" and ")  # Remove trailing "and"
            m_query += "),\n"

        # Add SELECT columns (replace placeholders for real values or parameters)
        m_query += "    SelectedColumns = Table.SelectColumns(FilteredRows, {"
        for col in columns:
            col = col.strip()
            m_query += f"\"{col}\", "
        m_query = m_query.rstrip(", ")  # Remove trailing comma
        m_query += "}),\n"

    # Step 3: Handle JOIN operations
    joins = re.findall(r"(INNER|LEFT|RIGHT|FULL)\s+JOIN\s+(\S+)\s+ON\s+(.+)", sql_query, re.DOTALL)
    if joins:
        for join in joins:
            join_type, table_name, on_condition = join
            # Translate SQL JOIN to M Query JOIN syntax
            m_query += f"    {join_type}JoinedData = Table.Join(SelectedColumns, \"{on_condition}\", {table_name}, \"{on_condition}\", JoinKind.{join_type}),\n"

    # Step 4: Handle CASE expressions (CASE WHEN ... THEN ... ELSE)
    case_statements = re.findall(r"CASE(.*?)END", sql_query, re.DOTALL)
    if case_statements:
        for case in case_statements:
            # Try to match WHEN and THEN parts without assuming parentheses
            when_match = re.search(r"WHEN\s+(.*?)\s+THEN", case)
            then_match = re.search(r"THEN\s+(.*)", case)
            
            if when_match and then_match:
                condition = when_match.group(1).strip()
                action = then_match.group(1).strip()
                m_query += f"    ComputedColumn = Table.AddColumn(SelectedColumns, \"Computed\", each if {condition} then {action} else 0),\n"
            else:
                # Handle the case if no match found (optional: print a message or skip the case)
                print("Error in CASE statement parsing:", case)
    
    # Step 5: Handle ORDER BY (Sorting)
    order_by = re.findall(r"ORDER BY(.*)", sql_query)
    if order_by:
        order_columns = order_by[0].strip().split(',')
        m_query += "    SortedData = Table.Sort(SelectedColumns, {\n"
        for column in order_columns:
            column = column.strip()
            # Assuming default sorting direction is Ascending, you can add handling for DESC
            m_query += f"        {{\"{column}\", Order.Ascending}},\n"
        m_query = m_query.rstrip(",\n")  # Remove trailing comma
        m_query += "\n    }),\n"

    # Step 6: Close the M Query script
    m_query += "in\n"
    m_query += "    SortedData"

    return m_query

print(convert_sql_to_mquery(sql_query),"-----------")