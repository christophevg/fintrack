from freezegun import freeze_time

from colorama import Fore, Style

from fintrack.books      import Sheet
from fintrack.ui.tabular import Tabular, positive_green, negative_red

import fintrack.utils

from unittest.mock import Mock

@freeze_time("Jan 14th, 2012", auto_tick_seconds=24*3600)
def test_basic_sheet_usage(monkeypatch):
  monkeypatch.setattr(fintrack.utils.uuid, "uuid4", Mock(side_effect=["uid1", "uid2"]))

  sheet = Sheet([
    { "amount": 1, "description": "test 1" }, 
    { "amount": 2, "description": "test 2" }, 
  ])
  assert str(Tabular(sheet)) == """+-------------+----------+---------------+-------+
| timestamp   |   amount | description   | uid   |
+=============+==========+===============+=======+
| Jan 14      |        1 | test 1        | uid1  |
+-------------+----------+---------------+-------+
| Jan 15      |        2 | test 2        | uid2  |
+-------------+----------+---------------+-------+"""

  assert str(Tabular(sheet.balanced)) == """+-------------+----------+-----------+---------------+-------+
| timestamp   |   amount |   balance | description   | uid   |
+=============+==========+===========+===============+=======+
| Jan 14      |        1 |         1 | test 1        | uid1  |
+-------------+----------+-----------+---------------+-------+
| Jan 15      |        2 |         3 | test 2        | uid2  |
+-------------+----------+-----------+---------------+-------+"""

@freeze_time("Jan 14th, 2012", auto_tick_seconds=24*3600)
def test_sheet_coloring(monkeypatch):
  monkeypatch.setattr(fintrack.utils.uuid, "uuid4", Mock(side_effect=["uid1", "uid2"]))

  sheet = Sheet([
    { "amount":   50, "description": "test 1" },
    { "amount": -100, "description": "test 2" },
  ])
  rules = {
    "amount" : [ positive_green, negative_red ],
    "balance": [ negative_red ]
  }
  assert str(Tabular(sheet, colorize=rules)) == f"""+-------------+----------+---------------+-------+
| timestamp   |   amount | description   | uid   |
+=============+==========+===============+=======+
| Jan 14      |       {Fore.GREEN}50{Style.RESET_ALL} | test 1        | uid1  |
+-------------+----------+---------------+-------+
| Jan 15      |     {Fore.RED}-100{Style.RESET_ALL} | test 2        | uid2  |
+-------------+----------+---------------+-------+"""

  assert str(Tabular(sheet.balanced, colorize=rules)) == f"""+-------------+----------+-----------+---------------+-------+
| timestamp   |   amount |   balance | description   | uid   |
+=============+==========+===========+===============+=======+
| Jan 14      |       {Fore.GREEN}50{Style.RESET_ALL} |        50 | test 1        | uid1  |
+-------------+----------+-----------+---------------+-------+
| Jan 15      |     {Fore.RED}-100{Style.RESET_ALL} |       {Fore.RED}-50{Style.RESET_ALL} | test 2        | uid2  |
+-------------+----------+-----------+---------------+-------+"""
