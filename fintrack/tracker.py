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
    self._records  = Ordered(Record)
    self._plans    = Ordered(PlannedRecord)
    self._scope    = None
    self._balanced = False
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
    return {
      "version" : __version__
    }

  @property
  def records(self):
    self._scope = self._records
    return self

  @property
  def plans(self):
    self._scope = self._plans
    return self

  def future(self, until="next month"):
    self._scope = Ordered(Record)
    for plan in self._plans:
      self._scope = self._scope + Ordered(Record, plan.take(until=until))
    return self

  @property
  def overview(self):
    self._scope = self._records
    for plan in self._plans:
      self._scope = self._scope + Ordered(Record, plan.take(until="next month"))
    return self

  def balanced(self):
    self._balanced = True
    return self

  @property
  def table(self):
    return Tabular(self._scope, balanced=balanced if self._balanced else None)

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

    # save records
    with (self._folder / "records.json").open("w") as fp:
      json.dump(self._records, fp, cls=ClassEncoder, indent=2)

    # save plans
    with (self._folder / "plans.json").open("w") as fp:
      json.dump(self._plans, fp, cls=ClassEncoder, indent=2)

    return self

  def load(self):
    """
    loads all config/data from the folder
    """
    # load configuration
    try:
      with (self._folder / "config.yaml").open() as fp:
        _ = yaml.safe_load(fp) # do nothing with it for now
    except FileNotFoundError:
      pass
    
    # load records
    try:
      with (self._folder / "records.json").open() as fp:
        self._records = Ordered(Record, json.load(fp, cls=ClassDecoder(Record)))
    except FileNotFoundError:
      pass

    # load plans
    try:
      with (self._folder / "plans.json").open() as fp:
        self._plans = Ordered(PlannedRecord, json.load(fp, cls=ClassDecoder(PlannedRecord)))
    except FileNotFoundError:
      pass

  def add(self, record_or_plan):
    """
    add a record or plan + save
    """
    self._scope.append(record_or_plan)
    self.save()

  def record(self, *args, **kwargs):
    """
    utility function to create a record from arguments and add it
    """
    self.records.add(Record(*args, **kwargs))

  def plan(self, *args, **kwargs):
    """
    utility function to create a plan from arguments and add it
    """
    self.plans.add(PlannedRecord(*args, **kwargs))

  def slurp(self, source=sys.stdin):
    """
    reads tab separated rows from stdin and imports them as records
    """
    for line in source:
      line = line.strip()
      if not line:
        break
      self.record(*line.split("\t"))

  def __iter__(self):
    for record_or_plan in self._scope:
      yield record_or_plan

  def __len__(self):
    return len(self._scope)
  
  def __getitem__(self, index):
    return self._scope[index]
