import os

from pathlib import Path

import yaml
import json
import uuid

from fintrack.tracker import Tracker, __version__
from fintrack.recorders import Record, RecordDecoder

def test_version():
  assert Tracker().version() == __version__

def test_init_and_using():
  assert Tracker().using == Path("~/.fintrack").expanduser()
  assert Tracker(folder="testing").using == Path().cwd() / "testing"
  assert Tracker(folder="/testing").using == Path("/testing")
  assert Tracker(folder="~/testing").using == Path("~/testing").expanduser()
  user = os.getlogin()
  assert Tracker(folder=f"~{user}/testing").using == Path(f"~{user}/testing").expanduser()

def test_use_and_using():
  assert Tracker().use("testing").using == Path().cwd() / "testing"
  assert Tracker().use("/testing").using == Path("/testing")
  assert Tracker().use("~/testing").using == Path("~/testing").expanduser()
  user = os.getlogin()
  assert Tracker().use(f"~{user}/testing").using == Path(f"~{user}/testing").expanduser()

def test_config():
  assert Tracker().config == { "version" : __version__ }

def test_record(tmp_path):
  tracker = Tracker(folder=tmp_path)
  tracker.record(-125, "test 1")
  tracker.record(+125, "test 2")
  tracker.record(+125, "test 3")
  assert [ record.description for record in tracker] == [ "test 1", "test 2", "test 3" ]

def test_save(tmp_path):
  tracker = Tracker(folder=tmp_path)
  tracker.record(-125, "test 1", timestamp="6/7", uid="test1")
  tracker.record(+125, "test 2", timestamp="7/7", uid="test2")
  uid3 = uuid.uuid4()
  tracker.record(-250, "test 3", timestamp="8/7", uid=uid3)
  tracker.save()

  with (tmp_path / "config.yaml").open() as fp:
    config = yaml.safe_load(fp)
  assert config == { "version" : __version__ }

  with (tmp_path / "records.json").open() as fp:
    records = json.load(fp, cls=RecordDecoder)

  assert len(records) == 3
  assert all([ isinstance(record, Record) for record in records ])
  assert records[0].amount      == -125
  assert records[1].description == "test 2"
  assert records[2].uid         == uid3

def test_load(tmp_path):
  with (tmp_path / "config.yaml").open("w") as fp:
    yaml.safe_dump({ "version" : __version__ }, fp)
  with (tmp_path / "records.json").open("w") as fp:
    json.dump([
      { "amount": -125, "description": "test load" }
    ], fp)
  
  tracker = Tracker(folder=tmp_path)
  assert len(tracker) == 1
  assert tracker[0].amount == -125 
  assert tracker[0].description == "test load"

  