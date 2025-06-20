import sys

from dataclasses import dataclass

from pathlib import Path

import yaml
import json

from datetime import datetime

from sortedcontainers import SortedList

from slugify import slugify

from fintrack.records import Record
from fintrack.plans   import PlannedRecord
from fintrack.utils   import asrow, ClassEncoder, ClassDecoder, parse_datetime
from fintrack.utils   import all_subclasses

import logging
logger = logging.getLogger(__name__)

DEFAULT_SHEETS = {
  "records" : "Sheet",
  "plans"   : "PlannedSheet"
}
DEFAULT_SHEET = "records"

class Book:
  """
  Following the analogy of a spreadsheet, a Book consists of several named
  sheets and provides access to them, along with persistence.
  """
  
  def __init__(self, folder="~/.fintrack"):
    self._sheets = {}     # all sheets by name: name -> sheet 

    self._sheet  = None   # currently active sheet
    self._folder = None   # storage location

    self.folder  = folder # set the folder, using the setter, to trigger loading

  @property
  def sheet(self):
    return self._sheet

  @sheet.setter
  def sheet(self, name):
    """
    accepts a sheet name and makes it the currently active one. the name should 
    be a slug and will be transformed to it first if not
    """
    if not isinstance(name, str):
      raise TypeError("select sheets by their name as a string")
    name = slugify(name)
    try:
      self._sheet = self._sheets[name]
      logger.info(f"sheet {name} selected")
    except KeyError:
      raise ValueError(f"unknown sheet: {name}, options: {list(self._sheets.keys())}")

  @property
  def config(self):
    """
    the configuration consists of a mapping of the sheet names to their type.
    """
    return {
      "sheets" : {
        name : sheet.__class__.__name__ for name, sheet in self._sheets.items()
      }
    }

  # storage

  @property
  def folder(self):
    return self._folder

  @folder.setter
  def folder(self, new_folder):
    """
    accepts a string or Path object to this books storage location. if different
    from the current location, the data from new location is loaded
    """
    new_folder = Path().cwd() / Path(new_folder).expanduser()
    if new_folder != self._folder:
      self._folder = new_folder
      self.load()
  
  @property
  def types(self):
    subclasses = {
      cls.__name__ : cls for cls in all_subclasses(SheetLike)
    }
    return subclasses
  
  def load(self):
    """
    loads all config/data from the folder
    """
    # load configuration
    try:
      with (self._folder / "config.yaml").open() as fp:
        config = yaml.safe_load(fp)
    except FileNotFoundError:
      logger.warning(f"{self._folder} doesn't contain config.yaml")
      config = { "sheets" : {} }
    
    # load sheets
    self._sheets = {}
    if "sheets" in config:
      for name, classname in config["sheets"].items():
        try:
          sheetclass = self.types[classname]
          with (self._folder / f"{name}.json").open() as fp:
            self._sheets[name] = sheetclass()
            recordtype = self._sheets[name].type
            self._sheets[name].update(json.load(fp, cls=ClassDecoder(recordtype)))
        except KeyError:
          logger.warning(f"ignoring unknown sheetclass {classname}")
        except FileNotFoundError:
          logger.warning(f"could not find sheet {name}.json")

    # ensure at least empty records and plans sheets are available
    self._sheets = {
      name : self.types[classname]() for name, classname in DEFAULT_SHEETS.items()
    } | self._sheets

    self.sheet = DEFAULT_SHEET # after loading, make the "records" sheet active
    return self
    
  def save(self):
    """
    save all config/data to the folder
    """
    # ensure the folder exists
    self._folder.mkdir(parents=True, exist_ok=True)

    # save configuration
    with (self._folder / "config.yaml").open("w") as fp:
      yaml.safe_dump(self.config, fp, indent=2, default_flow_style=False)

    # save sheets
    for name, sheet in self._sheets.items():
      # save records
      with (self._folder / f"{name}.json").open("w") as fp:
        json.dump(sheet, fp, cls=ClassEncoder, indent=2)

    return self

  # sheet management
  
  # def create(self, name, cls=Record):
  #   if name in self._sheets:
  #     raise ValueError(f"sheet named {name} already exists")
  #   sheet = Sheet(cls=cls)
  #   self._sheets[name] = sheet
  #   return sheet
  #
  # def remove(self, name):
  #   del self._sheets[name]

  # record management

  def add(self, *args, **kwargs):
    """
    add a record or plan using their arguments to the current sheet and save
    """
    record = self.sheet.add(*args, **kwargs)
    self.save()
    logger.info(f"added {record}")
    return record

  def slurp(self, source=sys.stdin):
    """
    reads tab separated rows from source iterable, default is stdin, and
    imports them as records
    """
    for line in source:
      line = line.strip()
      if not line:
        break
      self.add(*line.split("\t"))

  # iterator support, making Book a list of what's on its current sheet

  def __iter__(self):
    return iter(self.sheet)

  def __len__(self):
    return len(self.sheet)

  def __getitem__(self, index):
    return self.sheet[index]

# Sheets

