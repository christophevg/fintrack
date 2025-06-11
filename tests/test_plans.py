from datetime import datetime

from fintrack.plans import PlannedRecord
from fintrack.utils import asrow

def test_fixed_timestamp_plan():
  plan = PlannedRecord(
    -125,
    "groceries",
    "every other week on friday",
    "{plan.description} on {date}"
  )
  records = plan.take(3, start=datetime(2025, 6, 9))
  assert [ asrow(record) for record in records ] == [
    ['Jun 13', -125, 'groceries', 'groceries on Jun 13'],
    ['Jun 27', -125, 'groceries', 'groceries on Jun 27'],
    ['Jul 11', -125, 'groceries', 'groceries on Jul 11']
  ]
