from freezegun import freeze_time
from datetime import datetime

import json

from fintrack.records import Record
from fintrack.util    import ClassEncoder
import fintrack.util

def test_record_with_provided_timestamp():
  ts = datetime.now()
  assert Record(-125, "test record", timestamp=ts).timestamp == ts

@freeze_time("Jan 14th, 2012")
def test_record_with_default_timestamp():
  assert Record(-125, "test record").timestamp == datetime.now()

def test_record_with_provided_uid():
  assert Record(-125, "test record", uid="123").uid == "123"

def test_record_with_default_uid(monkeypatch):
  monkeypatch.setattr(fintrack.util.uuid, "uuid4", lambda: "456")
  assert Record(-125, "test record").uid == "456"

def test_record_timestamp_parsing():
  ts = datetime(2019, 6, 7)
  assert Record(-125, "test record", timestamp="2019-07-06").timestamp == ts
  assert Record(-125, "test record", timestamp="7/6/19").timestamp == ts
  ts = datetime(datetime.now().year, 6, 7)
  assert Record(-125, "test record", timestamp="7/6").timestamp == ts

def test_records_order():
  r1 = Record(+125, "test record 1", timestamp="6/6")
  r2 = Record(-125, "test record 2", timestamp="7/6 12:00")
  r3 = Record(-125, "test record 3", timestamp="7/6 13:00")
  r4 = Record(-125, "test record 4", timestamp="8/6 12:00")
  r5 = Record(-125, "test record 5", timestamp="8/6 13:00")
  r6 = Record(-125, "test record 6", timestamp="9/6")

  assert r1 < r2 < r3 < r4 < r5 < r6

def test_recordencoder():
  try:
    json.dumps([{"a:" : object() }], cls=ClassEncoder, indent=2)
    assert False, "expected encoder to fail on non-Record objecttype"
  except TypeError:
    pass
