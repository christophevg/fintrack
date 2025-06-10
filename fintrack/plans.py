from dataclasses import dataclass, field

from recurrent.event_parser import RecurringEvent
from datetime import datetime
from dateutil.rrule import rrulestr

from humanize import naturalday

from decimal import Decimal, getcontext

from fintrack.records import Record
from fintrack.util    import now, uid, parse_amount, parse_datetime

import logging
logger = logging.getLogger(__name__)

getcontext().prec = 2

@dataclass
class PlannedRecord:
  """
  represents a plannen record and generates Records according to a schedule
  """
  amount      : Decimal
  description : str
  schedule    : str

  # optional
  uids        : str = None
  uid         : str = field(default_factory=uid)
  
  columns = [ "schedule", "amount", "description", "uids", "uid" ]
    
  def __post_init__(self):
    """
    if amount is a string, parse it, ensure the schedule is valid
    """
    if not isinstance(self.amount, Decimal):
      self.amount = parse_amount(self.amount)
    # ensure the schedule is valid
    if RecurringEvent().parse(self.schedule) is None:
      raise ValueError("schedule is invalid")

  def __repr__(self):
    return f"plan for {self.amount} {self.schedule} {self.description}"

  @property
  def next_occurrence(self):
    return self.take(1)[0]
  
  def __lt__(self, other):
    return self.next_occurrence.timestamp < other.next_occurrence.timestamp
    
  def occurrence(self, on_date, index):
    args = [ self.amount, self.description, on_date ]
    if self.uids:
      args.append(self.uids.format(plan=self, index=index, date=naturalday(on_date)))
    return Record(*args)

  def take(self, count=None, until=None, start=None):
    """
    starting from start, or now if omitted, generates up to count Records and
    returns them as Records
    """
    if start is None:
      start = now()

    if until and not isinstance(until, datetime):
      until = parse_datetime(until)

    r = RecurringEvent()
    event = r.parse(self.schedule)
    if r.is_recurring:
      if until:
        dates = rrulestr(event).between(after=start, before=until, count=count)        
      elif count:
        dates = rrulestr(event).xafter(start, count=count)
      return [ self.occurrence(dt, index) for index, dt in enumerate(dates) ]
    elif isinstance(event, datetime):
      if start and event < start:
        return []
      if until and event > until:
        return []
      return [ Record(self.amount, self.description, event, self.uid) ]
    elif event is None:
      raise ValueError("schedule is invalid")
