from datetime import datetime

from fintrack.plans import PlannedRecord

def test_fixed_timestamp_plan():
  plan = PlannedRecord(
    -125,
    "groceries",
    "every other week on friday",
    "{plan.description} on {date}"
  )
  records = plan.take(3, start=datetime(2025, 6, 9))
  assert records.rows(with_balance=False, with_color=False) == [
    ['Jun 13', -125, 'groceries', 'groceries on Jun 13'],
    ['Jun 27', -125, 'groceries', 'groceries on Jun 27'],
    ['Jul 11', -125, 'groceries', 'groceries on Jul 11']
  ]
