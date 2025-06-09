from fintrack.ui.tabular import Tabular

def test_simple_table_of_dicts():
  rows = [
    { "a": 1, "b": 2 }, 
    { "a": 3, "b": 4 }, 
  ]
  table = Tabular(rows)
  assert table.columns == [ "a", "b" ]
  assert table.rows    == [ [1, 2], [3, 4] ]
  assert str(table)    == """+-----+-----+
|   a |   b |
+=====+=====+
|   1 |   2 |
+-----+-----+
|   3 |   4 |
+-----+-----+"""
