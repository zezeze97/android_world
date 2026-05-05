# Copyright 2026 The android_world Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility functions for interacting with SQLite database on an Android device."""

import os
import shutil
import sqlite3
import subprocess
import time
from typing import Optional, Type
from android_world.env import adb_utils
from android_world.env import interface
from android_world.task_evals.utils import sqlite_schema_utils
from android_world.utils import file_utils


def _find_external_sqlite() -> str:
  """Returns a sqlite3 binary that can handle Android app databases."""
  potential_paths = [
      os.path.expanduser('~/Library/Android/sdk/platform-tools/sqlite3'),
      os.path.expanduser('~/Android/Sdk/platform-tools/sqlite3'),
      shutil.which('sqlite3'),
  ]
  for path in potential_paths:
    if path and os.path.isfile(path):
      return path
  raise EnvironmentError(
      'sqlite3 with Android database support was not found. Please install'
      ' Android SDK platform-tools or put sqlite3 on PATH.'
  )


def _is_missing_fts4_error(error: sqlite3.OperationalError) -> bool:
  return 'no such module: fts4' in str(error).lower()


def _quote_sql_value(value: object) -> str:
  """Converts a Python value into a SQLite literal."""
  if value is None:
    return 'NULL'
  if isinstance(value, bool):
    return str(int(value))
  if isinstance(value, (int, float)):
    return str(value)
  if isinstance(value, bytes):
    return "X'" + value.hex() + "'"
  return "'" + str(value).replace("'", "''") + "'"


def _inline_sql_parameters(command: str, values: tuple[object, ...]) -> str:
  """Returns a SQL command with positional parameters inlined as literals."""
  parts = command.split('?')
  if len(parts) != len(values) + 1:
    raise ValueError('SQL command placeholder count does not match values.')
  result = []
  for part, value in zip(parts, values):
    result.append(part)
    result.append(_quote_sql_value(value))
  result.append(parts[-1])
  return ''.join(result)


def _execute_external_sqlite(
    db_path: str, commands: list[str], use_transaction: bool = True
) -> None:
  """Executes SQL with an external sqlite3 binary.

  Some Android app databases contain FTS4 virtual tables. The Python sqlite3
  build used by some conda environments does not include FTS4, while Android
  SDK platform-tools sqlite3 does.
  """
  sqlite_binary = _find_external_sqlite()
  script_lines = []
  if use_transaction:
    script_lines.extend(['PRAGMA foreign_keys = OFF;', 'BEGIN;'])
  script_lines.extend(command.rstrip(';') + ';' for command in commands)
  if use_transaction:
    script_lines.append('COMMIT;')
  subprocess.run(
      [sqlite_binary, db_path],
      input='\n'.join(script_lines) + '\n',
      text=True,
      capture_output=True,
      check=True,
  )


def execute_query(
    query: str, db_path: str, row_type: Type[sqlite_schema_utils.RowType]
) -> list[sqlite_schema_utils.RowType]:
  """Retrieves all rows from the given SQLite database path.

  Args:
    query: The query to issue.
    db_path: The path to the SQLite database file.
    row_type: The object type that will be created for each retrieved row.

  Returns:
      A list of tuples, each representing an row from the database.
  """
  conn = sqlite3.connect(db_path)
  conn.row_factory = sqlite3.Row
  cursor = conn.cursor()
  raw_rows = cursor.execute(query).fetchall()
  conn.close()

  rows = []
  for row in raw_rows:
    row = dict(row)
    rows.append(row_type(**row))  # pytype: disable=bad-return-type
  return rows


def get_rows_from_remote_device(
    table_name: str,
    remote_db_file_path: str,
    row_type: Type[sqlite_schema_utils.RowType],
    env: interface.AsyncEnv,
    timeout_sec: Optional[float] = None,
    n_retries: int = 3,
) -> list[sqlite_schema_utils.RowType]:
  """Retrieves rows from a table in a SQLite database located on a remote Android device.

  This function first copies the database from the remote device to a
  temporary local directory.

  Args:
    table_name: The name of the table from which to retrieve rows.
    remote_db_file_path: The database path on the remote device.
    row_type: The class type corresponding to the table's row structure. Each
      new database needs an equivalent python representation class type.
    env: The Android environment interface used for interacting with the remote
      device.
    timeout_sec: Optional timeout in seconds for the database copy operation.
    n_retries: The number of times to try. This is relevant in cases where a
      database has not been created/being created when an app is launched for
      the first time after clearing the database.

  Returns:
    All rows from the table.

  Raises:
    ValueError: If cannot query table.
  """
  with env.controller.pull_file(
      remote_db_file_path, timeout_sec
  ) as local_db_directory:
    local_db_path = file_utils.convert_to_posix_path(
        local_db_directory, os.path.split(remote_db_file_path)[1]
    )
    for _ in range(n_retries):
      try:
        return execute_query(
            f"SELECT * FROM {table_name};",
            local_db_path,
            row_type,
        )
      except sqlite3.OperationalError:
        time.sleep(1.0)
  raise ValueError(
      f"Failed to retrieve rows from {table_name} from"
      f" {remote_db_file_path} after {n_retries} retries. Try increasing the "
      "number of retries."
  )


