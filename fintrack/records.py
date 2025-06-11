from dataclasses import dataclass, field

from datetime import datetime
import uuid
from decimal import Decimal, getcontext
import humanize

from fintrack.utils import now, uid, parse_amount, parse_datetime

import logging
logger = logging.getLogger(__name__)

getcontext().prec = 2

@dataclass
class RecordLike:
  """
  represents some financial transaction, consisting of an amount and
  description
  """
  amount      : Decimal
  description : str

@dataclass
class Record(RecordLike):
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
  columns = ( "timestamp", "amount", "description", "uid" )
  
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
  
  def __repr__(self):
    return f"record for {self.amount} {humanize.naturalday(self.timestamp)} {self.description}"
  
  def __lt__(self, other):
    return self.timestamp < other.timestamp
