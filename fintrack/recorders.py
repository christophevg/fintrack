import os
import re

from dataclasses import dataclass, field, asdict
from collections import UserList

from datetime import datetime
from dateparser import parse
import humanize

import uuid
import bisect
import json

from tabulate import tabulate
from colorama import Fore, Style, init

import logging
logger = logging.getLogger(__name__)

# reset coloring in between prints
init(autoreset=True)

DATE_ORDER = os.environ.get("DATE_ORDER", "DMY")
if DATE_ORDER:
  logging.debug(f"using a date order {DATE_ORDER}")

DATE_LANG = os.environ.get("DATE_LANG", None)
if DATE_LANG:
  humanize.i18n.activate(DATE_LANG)
  logging.debug(f"using date language {DATE_LANG}")

DECIMAL_POINT = os.environ.get("DECIMAL_POINT", ",")

def now():
  return datetime.now() # wrapped to be able to monkeypatch it in tests

def uid():
  return str(uuid.uuid4()) # wrapped to be able to monkeypatch it in tests

def parse_amount(amount):
  # remove everything that shouldn't be in there
  if DECIMAL_POINT == ".":
    amount = re.sub("[^\d.-]","", amount)
  else:
    amount = re.sub(DECIMAL_POINT, ".", re.sub(f"[^\d{DECIMAL_POINT}-]","", amount))
  return float(amount)

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
    if amount or timestamp are a string, parse it
    """
    if isinstance(self.amount, str):
      self.amount = parse_amount(self.amount)
    if not isinstance(self.timestamp, datetime):
      self.timestamp = parse(self.timestamp, settings={"DATE_ORDER": DATE_ORDER})
  
  def __lt__(self, other):
    return self.timestamp < other.timestamp

  def __getitem__(self, key):
    """
    returns a property by name, as a basic type (datetime, uuid => str)
    """
    value = getattr(self, key)
    if key == "timestamp":
      return humanize.naturalday(value)
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

  def columns(self, with_balance=True):
    c = Record.columns.copy()
    if with_balance:
      c.insert(c.index("amount")+1, "balance")
    return c

  def rows(self, with_balance=True, with_color=True):

    def colorize(value):
      if not with_color:
        return value
      if value < 0:
        return Fore.RED + str(value) + Style.RESET_ALL
      return value

    balance = 0
    r = []
    for record in self:
      balance += record["amount"]
      r.append([
        colorize(balance) if column == "balance" else record[column]
        for column in self.columns(with_balance=with_balance)
      ])
    return r

  def show(self, with_balance=True):
    if not len(self):
      logger.warning("no records available")
      return
    return tabulate(
      self.rows(with_balance=with_balance),
      self.columns(with_balance=with_balance),
      tablefmt="grid"
    )

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
