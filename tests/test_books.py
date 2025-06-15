from fintrack.books import Sheet

# Book

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
