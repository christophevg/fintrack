import sys

from pathlib import Path

import yaml
import json

import logging

from fintrack            import __version__
from fintrack.books      import Sheet
from fintrack.records    import Record
from fintrack.plans      import PlannedRecord
from fintrack.utils      import ClassEncoder, ClassDecoder
from fintrack.ui.tabular import Tabular, positive_green, negative_red

logger = logging.getLogger(__name__)

class Tracker:
  def __init__(self, folder="~/.fintrack"):
    self._sheets   = {}
    self._sheet    = None   # currently active sheet
    self.types = {
      "records" : Record,
      "plans"   : PlannedRecord
    }
    # use folder, which also triggers loading
    self.use(folder)
    
  @property
  def version(self):
    """
    provide the version
    """
    return __version__

  @property
  def using(self):
    """
    provide the current folder containing the FinTrack data files
    """
    return self._folder

  @property
  def config(self):
    """
    the configuration consists of the version and a dictionary of sheets mapping
    their name to their (content) type, Record or PlannedRecord
    """
    return {
      "version": __version__,
      "sheets" : {
        name : {
          type : name for name, type in self.types.items()
        }[collection.type] for name, collection in self._sheets.items()
      }
    }

  @property
  def current_sheet(self):
    if self._sheet is None:
      logger.error("no sheet selected, use 'sheet <name>' to select one")
      sys.exit(1)
    return self._sheet
  
  def sheet(self, name):
    """
    sets the active sheet
    """
    self._sheet = self._sheets[name]
    logger.info(f"activated sheet '{name}'")
    return self

  def future(self, until="next month"):
    """
    future generates records from the planned records
    TODO: generalize
    """
    self._sheet = Sheet()
    for plan in self._sheets["plans"]:
      self._sheet = self._sheet + Sheet(plan.take(until=until))
    return self

  @property
  def overview(self):
    """
    overview is a ready-made composite sheet of records and the future
    TODO: generalize
    """
    self._sheet = self._sheets["records"]
    for plan in self._sheets["plans"]:
      self._sheet = self._sheet + Sheet(plan.take(until="next month"))
    return self

  @property
  def balanced(self):
    """
    makes the balanced version of the current sheet active
    """
    self._sheet = self.current_sheet.balanced
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
    """
    change the folder containing the FinTrack data files
    """
    self._folder = Path().cwd() / Path(folder).expanduser()
    logger.debug(f"using {self._folder}")
    self.load()
    return self

  def save(self):
    """
    save all config/data to the folder
    """
    # ensire folder exists
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
          type = self.types[typename]
          with (self._folder / f"{name}.json").open() as fp:
            self._sheets[name] = Sheet(json.load(fp, cls=ClassDecoder(type)), cls=type)
        except FileNotFoundError:
          logger.warning(f"could not find sheet {name}.json")

    # ensure at least empty records and plans sheets are available
    self._sheets = {
      name : Sheet(cls=type) for name, type in self.types.items()
    } | self._sheets

    self.sheet("records")
    return self

  # record management

  def add(self, *args, **kwargs):
    """
    add a record or plan using their arguments to the current sheet and save
    """
    record = self.current_sheet.add(*args, **kwargs)
    self.save()
    logger.info(f"added {record}")

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

  # iterator support, making Tracker a list of what's on its current sheet

  def __iter__(self):
    for record_or_plan in self.current_sheet:
      yield record_or_plan

  def __len__(self):
    return len(self.current_sheet)
  
  def __getitem__(self, index):
    return self.current_sheet[index]
