from datetime import datetime

from utilities import check_queries_equivalent

from tests.fixtures.query_managers import TestQueryManager

DEFAULT_ID = 1
LIMIT = 10
OFFSET = 5
FLOAT_COL_CLAUSE = 10
START_DATE_CLAUSE = datetime(year=2000, month=1, day=1)
END_DATE_CLAUSE = datetime(year=2010, month=1, day=1)

SELECT_SIMPLE = f"""
SELECT test.bool_col, test.date_col, test.float_col, test.id
FROM test
LIMIT {LIMIT}
OFFSET {OFFSET}
"""

SELECT_WHERE = f"""
SELECT date_col, id, bool_col, float_col
FROM test
WHERE test.bool_col = false AND
test.float_col <= {FLOAT_COL_CLAUSE} AND
test.date_col BETWEEN '{START_DATE_CLAUSE}' AND '{END_DATE_CLAUSE}'
ORDER BY test.date_col DESC
"""

SELECT_JOIN = f"""
SELECT test.bool_col, test.date_col, test.float_col, test.id, child_test.string_col AS child_test_string_col, child_test.parent_id AS child_test_parent_id, child_test.id AS child_test_id
FROM test JOIN child_test ON test.id = child_test.parent_id
WHERE test.id = {DEFAULT_ID}
"""


async def test_select_limit_offset():
    query = TestQueryManager.select(limit=LIMIT, offset=OFFSET)
    compiled_query = TestQueryManager.convert_query_to_string(query)
    assert check_queries_equivalent(compiled_query, SELECT_SIMPLE)


async def test_select_where_order_by():
    query = TestQueryManager.select(
        columns=[
            "date_col",
            "id",
            "bool_col",
            "float_col",
        ],
        where={
            "bool_col": False,
            "float_col": ("le", FLOAT_COL_CLAUSE),
            "date_col": ("between", (START_DATE_CLAUSE, END_DATE_CLAUSE)),
        },
        order={"date_col": "desc"},
    )
    compiled_query = TestQueryManager.convert_query_to_string(query)
    assert check_queries_equivalent(compiled_query, SELECT_WHERE)


async def test_select_join():
    query = TestQueryManager.select(
        where={"id": DEFAULT_ID},
        join=["children"],
    )
    compiled_query = TestQueryManager.convert_query_to_string(query)
    assert check_queries_equivalent(compiled_query, SELECT_JOIN)
