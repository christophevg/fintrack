from fintrack.records import Record
from fintrack.books import Sheet

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
    Sheet(Record).add("blah")
    assert False, "sheets of Records shouldn't accept strings"
  except TypeError:
    pass
