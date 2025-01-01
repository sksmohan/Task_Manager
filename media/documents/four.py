import re

# def sql_edit(string):

#     pattern1 = r"\s*[A-Za-z0-9_]+\.[A-Za-z0-9_]+\s*\([^)][#prompt|#promptmany]+\([^\)]\)[^)]\)[^,;],?"
#     cleaned_sql = re.findall(pattern1, string)
#     empty = []

#     for i in cleaned_sql:
#         if ' AS ' in i:
#             first = r"\s+AS\s+([^,;]*),?"
#             matches = re.findall(first, i)
#             empty.append(matches[0])
#         else:
#             first = r"\s*[A-Za-z0-9_]+\.([A-Za-z0-9_]+)\s*\([^)]*[#prompt|#promptmany]+"
#             matches = re.findall(first, i)
#             empty.append(matches[0])

#     cleaned_sql1 = re.sub(pattern1,"",string)

#     new1=r"WHERE\s*\(\s*\([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\s*=\s*#(?:prompt|promptmany)\([^\)]\)#\)\s(?:AND|OR)\s*"
#     cleaned_sql1 = re.sub(new1,"WHERE ( ",cleaned_sql1)
    
#     pattern2 =r"\s*(AND|OR)?\s*\([^)](\([\+#]?\))?\s[^)]#prompt(?:many)?\([^\)]\)[^\)]\s\)?\s*\)?"
#     cleaned_sql1 = re.sub(pattern2,"",cleaned_sql1)

#     return cleaned_sql1 ,empty

def sql_edit(string):

    pattern1 = r"\s*[A-Za-z0-9_]+\.[A-Za-z0-9_]+\s*\([^)]*[#¿]+(?:prompt|promptmany)+\([^\)]*\)[^)]*\)[^,;]*,?"
    cleaned_sql = re.findall(pattern1, string)
    empty = []

    for i in cleaned_sql:
        if ' AS ' in i:
            first = r"\s+AS\s+([^,;]*),?"
            matches = re.findall(first, i)
            empty.append(matches[0])
        else:
            first = r"\s*[A-Za-z0-9_]+\.([A-Za-z0-9_]+)\s*\([^)]*[#¿]+(?:prompt|promptmany)+"
            matches = re.findall(first, i)
            empty.append(matches[0])

    cleaned_sql1 = re.sub(pattern1,"",string)

    new1=r"WHERE\s*\(\s*\([a-zA-Z0-9_]+\.[a-zA-Z0-9_]+\s*=\s*[#¿]+(?:prompt|promptmany)\([^\)]*\)[#¿]+\)\s*(?:AND|OR)\s*"
    cleaned_sql1 = re.sub(new1,"WHERE ( ",cleaned_sql1)
    
    pattern2 =r"\s*(AND|OR)?\s*\([^)]*(\([\+#]?\))?\s*[^)]*[#¿]+prompt(?:many)?\([^\)]*\)[^\)]*\s*\)?\s*\)?"
    cleaned_sql1 = re.sub(pattern2,"",cleaned_sql1)

    return cleaned_sql1 ,empty



sql_query = """
 SELECT ODSMGR_CUST.FW_GET_BASIC_SKILL_SUM (o100942.PERSON_UID,
						o100942.ACADEMIC_PERIOD)
						AS BasicSkillSum,
						ODSMGR_CUST.FW_GET_PREV_SAP_CODE (o100942.PERSON_UID, #prompt('p_term')# )
						AS GET_PREV_SAP_CODE,
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
						WHEN TO_NUMBER (o100942.CREDITS_ATTEMPTED) &gt; 0
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
						WHERE ( ( o100942.ACADEMIC_PERIOD = o100861.ACADEMIC_PERIOD
						AND o100942.PERSON_UID = o100861.PERSON_UID))
						AND (o100942.IS_ENROLLED = 'Y')
						-- AND (o100942.SATISFACTORY_ACAD_PROG_CODE = :SAPCODES)
						AND (o100942.ACADEMIC_PERIOD = #prompt('p_term')#)
						AND (o100942.FINAID_CAMPUS = #prompt('p_FAcollege')#)
						AND (o100942.AID_YEAR = #prompt('p_Aid_Year')#)
						ORDER BY o100861.NAME ASC
"""

