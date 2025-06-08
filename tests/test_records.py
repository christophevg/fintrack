from freezegun import freeze_time
from datetime import datetime

import re

import json

from fintrack.recorders import Record, Records, RecordEncoder
import fintrack.recorders

def test_record_with_provided_timestamp():
  ts = datetime.now()
  assert Record(-125, "test record", timestamp=ts).timestamp == ts

@freeze_time("Jan 14th, 2012")
def test_record_with_default_timestamp():
  assert Record(-125, "test record").timestamp == datetime.now()

def test_record_with_provided_uid():
  assert Record(-125, "test record", uid="123").uid == "123"

def test_record_with_default_uid(monkeypatch):
  monkeypatch.setattr(fintrack.recorders.uuid, "uuid4", lambda: "456")
  assert Record(-125, "test record").uid == "456"

def test_record_timestamp_parsing():
  ts = datetime(2019, 6, 7)
  assert Record(-125, "test record", timestamp="2019-07-06").timestamp == ts
  assert Record(-125, "test record", timestamp="7/6/19").timestamp == ts
  ts = datetime(datetime.now().year, 6, 7)
  assert Record(-125, "test record", timestamp="7/6").timestamp == ts

def test_ordered_records():
  records = Records()
  assert list(records) == []

  record1 = Record(+125, "test record 1", timestamp="6/6")
  record2 = Record(-125, "test record 2", timestamp="7/6 12:00")
  record3 = Record(-125, "test record 3", timestamp="7/6 13:00")
  
  records.append(record2)
  records.append(record3)
  records.append(record1)

  assert list(records) == [ record1, record2, record3 ]

def test_combining_records():
  records1 = Records()
  records2 = Records()
  records3 = Records()

  records = [
    Record(+125, "test record 1", timestamp="6/6"),
    Record(-125, "test record 2", timestamp="7/6 12:00"),
    Record(-125, "test record 3", timestamp="7/6 13:00"),
    Record(-125, "test record 4", timestamp="8/6 12:00"),
    Record(-125, "test record 5", timestamp="8/6 13:00"),
    Record(-125, "test record 6", timestamp="9/6")
  ]
  
  records1.append(records[5])
  records1.append(records[0])
  records2.append(records[4])
  records3.append(records[1])
  records3.append(records[3])
  records3.append(records[2])

  assert list(records1 + records2 + records3 ) == records

def test_records_only_accept_record_objects():
  try:
    Records().append("blah")
    assert False, "records shouldn't accept strings"
  except TypeError:
    pass

def test_records_tabulation():
  assert Records().show() is None
  records = Records([
    Record(+125, "test record 1", timestamp="6/6",       uid="1"),
    Record(-125, "test record 2", timestamp="7/6 12:00", uid="2"),
    Record(-125, "test record 3", timestamp="7/6 13:00", uid="3")
  ])
  assert records.show(with_balance=False) == """+-------------+----------+---------------+-------+
| timestamp   |   amount | description   |   uid |
+=============+==========+===============+=======+
| Jun 06      |      125 | test record 1 |     1 |
+-------------+----------+---------------+-------+
| yesterday   |     -125 | test record 2 |     2 |
+-------------+----------+---------------+-------+
| yesterday   |     -125 | test record 3 |     3 |
+-------------+----------+---------------+-------+"""
  ansi = r'\x1b\[[\d;]+m'
  table = re.sub(ansi,"", records.show())
  assert table == """+-------------+----------+-----------+---------------+-------+
| timestamp   |   amount |   balance | description   |   uid |
+=============+==========+===========+===============+=======+
| Jun 06      |      125 |       125 | test record 1 |     1 |
+-------------+----------+-----------+---------------+-------+
| yesterday   |     -125 |         0 | test record 2 |     2 |
+-------------+----------+-----------+---------------+-------+
| yesterday   |     -125 |      -125 | test record 3 |     3 |
+-------------+----------+-----------+---------------+-------+"""

def test_recordencoder():
  try:
    json.dumps([{"a:" : object() }], cls=RecordEncoder, indent=2)
    assert False, "expected encoder to fail on non-Record objecttype"
  except TypeError:
    pass
  