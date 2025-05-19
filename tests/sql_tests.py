# coding=utf-8
# -*- coding: UTF-8 -*-
#
# This file is part of the kernelstudio package.
#
# (c) 2014-2025 zlin <admin@kernelstudio.com>
#
# For the full copyright and license information, please view the LICENSE file
# that was distributed with this source code.
import pandas as pd

from ksai.database.executor import DatabaseConfig, DatabaseExecutor
from ksai.utils.sqls import is_validate_sql

config = DatabaseConfig(
    'mysql',
    '127.0.0.1',
    3306,
    'ksai',
    'root',
    'admin'
)

executor = DatabaseExecutor(config)

results = executor.select(
    "select id,true_name,created_at from ks_user LIMIT 3;",
    date_format='%Y年-%m月-%d日 %H时:%M分:%S秒')

df = pd.DataFrame(results)

print(df.to_markdown(index=False))

sqls = [
    "select id,true_name,created_at from ks_user LIMIT 3;",
    "selectid,true_name,created_at from ks_user LIMIT 3;",
]

for sql in sqls:
    print(is_validate_sql(sql))
