from sortedcontainers import SortedList

from fintrack.records import RecordLike, Record
from fintrack.utils   import asrow

class BalancedSheet:
  """
  wraps a sheet overriding rows and columns properties to include a balance
  """
  def __init__(self, sheet):
    self._sheet = sheet
    self._amount_index = sheet.columns.index("amount")
  
  def __getattr__(self, attr):
    """
    proxy all not-overridden attrs
    """
    return getattr(self._sheet, attr)

  @property
  def columns(self):
    """
    returns columns with additional balance column after the amount column
    """
    cols = list(self._sheet.columns)
    cols.insert(self._amount_index+1, "balance")
    return tuple(cols)
  
  @property
  def rows(self):
    """
    returns rows with additional balance column after the amount column
    """
    balance = 0
    for row in self._sheet.rows:
      balance += row[self._amount_index]
      row.insert(self._amount_index+1, balance)
      yield row

class Sheet:
  """
  a sheet maintains a sorted collection of <records> of <type> (default:Record)
  """

  def __init__(self, records=None, cls=Record, book=None):
    if not issubclass(cls, RecordLike):
      raise TypeError("sheets can only handle Record-like types")
    self._type    = cls
    self._book    = book
    self._records = SortedList()
    if records:
      self.update(records)
    self.balanced = BalancedSheet(self)
  
  @property
  def type(self):
    return self._type
  
  def add(self, *args, **kwargs):
    """
    add accepts a record of the correct type for this sheet, or a dict with the
    arguments to construct one, or the actual arguments to construct one
    e.g. sheet = Sheet(Record)
         sheet.add(Record(-125, "test"))
         sheet.add(-125, "test")
    """
    if len(args) == 1 and isinstance(args[0], self._type):
      record = args[0]
    elif len(args) == 1 and isinstance(args[0], dict):
      record = self._type(**args[0])
    else:
      record = self._type(*args, **kwargs)
    self._records.add(record)
    return record
  
  @property
  def columns(self):
    return self.type.columns

  @property
  def rows(self):
    """
    alternative iterator, providing records as lists of their properties 
    """
    for record in self:
      yield asrow(record)

  def update(self, other):
    for obj in other:
      self.add(obj)

  def __add__(self, other):
    """
    constructs a new sheet with own and other sheet's records
    """
    new = self.__class__(self, cls=self.type)
    new.update(other)
    return new

  def __iter__(self):
    for record in self._records:
      yield record

  def __len__(self):
    return len(self._records)

  def __getitem__(self, index):
    return self._records[index]
