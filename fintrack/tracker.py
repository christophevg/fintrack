import sys

from pathlib import Path

import yaml
import json

import logging

from fintrack            import __version__
from fintrack.records    import Record, balanced
from fintrack.plans      import PlannedRecord
from fintrack.util       import Ordered, ClassEncoder, ClassDecoder
from fintrack.ui.tabular import Tabular

logger = logging.getLogger(__name__)

class Tracker:
  def __init__(self, folder="~/.fintrack"):
    self._sheets   = {}
    self._sheet    = None   # currently active sheet
    self._balanced = False
    self.types = {
      "records" : Record,
      "plans"   : PlannedRecord
    }
    # use folder, which also triggers loading
    self.use(folder)
    
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
    self._sheet = Ordered(Record)
    for plan in self._sheets["plans"]:
      self._sheet = self._sheet + Ordered(Record, plan.take(until=until))
    return self

  @property
  def overview(self):
    """
    overview is a ready-made composite sheet of records and the future
    TODO: generalize
    """
    self._sheet = self._sheets["records"]
    for plan in self._sheets["plans"]:
      self._sheet = self._sheet + Ordered(Record, plan.take(until="next month"))
    return self

  def balanced(self):
    """
    activate addition of balance
    TODO: toggle it?
    """
    self._balanced = True
    return self

  @property
  def table(self):
    """
    visualize the current sheet as a table
    """
    return Tabular(self.current_sheet, balanced=balanced if self._balanced else None)

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
            self._sheets[name] = Ordered(type, json.load(fp, cls=ClassDecoder(type)))
        except FileNotFoundError:
          logger.warning(f"could not find sheet {name}.json")

    # ensure at least empty records and plans sheets are available
    self._sheets = {
      name : Ordered(type) for name, type in self.types.items()
    } | self._sheets

    self.sheet("records")
    return self

  # record management

  def append(self, record_or_plan):
    """
    add a record or plan to the current sheet and save
    """
    self.current_sheet.append(record_or_plan)
    self.save()

  def add(self, *args, **kwargs):
    """
    utility function to create a (planned)record from arguments and add it
    """
    record = self.current_sheet.type(*args, **kwargs)
    self.append(record)
    logger.info(f"added {record}")

  def slurp(self, typename, source=sys.stdin):
    """
    reads tab separated rows from stdin and imports them as records
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
