import re
sql_query ="""CASE WHEN (substr ([Presentation
      Layer].[Ir_Section].[Academic_Period],5,2) IN
      ('50','70'))
      THEN
      substr([Presentation
      Layer].[Ir_Section].[Academic_Period],1,4)||'-'||TO_CHAR(TO_NUMBER(substr([Presentation
      Layer].[Ir_Section].[Academic_Period],1,4))+1) ELSE
      TO_CHAR(TO_NUMBER(substr([Presentation
      Layer].[Ir_Section].[Academic_Period],1,4))-1)||'-'||substr([Presentation
      Layer].[Ir_Section].[Academic_Period],1,4) END"""


sql_query = " ".join(sql_query.split())

when_then_pattern = r"WHEN\s*(.*?)\s*THEN"
when_then_matches = re.findall(when_then_pattern, sql_query)
# print(when_then_matches)

then_clauses = re.findall(r'THEN\s*(.*?)\s*(?:WHEN|ELSE|END)', sql_query)
print("THEN Clauses:")
print(then_clauses)