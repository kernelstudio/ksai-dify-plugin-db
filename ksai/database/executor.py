# coding=utf-8
# -*- coding: UTF-8 -*-
#
# This file is part of the kernelstudio package.
#
# (c) 2014-2025 zlin <admin@kernelstudio.com>
#
# For the full copyright and license information, please view the LICENSE file
# that was distributed with this source code.
import datetime
import logging
import typing as t
from urllib import parse
from uuid import UUID

import pandas as pd
from sqlalchemy import create_engine

from ksai.utils.sqls import is_single_select_query
from ksai.utils.strings import has_text

driver_mapping = {
    "postgresql": "postgresql+psycopg2",
    "mysql": "mysql+pymysql",
    "oracle": "oracle+oracledb",
    "mssql": "mssql+pymssql",
}


class DatabaseConfig:

    def __init__(self,
                 database_type: t.Optional[str],
                 host: t.Optional[str],
                 port: t.Optional[int],
                 database: t.Optional[str],
                 username: t.Optional[str],
                 password: t.Optional[str],
                 properties: t.Optional[str] = None
                 ):
        self.database_type = database_type
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.properties = properties

    @staticmethod
    def from_dict(config: dict):
        return DatabaseConfig(
            config.get("type"),
            config.get("host"),
            config.get("port"),
            config.get("database"),
            config.get("username"),
            config.get("password"),
            config.get("properties")
        )

    @property
    def engine(self):
        return create_engine(self.url, pool_size=100, pool_recycle=36)

    @property
    def driver(self):
        return driver_mapping[self.database_type]

    @property
    def url(self):
        parsed_username = parse.quote_plus(self.username)
        parsed_password = parse.quote_plus(self.password)
        parsed_host = parse.quote_plus(self.host)
        url = f"{self.driver}://{parsed_username}:{parsed_password}@{parsed_host}"

        if has_text(str(self.port)):
            url = f"{url}:{str(self.port)}"
        url = f"{url}/"

        if has_text(self.database):
            parsed_database = parse.quote_plus(self.database)
            url = f"{url}{parsed_database}"

        if has_text(self.properties):
            url = f"{url}?{self.properties}"
        logging.info(f"Database URL: {url}")

        return url


class DatabaseExecutor:

    def __init__(self, config: DatabaseConfig):
        self.config = config

    @staticmethod
    def create_from_config(config: dict):
        return DatabaseExecutor(DatabaseConfig.from_dict(config))

    def test_connection(self):
        try:
            connection = self.config.engine.connect()
            connection.close()
            return True
        except Exception as e:
            raise ValueError(f"Could not connect to database: {e}")

    def select(self, sql: str, placeholder: str = '-', date_format='%Y-%m-%d %H:%M:%S'):

        if is_single_select_query(sql) is False:
            raise ValueError(f"'{sql}' is not a single SELECT query.")

        if has_text(placeholder) is False:
            placeholder = '-'

        if has_text(date_format) is False:
            date_format = '%Y-%m-%d %H:%M:%S'

        query_sql = sql.replace('%', '%%')

        df = pd.read_sql_query(sql=query_sql, con=self.engine, parse_dates=date_format)
        df = df.fillna(placeholder)

        results = []
        if len(df) > 0:
            results = df.to_dict(orient="records")
        for result in results:
            for key in result:
                if type(result[key]) is pd.Timestamp:
                    result[key] = result[key].strftime(date_format)
                    continue
                if type(result[key]) is datetime.date:
                    result[key] = result[key].strftime('%Y-%m-%d')
                    continue
                if type(result[key]) is UUID:
                    result[key] = str(result[key])
                    continue

        return results
