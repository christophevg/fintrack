from dataclasses import dataclass, field

from recurrent.event_parser import RecurringEvent
from datetime import datetime
from dateutil import rrule

import humanize

import uuid

from fintrack.records import Record, Records
from fintrack.util    import now, uid, parse_amount

import logging
logger = logging.getLogger(__name__)

@dataclass
class PlannedRecord:
  """
  represents a plannen record and generates Records according to a schedule
  """
  amount      : float
  description : str
  schedule    : str
  # optional
  uids        : str = None
  uid         : uuid.UUID = field(default_factory=uid)
    
  def __post_init__(self):
    """
    if amount or schedule are a string, parse it
    """
    if isinstance(self.amount, str):
      self.amount = parse_amount(self.amount)
    # ensure the schedule is valid
    if RecurringEvent().parse(self.schedule) is None:
      raise ValueError("schedule is invalid")
  
  def take(self, count, start=None):
    """
    starting from start, or now if omitted, generates up to count Records and
    returns them as Records
    """
    if start is None:
      start = now()

    r = RecurringEvent()
    event = r.parse(self.schedule)
    if r.is_recurring:
      return Records([
        Record(
          self.amount, self.description, dt,
          self.uids.format(plan=self, index=index, date=humanize.naturalday(dt)) if self.uids else None
        )
        for index, dt in enumerate(rrule.rrulestr(event).xafter(start, count=count))
      ])
    elif isinstance(event, datetime):
      return Records([Record(self.amount, self.description, event, self.uid)])
    elif event is None:
      raise ValueError("schedule is invalid")