sql_query2="""
SELECT finaid.FW_GET_BASIC_SKILL_SUM (o100942.PERSON_UID, o100942.ACADEMIC_PERIOD) AS BasicSkillSum,
       finaid.FW_GET_PREV_SAP_CODE (o100942.PERSON_UID, ¿prompt('p_term')¿) AS GET_PREV_SAP_CODE,
       CASE
           WHEN ((finaid.F_SPLIT_FIELDS (finaid.FW_GET_OVERALL_GPA_TERM_STATS (o100942.PERSON_UID, o100942.PREVIOUSLY_ENROLLED_TERM), 1)) = '0'
                 OR (finaid.F_SPLIT_FIELDS (finaid.FW_GET_OVERALL_GPA_TERM_STATS (o100942.PERSON_UID, o100942.PREVIOUSLY_ENROLLED_TERM), 1)) IS NULL) THEN 0
           ELSE CAST ((finaid.F_SPLIT_FIELDS (finaid.FW_GET_OVERALL_GPA_TERM_STATS (o100942.PERSON_UID, o100942.PREVIOUSLY_ENROLLED_TERM), 2)) AS integer) / CAST ((finaid.F_SPLIT_FIELDS (finaid.FW_GET_OVERALL_GPA_TERM_STATS (o100942.PERSON_UID, o100942.PREVIOUSLY_ENROLLED_TERM), 1)) AS integer)
       END AS OVERALL_GPA_TERM_STATS,
       CASE
           WHEN CAST (o100942.CREDITS_ATTEMPTED AS integer) > 0 THEN CAST (o100942.CREDITS_EARNED AS integer) / CAST (o100942.CREDITS_ATTEMPTED AS integer)
           ELSE 0
       END AS PERCENT_COMPLETED,
       o100942.ACADEMIC_PERIOD AS Term,
       o100942.AID_YEAR AS AIDYEAR,
       o100942.CREDITS_ATTEMPTED AS CREDITS_ATTEMPT,
       o100942.CREDITS_EARNED AS CREDITS_EARN,
       o100861.ENROLLMENT_STATUS AS ENROLL_STATUS,
       o100942.FINAID_CAMPUS AS FINAID_CAMPUS,
       cast(o100942.GPA_SCORE AS integer) AS GPA_SCORE,
       o100861.ID AS ID,
       o100942.IS_ENROLLED AS IS_ENROLLED,
       o100861.NAME AS StuNAME,
       o100942.SATISFACTORY_ACAD_PROG_CODE AS SAP_CODE,
       o100861.TOTAL_CREDITS AS TOTAL_CREDIT
FROM finaid.ENROLLMENT o100861,
     finaid.FINAID_SAP_GPA o100942
WHERE ((o100942.ACADEMIC_PERIOD = o100861.ACADEMIC_PERIOD
        AND o100942.PERSON_UID = o100861.PERSON_UID))
  AND (o100942.IS_ENROLLED = 'Y')
  AND (o100942.ACADEMIC_PERIOD = ¿prompt('p_term')¿)
  AND (o100942.FINAID_CAMPUS = ¿prompt('p_FAcollege')¿)
  AND (o100942.AID_YEAR = ¿prompt('p_Aid_Year')¿)
ORDER BY o100861.NAME ASC
SELECT BasicSkillSum,
       GET_PREV_SAP_CODE,
       OVERALL_GPA_TERM_STATS,
       PERCENT_COMPLETED,
       Term,
       AIDYEAR,
       CREDITS_ATTEMPT,
       CREDITS_EARN,
       ENROLL_STATUS,
       FINAID_CAMPUS,
       GPA_SCORE,
       ID,
       IS_ENROLLED,
       StuNAME,
       SAP_CODE,
       TOTAL_CREDIT
FROM finaid.FinAidresult"""


# print(sql_edit(sql_query)[0])
print(sql_edit(sql_query2)[0])
