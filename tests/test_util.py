from fintrack.util import Ordered

# Ordered

def test_ordered_list_only_accept_correct_objects():
  class MyClass:
    pass

  Ordered(MyClass).append(MyClass())

  try:
    Ordered(MyClass).append("blah")
    assert False, "ordered list of objects shouldn't accept strings"
  except TypeError:
    pass
