from freezegun import freeze_time

from fintrack.books      import Sheet
from fintrack.ui.tabular import Tabular

import fintrack.utils

from unittest.mock import Mock

@freeze_time("Jan 14th, 2012", auto_tick_seconds=24*3600)
def test_basic_sheet(monkeypatch):
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
