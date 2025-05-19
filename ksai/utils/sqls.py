# coding=utf-8
# -*- coding: UTF-8 -*-
#
# This file is part of the kernelstudio package.
#
# (c) 2014-2025 zlin <admin@kernelstudio.com>
#
# For the full copyright and license information, please view the LICENSE file
# that was distributed with this source code.

import sqlparse
from sqlglot import parse

from ksai.utils.strings import has_text


def parse_sql(sql: str) -> tuple | None:
    if sql is None:
        return None
    return sqlparse.parse(sql)


def is_select_statement(statement) -> bool:
    return statement is not None and 'SELECT' == statement.get_type().upper()


def is_single_select_query(sql: str) -> bool:
    statements = sqlparse.parse(sql)
    if statements is not None:
        return len(statements) == 1 and is_select_statement(statements[0])
    return False


def is_validate_sql(sql: str) -> bool:
    if has_text(sql) is False:
        return False
    try:
        parse(sql)
        return True
    except Exception as e:
        print(f"Exception while parsing sql: {e}")
        return False