def table_exists(
    table_name: str,
    remote_db_file_path: str,
    env: interface.AsyncEnv,
) -> bool:
  """Checks if a table exists in a SQLite database on a remote Android device.

  Args:
    table_name: The name of the table from which to retrieve rows.
    remote_db_file_path: The path to the sqlite database on the device.
    env: The environment.

  Returns:
    True if the table exists in the database.
  """
  try:
    get_rows_from_remote_device(
        table_name,
        remote_db_file_path,
        sqlite_schema_utils.GenericRow,
        env,
    )
    return True
  except (FileNotFoundError, ValueError):
    return False


def delete_all_rows_from_table(
    table_name: str,
    remote_db_file_path: str,
    env: interface.AsyncEnv,
    app_name: str,
    timeout_sec: Optional[float] = None,
) -> None:
  """Deletes all rows from a specified table in a SQLite database on a remote Android device.

  Args:
    table_name: Deletes all rows from the table.
    remote_db_file_path: The path to the sqlite database on the device.
    env: The environment.
    app_name: The name of the app that owns the database.
    timeout_sec: Timeout in seconds.
  """
  if not table_exists(table_name, remote_db_file_path, env):
    # If the database was never created, opening the app may create it.
    adb_utils.launch_app(app_name, env.controller)
    time.sleep(7.0)

  with env.controller.pull_file(
      remote_db_file_path, timeout_sec
  ) as local_db_directory:
    local_db_path = file_utils.convert_to_posix_path(
        local_db_directory, os.path.split(remote_db_file_path)[1]
    )

    conn = sqlite3.connect(local_db_path)
    cursor = conn.cursor()
    delete_command = f"DELETE FROM {table_name}"
    try:
      cursor.execute(delete_command)
      conn.commit()
    except sqlite3.OperationalError as e:
      conn.rollback()
      conn.close()
      if not _is_missing_fts4_error(e):
        raise
      _execute_external_sqlite(local_db_path, [delete_command])
    else:
      conn.close()
    env.controller.push_file(local_db_path, remote_db_file_path, timeout_sec)
    adb_utils.close_app(
        app_name, env.controller
    )  # Close app to register the changes.


def insert_rows_to_remote_db(
    rows: list[sqlite_schema_utils.RowType],
    exclude_key: str | None,
    table_name: str,
    remote_db_file_path: str,
    app_name: str,
    env: interface.AsyncEnv,
    timeout_sec: Optional[float] = None,
) -> None:
  """Inserts rows into a SQLite database located on a remote Android device.

  Args:
    rows: The rows to insert into the remote database.
    exclude_key: Name of field to exclude adding to database. Typically an auto
      incrementing key.
    table_name: The name of the table to insert rows into.
    remote_db_file_path: Location of the SQLite database to insert rows into.
    app_name: The name of the app that owns the database.
    env: The environment.
    timeout_sec: Optional timeout in seconds for the database copy operation.
  """
  with env.controller.pull_file(
      remote_db_file_path, timeout_sec
  ) as local_db_directory:
    local_db_path = file_utils.convert_to_posix_path(
        local_db_directory, os.path.split(remote_db_file_path)[1]
    )

    conn = sqlite3.connect(local_db_path)
    cursor = conn.cursor()
    insert_commands = []
    for index, row in enumerate(rows):
      insert_command, values = sqlite_schema_utils.insert_into_db(
          row, table_name, exclude_key
      )
      insert_commands.append(_inline_sql_parameters(insert_command, values))
      try:
        cursor.execute(insert_command, values)
      except sqlite3.OperationalError as e:
        conn.rollback()
        conn.close()
        if not _is_missing_fts4_error(e):
          raise
        for remaining_row in rows[index + 1 :]:
          insert_command, values = sqlite_schema_utils.insert_into_db(
              remaining_row, table_name, exclude_key
          )
          insert_commands.append(
              _inline_sql_parameters(insert_command, values)
          )
        _execute_external_sqlite(local_db_path, insert_commands)
        break
    else:
      conn.commit()
      conn.close()

    env.controller.push_file(local_db_path, remote_db_file_path, timeout_sec)
    adb_utils.close_app(app_name, env.controller)
