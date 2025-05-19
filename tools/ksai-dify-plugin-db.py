# coding=utf-8
# -*- coding: UTF-8 -*-
#
# This file is part of the kernelstudio package.
#
# (c) 2014-2025 zlin <admin@kernelstudio.com>
#
# For the full copyright and license information, please view the LICENSE file
# that was distributed with this source code.
import json
import logging
from collections.abc import Generator
from typing import Any

import pandas as pd
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ksai.database.executor import driver_mapping, DatabaseExecutor
from ksai.utils.sqls import is_validate_sql
from ksai.utils.strings import has_text


def _validate_parameters(parameters: dict[str, Any]) -> None:
    for param in ['type', 'port', 'username', 'password', 'database', 'sql']:
        if param not in parameters or has_text(parameters.get(param, "")) is False:
            raise ValueError(f"Parameter {param} is required")

    database_type = parameters.get('type')
    if has_text(driver_mapping.get(database_type)) is False:
        raise ValueError(f"Database type {database_type} is not supported")


class KsaiDifyPluginDbTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        _validate_parameters(tool_parameters)

        sql = tool_parameters.get('sql')
        if is_validate_sql(sql) is False:
            raise ValueError(f"Invalid sql: {sql}")

        date_format = tool_parameters.get('date_format')
        placeholder = tool_parameters.get('placeholder')

        try:
            executor = DatabaseExecutor.create_from_config(tool_parameters)
        except Exception as e:
            message = "Creation database connection exception."
            logging.exception(message)
            raise Exception(message + " {}".format(e))

        try:
            results = executor.select(sql, placeholder, date_format)
        except Exception as e:
            message = "Execute SQL execution exception."
            logging.exception(message)
            raise Exception(message + " {}".format(e))

        output_format = tool_parameters.get('output_format')
        if results is None or len(results) == 0:
            results = []

        if "markdown" == output_format:
            df = pd.DataFrame(results)
            yield self.create_text_message(df.to_markdown(index=False))
        elif "json_string" == output_format:
            yield self.create_text_message(json.dumps(results, ensure_ascii=False))
        else:
            yield self.create_json_message({'results': results})
