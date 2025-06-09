from dataclasses import dataclass, field

from datetime import datetime
import uuid
from decimal import Decimal, getcontext
import operator

from fintrack.util import now, uid, parse_amount, parse_datetime

import logging
logger = logging.getLogger(__name__)

getcontext().prec = 2

@dataclass
class Record:
  """
  represents some financial transaction, consisting of an amount and
  description, with timestamp and unique identifier, defaulting to now and a
  random uuid
  """
  amount      : Decimal
  description : str

  # optional
  timestamp   : datetime = field(default_factory=now)
  uid         : str      = field(default_factory=uid)
  
  # exposed columns in prefered presentation order
  columns = [ "timestamp", "amount", "description", "uid" ]
  
  def __post_init__(self):
    """
    if amount or timestamp are a string, parse it, default uid
    """
    if not isinstance(self.amount, Decimal):
      self.amount = parse_amount(self.amount)
    if not isinstance(self.timestamp, datetime):
      self.timestamp = parse_datetime(self.timestamp)
    if self.uid is None:
      self.uid = uid()
    if isinstance(self.uid, uuid.UUID):
      self.uid = str(self.uid)
  
  def __lt__(self, other):
    return self.timestamp < other.timestamp

def running(rows, source, method=operator.add):
  """
  takes a list of rows, adding a running value based on a source property and a
  method to compute that running value
  """
  value = 0
  index = Record.columns.index(source)
  new_rows = []
  for row in rows:
    extended_row = row.copy()
    value = method(value , extended_row[index])
    extended_row.insert(index+1, value)
    new_rows.append(extended_row)
  return new_rows

def balanced(rows, headers=False):
  if headers:
    rows.insert(Record.columns.index("amount")+1, "balance")
    return rows
  return running(rows, "amount")
