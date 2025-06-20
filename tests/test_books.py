from fintrack.books   import Sheet, SheetExtract, CombinedSheet, PlannedSheet
from fintrack.records import Record
from fintrack.utils   import asrow

# Book

# TODO

# Sheet

def test_sheets_should_only_accept_correct_classes():
  class MyClass:
    pass

  try:
    Sheet(cls=MyClass).add(MyClass())
    assert False, "sheets should only accept Record-like types"
  except TypeError:
    pass

def test_sheets_should_only_accept_correct_arguments_to_create_instances():
  try:
    Sheet().add("blah")
    assert False, "sheets of Records shouldn't accept strings"
  except TypeError:
    pass

def test_taking_from_sheet():
  sheet = Sheet()
  sheet.add(-125, "test 1", timestamp="6/6")
  sheet.add(-125, "test 2", timestamp="7/6")
  sheet.add(-125, "test 3", timestamp="8/6")
  sheet.add(-125, "test 4", timestamp="9/6")
  sheet.add(-125, "test 5", timestamp="10/6")
  assert [record.description for record in sheet.take()] == [
    "test 1",
    "test 2",
    "test 3",
    "test 4",
    "test 5"
  ]
  assert [record.description for record in sheet.take(count=3)] == [
    "test 1",
    "test 2",
    "test 3"
  ]
  assert [record.description for record in sheet.take(start="8/6")] == [
    "test 3",
    "test 4",
    "test 5"
  ]
  assert [record.description for record in sheet.take(start="8/6", count=2)] == [
    "test 3",
    "test 4"
  ]
  assert [record.description for record in sheet.take(until="8/6")] == [
    "test 1",
    "test 2",
    "test 3"
  ]
  assert [record.description for record in sheet.take(start="7/6", until="9/6")] == [
    "test 2",
    "test 3",
    "test 4"
  ]

def test_sheet_extracts():
  sheet = Sheet()
  sheet.add(-125, "test 1", timestamp="6/6")
  sheet.add(-125, "test 2", timestamp="7/6")
  sheet.add(-125, "test 3", timestamp="8/6")
  sheet.add(-125, "test 4", timestamp="9/6")
  sheet.add(-125, "test 5", timestamp="10/6")
  extract = SheetExtract(sheet, count=2, start="7/6", until="9/6")
  assert extract.type is Record
  assert len(extract) == 2
  assert [ record.description for record in extract ] == [
    "test 2",
    "test 3"    
  ]

def test_combined_sheets():
  sheet1 = Sheet()
  sheet1.add(-125, "sheet 1 test 1", timestamp="6/6")
  sheet1.add(-125, "sheet 1 test 2", timestamp="7/6")
  sheet1.add(-125, "sheet 1 test 3", timestamp="8/6 12:00")
  sheet1.add(-125, "sheet 1 test 4", timestamp="9/6")
  sheet1.add(-125, "sheet 1 test 5", timestamp="10/6")

  sheet2 = Sheet()
  
  combined = CombinedSheet([
    SheetExtract(sheet1, start="8/6"),
    SheetExtract(sheet2, count=3)
  ])

  sheet2.add(-125, "sheet 2 test 1", timestamp="16/6")

  assert len(combined) == 4

  sheet2.add(-125, "sheet 2 test 2", timestamp="17/6")
  sheet2.add(-125, "sheet 2 test 3", timestamp="18/6")
  sheet2.add(-125, "sheet 2 test 4", timestamp="19/6")

  assert len(combined) == 6

  sheet2.add(-125, "sheet 2 test 5", timestamp="8/6 13:00")

  assert len(combined) == 6
  assert [ record.description for record in combined ] == [
    "sheet 1 test 3",
    "sheet 2 test 5",
    "sheet 1 test 4",
    "sheet 1 test 5",
    "sheet 2 test 1",
    "sheet 2 test 2"
  ]

def test_planned_sheet_taking():
  sheet = PlannedSheet()
  sheet.add(
    -125,
    "groceries",
    "every week on friday",
    "{plan.description} on {date}"
  )
  sheet.add(
    5,
    "savings",
    "every other day",
    "{plan.description} on {date}"
  )

  assert [ asrow(record) for record in sheet.take(8, start="7/1") ] == [
    ["Jan 09",    5, "savings",   "savings on Jan 09"  ],
    ["Jan 10", -125, "groceries", "groceries on Jan 10"],
    ["Jan 11",    5, "savings",   "savings on Jan 11"  ],
    ["Jan 13",    5, "savings",   "savings on Jan 13"  ],
    ["Jan 15",    5, "savings",   "savings on Jan 15"  ],
    ["Jan 17",    5, "savings",   "savings on Jan 17"  ],
    ["Jan 17", -125, "groceries", "groceries on Jan 17"],
    ["Jan 19",    5, "savings",   "savings on Jan 19"  ]
  ]
