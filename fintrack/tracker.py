import sys

import logging

from fintrack            import __version__
from fintrack.books      import Book, Sheet
from fintrack.ui.tabular import Tabular, positive_green, negative_red

logger = logging.getLogger(__name__)

class Tracker:
  """
  Tracker is the front-end to the Book/Sheet modules. It is mainly focused on
  providing a Fire-friendly API.
  """
  def __init__(self, folder="~/.fintrack"):
    self._book  = Book(folder)
    self._sheet = None
    
  @property
  def version(self):
    """
    provide the version
    """
    return __version__
  
  @property
  def config(self):
    return self._book.config
  
  @property
  def current_sheet(self):
    """
    TODO this should go
    """
    if self._sheet:         # is we have a local sheet, return that
      return self._sheet
    return self._book.sheet # standard: return the book's active sheet
  
  def select(self, name):
    """
    sets the active sheet
    """
    self._book.sheet = name
    return self

  def future(self, until="next month"):
    """
    future generates records from the planned records
    TODO: generalize
    """
    self._sheet = Sheet()
    for plan in self._book._sheets["plans"]:
      self._sheet = self._sheet + Sheet(plan.take(until=until))
    return self

  @property
  def overview(self):
    """
    overview is a ready-made composite sheet of records and the future
    TODO: generalize
    """
    self._sheet = self._book._sheets["records"]
    for plan in self._book._sheets["plans"]:
      self._sheet = self._sheet + Sheet(plan.take(until="next month"))
    return self

  @property
  def balanced(self):
    """
    makes the balanced version of the current sheet active
    """
    self._sheet = self.book.sheet.balanced
    return self

  @property
  def table(self):
    """
    visualize the current sheet as a table
    """
    rules = {
      "amount" : [ positive_green, negative_red ],
      "balance": [ negative_red ]
    }
    return Tabular(self.current_sheet, colorize=rules)

  # storage

  def use(self, folder):
    self._book.folder = folder
    return self

  @property
  def using(self):
    return self._book.folder

  def save(self):
    self._book.save()
    return self

  # record management

  def add(self, *args, **kwargs):
    self._book.add(*args, **kwargs)

  def slurp(self, source=sys.stdin):
    self._book.slurp(source=source)

  # iterator support, making Tracker a list of what's on its current sheet

  def __iter__(self):
    return iter(self._book)

  def __len__(self):
    return len(self._book)

  def __getitem__(self, index):
    return self._book[index]