class SheetLike:
  """
  a sheet maintains a sorted collection of <records> of a implemented type prop
  SheetLike is a baseclass with most Sheet functionality implemented, it only
  requires the implementing class to provide a type property, implement __iter__
  and the add() method
  """
  
  @property
  def type(self):
    raise NotImplementedError(f"{self.__class__.__name__} needs to provide a type property")
  
  def __iter__(self):
    raise NotImplementedError(f"{self.__class__.__name__} __iter__ needs to be implemented")

  def __len__(self):
    raise NotImplementedError(f"{self.__class__.__name__} __len__ needs to be implemented")
  
  def add(self, *args, **kwargs):
    raise NotImplementedError(f"{self.__class__.__name__} add() needs to be implemented")

  # list-like behavior based on add()

  def update(self, other):
    """
    merges in record from other sheet
    """
    for record in other:
      self.add(record)

  def __add__(self, other):
    """
    constructs a new sheet with own and other sheet's records
    """
    new = self.__class__(self)
    new.update(other)
    return new

  # list-like behavior based on iterator support

  def __getitem__(self, index):
    return list(self)[index]

  # alternative iterator, with filtering capabilities

  def take(self, count=None, until=None, start=None):
    """
    generator that yields records matching criteria
    """
    if until and not isinstance(until, datetime):
      until = parse_datetime(until)
    if start and not isinstance(start, datetime):
      start = parse_datetime(start)
    yielded = 0
    for record in self:
      if start and record.timestamp < start:
        continue
      if until and record.timestamp > until:
        continue
      yield record
      yielded += 1
      if count and yielded >= count:
        return

  # rows and columns

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

class ImmutableSheetLike(SheetLike):
  def add(self, *args, **kwargs):
    raise TypeError(f"{self.__class__.__name__} is immutable")

  def update(self, other):
    raise TypeError(f"{self.__class__.__name__} is immutable")

  def __add__(self, other):
    raise TypeError(f"{self.__class__.__name__} is immutable")

class Sheet(SheetLike):
  """
  a standard sheet, provides access to a list of records/rows
  """

  def __init__(self, records=None):
    self._records = SortedList()
    if records:
      self.update(records)
    self.balanced = BalancedSheet(self)

  @property
  def type(self):
    return Record

  def add(self, *args, **kwargs):
    """
    add accepts a record of the correct type for this sheet, or a dict with the
    arguments to construct one, or the actual arguments to construct one
    e.g. sheet = Sheet(Record)
         sheet.add(Record(-125, "test"))
         sheet.add({ "amount" : -125, "description": "test" })
         sheet.add(-125, "test")
    """
    if len(args) == 1 and isinstance(args[0], self.type):
      record = args[0]
    elif len(args) == 1 and isinstance(args[0], dict):
      record = self.type(**args[0])
    else:
      record = self.type(*args, **kwargs)
    self._records.add(record)
    return record

  def __iter__(self):
    return iter(self._records)

  def __len__(self):
    return len(self._records)

  def __getitem__(self, index):
    # optimization over the generic version on SheetLike
    return self._records[index]

class PlannedSheet(Sheet):
  """
  a PlanedSheet holds PlannedRecords and behaves as a Sheet, except for the take
  method that unrolls the PlannedRecords into Records
  """

  @property
  def type(self):
    return PlannedRecord

  def take(self, count=None, until=None, start=None):
    """
    generator that yields records matching criteria, after generating plans
    """
    # first create a virtual sheet from all plans, ensuring cross-sheet ordering
    records = Sheet()
    for plan in self:
      records.update(plan.take(count=count, until=until, start=start))
    # and now take from that
    return records.take(count=count, until=until, start=start)

@dataclass
class SheetExtract(ImmutableSheetLike):
  sheet : SheetLike
  # optional parameters to take
  count : int      = None
  until : datetime = None
  start : datetime = None

  def __post_init__(self):
    """
    we accept strings or datetimes, parsing them if needed
    """
    if self.until is not None and not isinstance(self.until, datetime):
      self.until = parse_datetime(self.until)
    if self.start is not None and not isinstance(self.start, datetime):
      self.start = parse_datetime(self.start)
  
  @property
  def type(self):
    return self.sheet.type
  
  def __iter__(self):
    return self.take(count=self.count, until=self.until, start=self.start)

  def __len__(self):
    # ugly ;-)
    records = list(self.take(count=self.count, until=self.until, start=self.start))
    return len(records)

  def take(self, count=None, until=None, start=None):
    return self.sheet.take(count=count, until=until, start=start)

class CombinedSheet(ImmutableSheetLike):
  """
  a SheetLike, combining extractions from other sheets.
  """
  def __init__(self, extracts):
    """
    a combined sheet 
    """
    self._extracts = extracts

  @property
  def type(self):
    return Record

  def __iter__(self):
    """
    creates a combination of all extracts and provides them as an iterable
    """
    combined = Sheet()
    for sheet in self._extracts:
      combined.update(sheet)
    return iter(combined)

  def __len__(self):
    return sum( [ len(sheet) for sheet in self._extracts ] )

class BalancedSheet(SheetLike):
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
