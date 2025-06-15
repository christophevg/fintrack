import sys

from pathlib import Path

import yaml
import json

from datetime import datetime

from sortedcontainers import SortedList

from slugify import slugify

from fintrack.records import RecordLike, Record
from fintrack.plans   import PlannedRecord
from fintrack.utils   import asrow, ClassEncoder, ClassDecoder, parse_datetime

import logging
logger = logging.getLogger(__name__)

DEFAULT_SHEETS = {
  "records" : Record,
  "plans"   : PlannedRecord
}
DEFAULT_SHEET = "records" 
TYPE_NAMES = {
  Record        : "records",
  PlannedRecord : "plans"
}

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
      "sheets" : { name : TYPE_NAMES[sheet.type] for name, sheet in self._sheets.items() }
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
      for name, typename in config["sheets"].items():
        try:
          type = DEFAULT_SHEETS[typename]
          with (self._folder / f"{name}.json").open() as fp:
            self._sheets[name] = Sheet(json.load(fp, cls=ClassDecoder(type)), cls=type)
        except FileNotFoundError:
          logger.warning(f"could not find sheet {name}.json")

    # ensure at least empty records and plans sheets are available
    self._sheets = {
      name : Sheet(cls=type) for name, type in DEFAULT_SHEETS.items()
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

class CombinedSheet:
  """
  behaves as a Sheet, combining Records from other sheets.
  """
  def init(self, combinations):
    """
    a combination is defined by a sheet and filtering parameters
    """
    self._combinations = combinations
  

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

  def take(self, count=None, until=None, start=None):
    """
    generator that yields records matching criteria
    """
    if until and not isinstance(until, datetime):
      until = parse_datetime(until)
    if start and not isinstance(start, datetime):
      start = parse_datetime(start)
    yielded = 0
    for record in self._records:
      if start and record.timestamp < start:
        continue
      if until and record.timestamp > until:
        continue
      yield record
      yielded += 1
      if count and yielded >= count:
        return

  def __iter__(self):
    for record in self._records:
      yield record

  def __len__(self):
    return len(self._records)

  def __getitem__(self, index):
    return self._records[index]
