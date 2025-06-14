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
  records = plan.take(3, start=datetime(2025, 1, 6))
  assert [ asrow(record) for record in records ] == [
    ["Jan 10", -125, "groceries", "groceries on Jan 10"],
    ["Jan 24", -125, "groceries", "groceries on Jan 24"],
    ["Feb 07", -125, "groceries", "groceries on Feb 07"]
  ]
