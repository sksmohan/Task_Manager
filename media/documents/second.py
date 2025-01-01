import re
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


sql_query1='''SELECT
						PD.APPLICABLE_GROSS_AMOUNT,
						PD.CALENDAR_YEAR,
						PD.DEDUCTION,
						EMP.EMPLOYEE_CLASS,
						PD.EMPLOYEE_DEDUCTION_AMOUNT,
						PD.EMPLOYER_DEDUCTION_AMOUNT,
						PD.EVENT_SEQUENCE_NUMBER,
						PD.ID,
						PD.NAME,
						PD.PAYROLL_IDENTIFIER,
						PD.PAYROLL_NUMBER
						FROM ODSMGR.EMPLOYEE EMP,
						ODSMGR.PAYROLL_DEDUCTION PD
						WHERE ( ( EMP.PERSON_UID = PD.PERSON_UID(+) ) )
						AND ( PD.PAYROLL_NUMBER = ( #prompt('p_Select_Payroll_Period')# ) )
						AND ( PD.CALENDAR_YEAR(+) = (#prompt('p_Calendar_Year')# ))
						AND ( PD.DEDUCTION in (#promptmany('p_Put_In_Deduction_Numbers')#))
'''

def sql_edit(string):

    pattern1 = r"\s*[A-Za-z0-9_]+\.[A-Za-z0-9_]+\s*\([^)]*[#prompt|#promptmany]+\([^\)]*\)[^)]*\)[^,;]*,?"
    cleaned_sql = re.findall(pattern1, string)
    empty = []

    for i in cleaned_sql:
        if ' AS ' in i:
            first = r"\s+AS\s+([^,;]*),?"
            matches = re.findall(first, i)
            empty.append(matches[0])
        else:
            first = r"\s*[A-Za-z0-9_]+\.([A-Za-z0-9_]+)\s*\([^)]*[#prompt|#promptmany]+"
            matches = re.findall(first, i)
            empty.append(matches[0])

    cleaned_sql1 = re.sub(pattern1,"",string)

    new1=r"WHERE\s*\(\s*\([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\s*=\s*#(?:prompt|promptmany)\([^\)]*\)#\)\s*(?:AND|OR)\s*"
    cleaned_sql1 = re.sub(new1,"WHERE ( ",cleaned_sql1)
    
    pattern2 =r"\s*(AND|OR)?\s*\([^)]*(\([\+#]?\))?\s*[^)]*#prompt(?:many)?\([^\)]*\)[^\)]*\s*\)?\s*\)?"
    cleaned_sql1 = re.sub(pattern2,"",cleaned_sql1)

    return cleaned_sql1 ,empty

print(sql_edit(sql_query1)[0])


def remove_prompt_logic_and_find_aliases(input_sql):
    
    select_pattern = r"\s*[A-Za-z0-9_]+\.[A-Za-z0-9_]+\s*\([^)][#prompt|#promptmany]+\([^\)]\)[^)]\)[^,;],?"
    select_alias = re.findall(select_pattern, input_sql)

    extracted_columns = []

    for match in select_alias:
        if ' AS ' in match:
            alias_pattern = r"\s+AS\s+([^,;]*),?"
            alias_matches = re.findall(alias_pattern, match)
            extracted_columns.append(alias_matches[0])
        else:
            column_pattern = r"\s*[A-Za-z0-9_]+\.([A-Za-z0-9_]+)\s*\([^)]*[#prompt|#promptmany]+"
            column_matches = re.findall(column_pattern, match)
            extracted_columns.append(column_matches[0])

    
    cleaned_sql = re.sub(select_pattern, "", input_sql)

    
    where_clause_pattern = r"WHERE\s*\(\s*\([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\s*=\s*#(?:prompt|promptmany)\([^\)]\)#\)\s(?:AND|OR)\s*"
    cleaned_sql = re.sub(where_clause_pattern, "WHERE ( ",cleaned_sql)
    
    
    remaining_prompt_pattern = r"\s*(AND|OR)?\s*\([^)](\([\+#]?\))?\s[^)]#prompt(?:many)?\([^\)]\)[^\)]\s\)?\s*\)?"
    final_cleaned_sql = re.sub(remaining_prompt_pattern, "", cleaned_sql)

    return final_cleaned_sql, extracted_columns


# print(remove_prompt_logic_and_find_aliases(sql_query)[0])







pattern2 = r"\s*['AND'|'OR']*\s*\(\s*[a-zA-Z0-9_()\+]+\.[a-zA-Z0-9_()\+=]+\s=\s[#prompt|#promptmany]+\([^\)]*\)#\s*\)"
















# # ii =''' WHERE ( (o100942.FINAID_CAMPUS = #prompt('p_FAcollege')#)
#                             AND ( o100942.ACADEMIC_PERIOD = o100861.ACADEMIC_PERIOD
#                             AND o100942.PERSON_UID = o100861.PERSON_UID))
#                             AND (o100942.IS_ENROLLED = 'Y')
#                             -- AND (o100942.SATISFACTORY_ACAD_PROG_CODE = :SAPCODES)
#                             AND (o100942.ACADEMIC_PERIOD = #prompt('p_term')#)
#                             AND (o100942.FINAID_CAMPUS = #prompt('p_FAcollege')#)
#                             OR (o100942.AID_YEAR = #prompt('p_Aid_Year')#)
#                             ORDER BY o100861.NAME ASC'''
# # new1 = r"WHERE\s*\(\s*(\([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\s=\s[#prompt|#promptmany]+\([^\)]*\)#\)\n*['AND'|'OR']+)"
# new1=r"WHERE\s*\(\s*\([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\s*=\s*#(?:prompt|promptmany)\([^\)]*\)#\)\s*(?:AND|OR)\s*"
# new3 = re.sub(new1,"WHERE ( ",ii)
# print(new3)