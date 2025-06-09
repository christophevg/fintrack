import sys

from pathlib import Path

import yaml
import json

import logging

from fintrack import __version__
from fintrack.records import Record, Records, RecordEncoder, RecordDecoder

logger = logging.getLogger(__name__)

class Tracker:
  def __init__(self, folder="~/.fintrack"):
    self.records = Records()
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
      json.dump(self.records, fp, cls=RecordEncoder, indent=2)

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
        self.records = Records(json.load(fp, cls=RecordDecoder))
    except FileNotFoundError:
      pass

  def add(self, record):
    """
    add a record + save
    """
    self.records.append(record)
    self.save()

  def record(self, *args, **kwargs):
    """
    utility function to create a record from arguments and add it
    """
    self.add(Record(*args, **kwargs))

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
    for record in self.records:
      yield record

  def __len__(self):
    return len(self.records)
  
  def __getitem__(self, index):
    return self.records[index]

  
