import os

from dataclasses import dataclass, field, asdict
from collections import UserList

from datetime import datetime
from dateutil.parser import parse

import uuid
import bisect
import json

from tabulate import tabulate

import logging
logger = logging.getLogger(__name__)

DAY_FIRST = os.environ.get("DAY_FIRST", "yes").lower() in [ "yes", "true" ]
if DAY_FIRST:
  logging.debug("using a day-first approach")

def now():
  return datetime.now() # wrapped to be able to monkeypatch it in tests

def uid():
  return str(uuid.uuid4()) # wrapped to be able to monkeypatch it in tests

@dataclass
class Record:
  """
  keeps and an amount and description, with timestamp and unique identifier,
  defaulting to now and a random uuid
  """
  amount      : float
  description : str
  # optional
  timestamp   : datetime  = field(default_factory=now)
  uid         : uuid.UUID = field(default_factory=uid)
  
  columns = [ "timestamp", "amount", "description", "uid" ]
  
  def __post_init__(self):
    """
    is timestamp is a string, parse it
    """
    if not isinstance(self.timestamp, datetime):
      self.timestamp = parse(self.timestamp, dayfirst=DAY_FIRST)
  
  def __lt__(self, other):
    return self.timestamp < other.timestamp

  def __getitem__(self, key):
    """
    returns a property by name, as a basic type (datetime, uuid => str)
    """
    value = getattr(self, key)
    if key == "timestamp":
      return value.isoformat()
    if key == "uid":
      return str(value)
    return value

class Records(UserList):
  """
  a list of Record objects (only), kept sorted on append including when combined
  """
  def __iter__(self):
    for record in self.data:
      yield record

  def append(self, record):
    if not isinstance(record, Record):
      raise TypeError("Records can only append Record objects")
    bisect.insort(self.data, record)

  def extend(self, other):
    for record in other:
      self.append(record)

  def __add__(self, other):
    new = self.copy()
    new.extend(other)
    return new

  def show(self):
    if not len(self):
      logger.warning("no records available")
      return
    return tabulate([
      [ record[column] for column in Record.columns ]
      for record in self
    ], Record.columns, tablefmt="grid")

class RecordEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Records):
      return list(obj)
    if isinstance(obj, Record):
      return asdict(obj)
    if isinstance(obj, datetime):
      return obj.isoformat()
    if isinstance(obj, uuid.UUID):
      return str(obj)
    return super().default(obj)

class RecordDecoder(json.JSONDecoder):
  def __init__(self, *args, **kwargs):
    super().__init__(object_hook=self.object_hook, *args, **kwargs)

  def object_hook(self, dct):
    try:
      dct["timestamp"] = datetime.fromisoformat(dct["timestamp"])
    except KeyError:
      pass
    try:
      dct["uid"] = uuid.UUID(dct["uid"])
    except (KeyError, ValueError):
      pass
    return Record(**dct)
